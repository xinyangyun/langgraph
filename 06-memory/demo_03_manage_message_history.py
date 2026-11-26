"""场景 3：删除旧消息，限制 checkpoint 中的短期记忆长度。"""

from langchain_core.messages import AIMessage, HumanMessage, RemoveMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph


def respond(state: MessagesState) -> dict:
    latest = state["messages"][-1]
    return {"messages": [AIMessage(content=f"已处理：{latest.content}")]}


def delete_old_messages(state: MessagesState) -> dict:
    messages = state["messages"]
    if len(messages) <= 4:
        return {}

    old_messages = messages[:-4]
    print("删除旧消息：", [message.content for message in old_messages])
    return {
        "messages": [RemoveMessage(id=message.id) for message in old_messages],
    }


def build_graph():
    builder = StateGraph(MessagesState)
    builder.add_node("respond", respond)
    builder.add_node("delete_old_messages", delete_old_messages)
    builder.add_edge(START, "respond")
    builder.add_edge("respond", "delete_old_messages")
    builder.add_edge("delete_old_messages", END)
    return builder.compile(checkpointer=InMemorySaver())


def main() -> None:
    graph = build_graph()
    config = {"configurable": {"thread_id": "managed-history-001"}}

    for text in ["第一条消息", "第二条消息", "第三条消息"]:
        result = graph.invoke(
            {"messages": [HumanMessage(content=text)]},
            config=config,
        )
        print("当前消息数：", len(result["messages"]))

    contents = [message.content for message in result["messages"]]
    print("最终保留消息：", contents)

    assert len(result["messages"]) == 4
    assert "第一条消息" not in contents
    assert "第二条消息" in contents
    assert "第三条消息" in contents


if __name__ == "__main__":
    main()
