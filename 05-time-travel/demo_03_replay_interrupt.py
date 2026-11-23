"""场景 3：回到 interrupt 之前，用新的人工输入创建分支。"""

from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt


class ChoiceState(TypedDict, total=False):
    question: str
    answer: str
    result: str


def ask_user(state: ChoiceState) -> dict[str, str]:
    answer = interrupt({"question": state["question"]})
    return {"answer": answer}


def format_result(state: ChoiceState) -> dict[str, str]:
    return {"result": f"你选择了：{state['answer']}"}


def build_graph():
    builder = StateGraph(ChoiceState)
    builder.add_node("ask_user", ask_user)
    builder.add_node("format_result", format_result)
    builder.add_edge(START, "ask_user")
    builder.add_edge("ask_user", "format_result")
    builder.add_edge("format_result", END)
    return builder.compile(checkpointer=InMemorySaver())


def main() -> None:
    graph = build_graph()
    thread_config = {"configurable": {"thread_id": "interrupt-replay-001"}}

    paused = graph.invoke(
        {"question": "请选择咖啡或茶"},
        config=thread_config,
    )
    print("第一次暂停：", paused["__interrupt__"][0].value)

    original = graph.invoke(Command(resume="咖啡"), config=thread_config)
    print("原始分支：", original["result"])

    history = list(graph.get_state_history(thread_config))
    before_ask_user = next(
        snapshot for snapshot in history if snapshot.next == ("ask_user",)
    )

    replayed_pause = graph.invoke(None, config=before_ask_user.config)
    print("回到历史后再次暂停：", replayed_pause["__interrupt__"][0].value)

    # 不传 checkpoint_id，只保留 thread_id，恢复刚刚创建的最新分支。
    forked = graph.invoke(Command(resume="茶"), config=thread_config)
    print("新分支：", forked["result"])

    assert original["result"] == "你选择了：咖啡"
    assert forked["result"] == "你选择了：茶"


if __name__ == "__main__":
    main()
