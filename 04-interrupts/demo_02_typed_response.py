"""场景 2：使用 response_schema 校验 interrupt 的恢复值。"""

from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt
from pydantic import BaseModel, ValidationError


class Decision(BaseModel):
    approved: bool
    note: str | None = None


class DecisionState(TypedDict, total=False):
    decision: Decision


def review(_: DecisionState) -> dict[str, Decision]:
    decision = interrupt(
        {"question": "是否批准发布？"},
        response_schema=Decision,
    )
    return {"decision": decision}


def build_graph():
    builder = StateGraph(DecisionState)
    builder.add_node("review", review)
    builder.add_edge(START, "review")
    builder.add_edge("review", END)
    return builder.compile(checkpointer=InMemorySaver())


def main() -> None:
    graph = build_graph()
    config = {"configurable": {"thread_id": "typed-response-001"}}

    paused = graph.invoke({}, config=config)
    interrupt_info = paused["__interrupt__"][0]
    print("响应 JSON Schema：", interrupt_info.response_schema)

    try:
        graph.invoke(Command(resume={"note": "缺少 approved"}), config=config)
    except ValidationError as error:
        print("无效恢复值被拒绝：", error.errors()[0]["msg"])

    resumed = graph.invoke(
        Command(resume={"approved": True, "note": "检查通过"}),
        config=config,
    )
    print("类型化审批结果：", resumed["decision"])

    assert isinstance(resumed["decision"], Decision)
    assert resumed["decision"].approved is True


if __name__ == "__main__":
    main()
