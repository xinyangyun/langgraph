"""场景 1：从历史 checkpoint 重放后续节点。"""

from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph


class JokeState(TypedDict, total=False):
    topic: str
    joke: str


def build_graph(call_counts: dict[str, int]):
    def generate_topic(_: JokeState) -> dict[str, str]:
        call_counts["generate_topic"] += 1
        print("执行 generate_topic")
        return {"topic": "程序员"}

    def write_joke(state: JokeState) -> dict[str, str]:
        call_counts["write_joke"] += 1
        print("执行 write_joke")
        return {"joke": f"关于{state['topic']}的第 {call_counts['write_joke']} 个笑话"}

    builder = StateGraph(JokeState)
    builder.add_node("generate_topic", generate_topic)
    builder.add_node("write_joke", write_joke)
    builder.add_edge(START, "generate_topic")
    builder.add_edge("generate_topic", "write_joke")
    builder.add_edge("write_joke", END)
    return builder.compile(checkpointer=InMemorySaver())


def main() -> None:
    call_counts = {"generate_topic": 0, "write_joke": 0}
    graph = build_graph(call_counts)
    config = {"configurable": {"thread_id": "replay-001"}}

    original = graph.invoke({}, config=config)
    print("首次结果：", original)

    history = list(graph.get_state_history(config))
    before_write_joke = next(
        snapshot for snapshot in history if snapshot.next == ("write_joke",)
    )
    print("选择的 checkpoint：", before_write_joke.config["configurable"])

    replayed = graph.invoke(None, config=before_write_joke.config)
    print("重放结果：", replayed)
    print("节点执行次数：", call_counts)

    # generate_topic 已经包含在 checkpoint 中，因此只重新执行 write_joke。
    assert call_counts == {"generate_topic": 1, "write_joke": 2}
    assert original["joke"] != replayed["joke"]


if __name__ == "__main__":
    main()
