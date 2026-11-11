"""场景 3：读取历史 checkpoint，并从中间状态创建一条新分支。"""

from operator import add
from typing import Annotated, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

from diagram_utils import save_graph_image


class NumberState(TypedDict):
    number: int
    history: Annotated[list[str], add]


def add_one(state: NumberState) -> dict:
    result = state["number"] + 1
    return {"number": result, "history": [f"加 1 -> {result}"]}


def double(state: NumberState) -> dict:
    result = state["number"] * 2
    return {"number": result, "history": [f"乘 2 -> {result}"]}


def build_graph():
    builder = StateGraph(NumberState)
    builder.add_node("add_one", add_one)
    builder.add_node("double", double)
    builder.add_edge(START, "add_one")
    builder.add_edge("add_one", "double")
    builder.add_edge("double", END)
    return builder.compile(checkpointer=InMemorySaver())


def main() -> None:
    graph = build_graph()
    config = {"configurable": {"thread_id": "calculation-001"}}

    original = graph.invoke({"number": 3, "history": []}, config=config)
    print("原始执行：", original)

    snapshots = list(graph.get_state_history(config))
    print("checkpoint 数量：", len(snapshots))
    for snapshot in reversed(snapshots):
        print("  number=", snapshot.values.get("number"), "next=", snapshot.next)

    before_double = next(snapshot for snapshot in snapshots if snapshot.next == ("double",))
    fork_config = graph.update_state(
        before_double.config,
        {"number": 10, "history": ["人工改为 10"]},
    )
    branched = graph.invoke(None, config=fork_config)
    print("分支执行：", branched)

    assert original["number"] == 8
    assert branched["number"] == 20
    save_graph_image(graph, "demo_03_time_travel.png")


if __name__ == "__main__":
    main()
