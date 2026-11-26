"""场景 1：父图和子图状态结构不同，通过包装节点转换输入输出。"""

from functools import partial
from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class ResearchState(TypedDict):
    subject: str
    notes: str
    summary: str


class ParentState(TypedDict):
    question: str
    answer: str


def collect_notes(state: ResearchState) -> dict[str, str]:
    return {"notes": f"{state['subject']}是一种常见的研究主题。"}


def summarize(state: ResearchState) -> dict[str, str]:
    return {"summary": f"研究摘要：{state['subject']}；资料：{state['notes']}"}


def build_research_subgraph():
    builder = StateGraph(ResearchState)
    builder.add_node("collect_notes", collect_notes)
    builder.add_node("summarize", summarize)
    builder.add_edge(START, "collect_notes")
    builder.add_edge("collect_notes", "summarize")
    builder.add_edge("summarize", END)
    return builder.compile(name="research_subgraph")


def call_research_subgraph(
    state: ParentState,
    *,
    research_graph,
) -> dict[str, str]:
    child_input = {
        "subject": state["question"],
        "notes": "",
        "summary": "",
    }
    print("父图 -> 子图，映射输入：", child_input)
    result = research_graph.invoke(child_input)
    mapped_output = {"answer": result["summary"]}
    print("子图 -> 父图，映射输出：", mapped_output)
    return mapped_output


def build_parent_graph():
    research_graph = build_research_subgraph()

    builder = StateGraph(ParentState)
    builder.add_node(
        "call_research_subgraph",
        partial(call_research_subgraph, research_graph=research_graph),
    )
    builder.add_edge(START, "call_research_subgraph")
    builder.add_edge("call_research_subgraph", END)
    return builder.compile(name="parent_graph"), research_graph


def main() -> None:
    parent_graph, research_graph = build_parent_graph()
    print("父图拓扑：")
    print(parent_graph.get_graph().draw_mermaid())
    print("子图拓扑：")
    print(research_graph.get_graph().draw_mermaid())

    result = parent_graph.invoke({"question": "LangGraph 子图"})
    print("父图输入：", "LangGraph 子图")
    print("父图输出：", result["answer"])
    assert "LangGraph 子图" in result["answer"]
    assert "answer" in result
    assert "notes" not in result


if __name__ == "__main__":
    main()
