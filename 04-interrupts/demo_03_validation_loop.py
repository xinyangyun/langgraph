"""场景 3：无效输入通过条件边回到 interrupt 节点重新询问。"""

from typing import Literal, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt


class AgeState(TypedDict, total=False):
    age: int | str
    attempts: int
    message: str


def ask_age(state: AgeState) -> dict:
    question = (
        "请输入年龄："
        if state.get("attempts", 0) == 0
        else "输入无效，请输入 1 到 120 之间的整数："
    )
    return {
        "age": interrupt(question),
        "attempts": state.get("attempts", 0) + 1,
    }


def validate_age(state: AgeState) -> dict[str, int | str]:
    try:
        age = int(state["age"])
        if 1 <= age <= 120:
            return {"age": age, "message": "年龄有效"}
    except (TypeError, ValueError):
        pass
    return {"message": "年龄无效"}


def route_after_validation(state: AgeState) -> Literal["ask_age", "__end__"]:
    return "__end__" if state["message"] == "年龄有效" else "ask_age"


def build_graph():
    builder = StateGraph(AgeState)
    builder.add_node("ask_age", ask_age)
    builder.add_node("validate_age", validate_age)
    builder.add_edge(START, "ask_age")
    builder.add_edge("ask_age", "validate_age")
    builder.add_conditional_edges("validate_age", route_after_validation)
    return builder.compile(checkpointer=InMemorySaver())


def main() -> None:
    graph = build_graph()
    config = {"configurable": {"thread_id": "validation-loop-001"}}

    first_pause = graph.invoke({"attempts": 0}, config=config)
    print("第一次询问：", first_pause["__interrupt__"][0].value)

    second_pause = graph.invoke(Command(resume="不是数字"), config=config)
    print("校验失败后重新询问：", second_pause["__interrupt__"][0].value)

    completed = graph.invoke(Command(resume="30"), config=config)
    print("最终结果：", completed)

    assert completed["age"] == 30
    assert completed["attempts"] == 2
    assert completed["message"] == "年龄有效"


if __name__ == "__main__":
    main()
