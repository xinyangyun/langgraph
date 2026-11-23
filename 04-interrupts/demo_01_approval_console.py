"""场景 1：在控制台人工批准或拒绝敏感操作。"""

from typing import Literal, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt


class ApprovalState(TypedDict, total=False):
    action: str
    result: str


def request_approval(
    state: ApprovalState,
) -> Command[Literal["execute_action", "cancel_action"]]:
    approved = interrupt(
        {
            "question": "是否执行这个敏感操作？",
            "action": state["action"],
        }
    )
    return Command(goto="execute_action" if approved else "cancel_action")


def execute_action(state: ApprovalState) -> dict[str, str]:
    return {"result": f"已执行：{state['action']}"}


def cancel_action(state: ApprovalState) -> dict[str, str]:
    return {"result": f"已取消：{state['action']}"}


def read_approval() -> bool:
    while True:
        answer = input("请输入审批结果（approve/reject）：").strip().lower()
        if answer == "approve":
            return True
        if answer == "reject":
            return False
        print("输入无效，请输入 approve 或 reject。")


def build_graph():
    builder = StateGraph(ApprovalState)
    builder.add_node("request_approval", request_approval)
    builder.add_node("execute_action", execute_action)
    builder.add_node("cancel_action", cancel_action)
    builder.add_edge(START, "request_approval")
    builder.add_edge("execute_action", END)
    builder.add_edge("cancel_action", END)
    return builder.compile(checkpointer=InMemorySaver())


def main() -> None:
    graph = build_graph()
    config = {"configurable": {"thread_id": "approval-console-001"}}

    paused = graph.invoke({"action": "删除生产环境缓存"}, config=config)
    print("图已暂停：", paused["__interrupt__"][0].value)

    approved = read_approval()
    resumed = graph.invoke(Command(resume=approved), config=config)
    print("恢复后的结果：", resumed["result"])

    expected_prefix = "已执行" if approved else "已取消"
    assert resumed["result"].startswith(expected_prefix)


if __name__ == "__main__":
    main()
