"""场景 2：使用 Store 保存跨 thread、按用户隔离的长期记忆。"""

from dataclasses import dataclass
from typing import Literal, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.runtime import Runtime
from langgraph.store.memory import InMemoryStore


class MemoryState(TypedDict, total=False):
    action: Literal["remember", "recall"]
    memory: str
    result: str


@dataclass
class Context:
    user_id: str


def manage_memory(state: MemoryState, runtime: Runtime[Context]) -> dict[str, str]:
    if runtime.store is None:
        raise RuntimeError("图没有配置 Store")

    namespace = ("users", runtime.context.user_id, "memories")
    if state["action"] == "remember":
        runtime.store.put(namespace, "profile", {"text": state["memory"]})
        return {"result": f"已写入长期记忆：{state['memory']}"}

    stored = runtime.store.get(namespace, "profile")
    if stored is None:
        return {"result": "没有找到长期记忆"}
    return {"result": f"读取到长期记忆：{stored.value['text']}"}


def build_graph(store: InMemoryStore):
    builder = StateGraph(MemoryState, context_schema=Context)
    builder.add_node("manage_memory", manage_memory)
    builder.add_edge(START, "manage_memory")
    builder.add_edge("manage_memory", END)
    return builder.compile(
        checkpointer=InMemorySaver(),
        store=store,
    )


def main() -> None:
    graph = build_graph(InMemoryStore())
    alice = Context(user_id="alice")

    remembered = graph.invoke(
        {"action": "remember", "memory": "我喜欢使用 PyCharm"},
        config={"configurable": {"thread_id": "alice-thread-001"}},
        context=alice,
    )
    print("线程 1：", remembered["result"])

    recalled = graph.invoke(
        {"action": "recall"},
        config={"configurable": {"thread_id": "alice-thread-002"}},
        context=alice,
    )
    print("线程 2：", recalled["result"])

    bob = graph.invoke(
        {"action": "recall"},
        config={"configurable": {"thread_id": "bob-thread-001"}},
        context=Context(user_id="bob"),
    )
    print("另一个用户：", bob["result"])

    assert "PyCharm" in recalled["result"]
    assert bob["result"] == "没有找到长期记忆"


if __name__ == "__main__":
    main()
