"""场景 2：在 LangGraph 节点中跨 thread 共享长期记忆。"""

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
        raise RuntimeError("图没有配置 store")

    namespace = ("users", runtime.context.user_id, "memories")
    if state["action"] == "remember":
        runtime.store.put(namespace, "profile", {"text": state["memory"]})
        return {"result": f"已记住：{state['memory']}"}

    memories = runtime.store.search(namespace)
    if not memories:
        return {"result": "没有找到长期记忆"}

    recalled = "；".join(item.value["text"] for item in memories)
    return {"result": f"长期记忆：{recalled}"}


def build_graph(store: InMemoryStore):
    builder = StateGraph(MemoryState, context_schema=Context)
    builder.add_node("manage_memory", manage_memory)
    builder.add_edge(START, "manage_memory")
    builder.add_edge("manage_memory", END)
    return builder.compile(checkpointer=InMemorySaver(), store=store)


def main() -> None:
    store = InMemoryStore()
    graph = build_graph(store)
    context = Context(user_id="alice")

    remembered = graph.invoke(
        {"action": "remember", "memory": "我喜欢使用 PyCharm 编写 Python"},
        config={"configurable": {"thread_id": "thread-001"}},
        context=context,
    )
    print("线程 1：", remembered["result"])

    recalled = graph.invoke(
        {"action": "recall"},
        config={"configurable": {"thread_id": "thread-002"}},
        context=context,
    )
    print("线程 2：", recalled["result"])

    bob_result = graph.invoke(
        {"action": "recall"},
        config={"configurable": {"thread_id": "thread-003"}},
        context=Context(user_id="bob"),
    )
    print("另一个用户：", bob_result["result"])

    assert "PyCharm" in recalled["result"]
    assert bob_result["result"] == "没有找到长期记忆"


if __name__ == "__main__":
    main()
