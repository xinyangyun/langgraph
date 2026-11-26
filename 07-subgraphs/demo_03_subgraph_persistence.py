"""场景 3：比较子图默认 per-invocation 与 per-thread 持久化。"""

from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph


class ParentState(TypedDict):
    question: str
    answer: str


class SpecialistState(TypedDict, total=False):
    question: str
    answer: str
    turn_count: int  # 子图私有状态，不会暴露到父图


def specialist(state: SpecialistState) -> dict[str, object]:
    turn_count = state.get("turn_count", 0) + 1
    print(f"子图内部 turn_count={turn_count}")
    return {
        "turn_count": turn_count,
        "answer": f"子图已处理 {turn_count} 次；当前问题：{state['question']}",
    }


def build_specialist_subgraph(*, persistent_per_thread: bool):
    builder = StateGraph(SpecialistState)
    builder.add_node("specialist", specialist)
    builder.add_edge(START, "specialist")
    builder.add_edge("specialist", END)
    return builder.compile(checkpointer=True if persistent_per_thread else None)


def build_parent_graph(*, persistent_per_thread: bool):
    subgraph = build_specialist_subgraph(
        persistent_per_thread=persistent_per_thread
    )
    builder = StateGraph(ParentState)
    # 直接注册子图，LangGraph 才能为其发现稳定的 checkpoint namespace。
    builder.add_node("specialist", subgraph)
    builder.add_edge(START, "specialist")
    builder.add_edge("specialist", END)
    return builder.compile(checkpointer=InMemorySaver())


def run_twice(graph, thread_id: str) -> list[str]:
    config = {"configurable": {"thread_id": thread_id}}
    answers = []
    for question in ["第一轮问题", "第二轮问题"]:
        result = graph.invoke({"question": question}, config=config)
        answers.append(result["answer"])
        print(f"{thread_id} / {question}: {result['answer']}")
    return answers


def main() -> None:
    per_invocation = build_parent_graph(persistent_per_thread=False)
    invocation_answers = run_twice(per_invocation, "subgraph-invocation-001")

    per_thread = build_parent_graph(persistent_per_thread=True)
    thread_answers = run_twice(per_thread, "subgraph-thread-001")

    assert all("处理 1 次" in answer for answer in invocation_answers)
    assert "处理 1 次" in thread_answers[0]
    assert "处理 2 次" in thread_answers[1]


if __name__ == "__main__":
    main()
