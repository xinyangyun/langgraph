"""场景 4：通过 interrupt ID 一次恢复多个并行暂停点。"""

from operator import add
from typing import Annotated, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt


class ParallelState(TypedDict):
    results: Annotated[list[str], add]


def branch_a(_: ParallelState) -> dict[str, list[str]]:
    answer = interrupt("请输入分支 A 的值：")
    return {"results": [f"A={answer}"]}


def branch_b(_: ParallelState) -> dict[str, list[str]]:
    answer = interrupt("请输入分支 B 的值：")
    return {"results": [f"B={answer}"]}


def build_graph():
    builder = StateGraph(ParallelState)
    builder.add_node("branch_a", branch_a)
    builder.add_node("branch_b", branch_b)
    builder.add_edge(START, "branch_a")
    builder.add_edge(START, "branch_b")
    builder.add_edge("branch_a", END)
    builder.add_edge("branch_b", END)
    return builder.compile(checkpointer=InMemorySaver())


def main() -> None:
    graph = build_graph()
    config = {"configurable": {"thread_id": "parallel-interrupts-001"}}

    paused = graph.invoke({"results": []}, config=config)
    pending = paused["__interrupt__"]
    print("待恢复的 interrupt：")
    for item in pending:
        print(f"  id={item.id}, value={item.value}")

    resume_map = {
        item.id: "苹果" if "A" in item.value else "香蕉"
        for item in pending
    }
    completed = graph.invoke(Command(resume=resume_map), config=config)
    print("并行恢复结果：", completed["results"])

    assert sorted(completed["results"]) == ["A=苹果", "B=香蕉"]


if __name__ == "__main__":
    main()
