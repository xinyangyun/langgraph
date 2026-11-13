"""场景 1：使用 checkpointer 保存同一 thread 的多轮会话状态。"""

from operator import add
from typing import Annotated, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

from diagram_utils import save_graph_image


class ConversationState(TypedDict):
    messages: Annotated[list[str], add]


def reply(state: ConversationState) -> dict[str, list[str]]:
    """根据 checkpointer 恢复出的完整历史生成一个确定性回复。"""
    user_messages = [message for message in state["messages"] if message.startswith("用户：")]
    latest = user_messages[-1].removeprefix("用户：")
    if len(user_messages) == 1:
        answer = f"助手：收到，你说的是“{latest}”。"
    else:
        first = user_messages[0].removeprefix("用户：")
        answer = f"助手：我还记得你最开始说的是“{first}”。"
    return {"messages": [answer]}


def build_graph():
    builder = StateGraph(ConversationState)
    builder.add_node("reply", reply)
    builder.add_edge(START, "reply")
    builder.add_edge("reply", END)
    return builder.compile(checkpointer=InMemorySaver())


def main() -> None:
    graph = build_graph()
    config = {"configurable": {"thread_id": "conversation-001"}}

    first = graph.invoke({"messages": ["用户：我叫小明"]}, config=config)
    print("第一轮：", first["messages"])

    second = graph.invoke({"messages": ["用户：我最开始说了什么？"]}, config=config)
    print("第二轮：", second["messages"])

    snapshot = graph.get_state(config)
    print("checkpoint 中的消息数：", len(snapshot.values["messages"]))

    assert len(second["messages"]) == 4
    assert "我叫小明" in second["messages"][-1]
    save_graph_image(graph, "demo_01_conversation_memory.png")


if __name__ == "__main__":
    main()
