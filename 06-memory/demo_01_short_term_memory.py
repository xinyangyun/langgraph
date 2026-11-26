"""场景 1：使用 checkpointer 保存同一 thread 的短期对话记忆。"""

from langchain_core.messages import AIMessage, HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph


def assistant(state: MessagesState) -> dict:
    human_messages = [
        message.content
        for message in state["messages"]
        if isinstance(message, HumanMessage)
    ]
    latest = str(human_messages[-1])

    if "叫什么" in latest:
        introduction = next(
            (
                str(message)
                for message in human_messages[:-1]
                if str(message).startswith("我叫")
            ),
            None,
        )
        reply = f"你之前说：{introduction}" if introduction else "你还没有告诉我名字。"
    elif latest.startswith("我叫"):
        reply = f"记住了，{latest.removeprefix('我叫')}。"
    else:
        reply = f"收到：{latest}"

    return {"messages": [AIMessage(content=reply)]}


def build_graph():
    builder = StateGraph(MessagesState)
    builder.add_node("assistant", assistant)
    builder.add_edge(START, "assistant")
    builder.add_edge("assistant", END)
    return builder.compile(checkpointer=InMemorySaver())


def main() -> None:
    graph = build_graph()
    config = {"configurable": {"thread_id": "short-term-001"}}

    first = graph.invoke(
        {"messages": [HumanMessage(content="我叫小明")]},
        config=config,
    )
    print("第一轮：", first["messages"][-1].content)

    second = graph.invoke(
        {"messages": [HumanMessage(content="我叫什么名字？")]},
        config=config,
    )
    print("第二轮：", second["messages"][-1].content)
    print("checkpoint 中的消息数：", len(second["messages"]))

    assert len(second["messages"]) == 4
    assert "我叫小明" in second["messages"][-1].content


if __name__ == "__main__":
    main()
