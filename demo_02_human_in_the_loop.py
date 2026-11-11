"""场景 2：在敏感操作前 interrupt，并在人工审批后从 checkpoint 恢复。"""

from typing import Literal, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from diagram_utils import save_graph_image


class ApprovalState(TypedDict, total=False):
    request: str
    amount: int
    decision: Literal["approve", "reject"]
    result: str


def ask_for_approval(state: ApprovalState) -> dict[str, str]:
    decision = interrupt(
        {
            "question": "是否批准这笔付款？",
            "request": state["request"],
            "amount": state["amount"],
            "allowed_answers": ["approve", "reject"],
        }
    )
    if decision not in {"approve", "reject"}:
        raise ValueError("审批结果必须是 approve 或 reject")
    return {"decision": decision}


def route_after_review(state: ApprovalState) -> Literal["pay", "cancel"]:
    return "pay" if state["decision"] == "approve" else "cancel"


def pay(state: ApprovalState) -> dict[str, str]:
    return {"result": f"已支付 {state['amount']} 元：{state['request']}"}


def cancel(state: ApprovalState) -> dict[str, str]:
    return {"result": f"已拒绝付款：{state['request']}"}


def read_decision() -> Literal["approve", "reject"]:
    while True:
        decision = input("请输入审批结果（approve/reject）：").strip().lower()
        if decision in {"approve", "reject"}:
            return decision
        print("输入无效，请输入 approve 或 reject。")


def build_graph():
    builder = StateGraph(ApprovalState)
    builder.add_node("review", ask_for_approval)
    builder.add_node("pay", pay)
    builder.add_node("cancel", cancel)
    builder.add_edge(START, "review")
    builder.add_conditional_edges("review", route_after_review)
    builder.add_edge("pay", END)
    builder.add_edge("cancel", END)
    return builder.compile(checkpointer=InMemorySaver())


def main() -> None:
    graph = build_graph()
    config = {"configurable": {"thread_id": "approval-001"}}

    paused = graph.invoke(
        {"request": "购买数据库扩容服务", "amount": 1200},
        config=config,
    )
    interrupt_info = paused["__interrupt__"][0]
    print("图已暂停，等待人工输入：", interrupt_info.value)

    decision = read_decision()
    resumed = graph.invoke(Command(resume=decision), config=config)
    print("恢复后的结果：", resumed["result"])

    assert resumed["decision"] == decision
    expected_prefix = "已支付" if decision == "approve" else "已拒绝付款"
    assert resumed["result"].startswith(expected_prefix)
    save_graph_image(graph, "demo_02_human_in_the_loop.png")


if __name__ == "__main__":
    main()
