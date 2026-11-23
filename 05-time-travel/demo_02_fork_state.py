"""场景 2：修改历史 checkpoint 的状态并创建一条新分支。"""

from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph


class JokeState(TypedDict, total=False):
    requested_topic: str
    topic: str
    joke: str


def generate_topic(state: JokeState) -> dict[str, str]:
    return {"topic": state["requested_topic"]}


def write_joke(state: JokeState) -> dict[str, str]:
    jokes = {
        "袜子": "袜子为什么成双成对？因为它们不想单独面对洗衣机。",
        "鸡": "鸡为什么过马路？因为它想看看另一边的 checkpoint。",
    }
    return {"joke": jokes[state["topic"]]}


def build_graph():
    builder = StateGraph(JokeState)
    builder.add_node("generate_topic", generate_topic)
    builder.add_node("write_joke", write_joke)
    builder.add_edge(START, "generate_topic")
    builder.add_edge("generate_topic", "write_joke")
    builder.add_edge("write_joke", END)
    return builder.compile(checkpointer=InMemorySaver())


def main() -> None:
    graph = build_graph()
    config = {"configurable": {"thread_id": "fork-001"}}

    original = graph.invoke({"requested_topic": "袜子"}, config=config)
    print("原始分支：", original)

    history = list(graph.get_state_history(config))
    before_write_joke = next(
        snapshot for snapshot in history if snapshot.next == ("write_joke",)
    )

    fork_config = graph.update_state(
        before_write_joke.config,
        {"topic": "鸡"},
        as_node="generate_topic",
    )
    forked = graph.invoke(None, config=fork_config)
    print("新分支：", forked)

    assert original["topic"] == "袜子"
    assert forked["topic"] == "鸡"
    assert original["joke"] != forked["joke"]


if __name__ == "__main__":
    main()
