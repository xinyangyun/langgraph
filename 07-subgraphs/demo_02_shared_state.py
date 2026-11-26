"""场景 2：父图与子图共享状态键，直接把已编译子图作为节点。"""

from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class ParentState(TypedDict):
    topic: str
    result: str


class SubgraphState(TypedDict, total=False):
    topic: str  # 与父图共享
    result: str  # 与父图共享
    internal_note: str  # 子图私有状态


def inspect_topic(state: SubgraphState) -> dict[str, str]:
    return {"internal_note": f"已检查主题：{state['topic']}"}


def compose_result(state: SubgraphState) -> dict[str, str]:
    return {"result": f"{state['internal_note']}；建议继续深入研究。"}


def build_subgraph():
    builder = StateGraph(SubgraphState)
    builder.add_node("inspect_topic", inspect_topic)
    builder.add_node("compose_result", compose_result)
    builder.add_edge(START, "inspect_topic")
    builder.add_edge("inspect_topic", "compose_result")
    builder.add_edge("compose_result", END)
    return builder.compile()


def build_parent_graph():
    builder = StateGraph(ParentState)
    builder.add_node("analysis_subgraph", build_subgraph())
    builder.add_edge(START, "analysis_subgraph")
    builder.add_edge("analysis_subgraph", END)
    return builder.compile()


def main() -> None:
    result = build_parent_graph().invoke(
        {"topic": "LangGraph 的子图"}
    )
    print("共享状态结果：", result)
    assert result["result"] == "已检查主题：LangGraph 的子图；建议继续深入研究。"
    assert "internal_note" not in result


if __name__ == "__main__":
    main()
