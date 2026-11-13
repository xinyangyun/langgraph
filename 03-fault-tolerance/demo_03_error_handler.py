"""场景 3：重试耗尽后由 error_handler 执行补偿并路由。"""

from typing import TypedDict

from langgraph.errors import NodeError
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, RetryPolicy


class PaymentState(TypedDict, total=False):
    order_id: str
    status: str
    error_message: str


def charge_payment(state: PaymentState) -> dict[str, str]:
    print(f"订单 {state['order_id']}：调用支付网关")
    raise ConnectionError("支付网关暂时不可用")


def payment_error_handler(
    state: PaymentState,
    error: NodeError,
) -> Command:
    print(f"节点 {error.node} 重试耗尽：{error.error}")
    return Command(
        update={
            "status": "compensated",
            "error_message": str(error.error),
        },
        goto="finalize",
    )


def finalize(state: PaymentState) -> dict[str, str]:
    return {"status": f"{state['status']}: order {state['order_id']} finalized"}


def build_graph():
    builder = StateGraph(PaymentState)
    builder.add_node(
        "charge_payment",
        charge_payment,
        retry_policy=RetryPolicy(
            max_attempts=3,
            initial_interval=0.01,
            backoff_factor=1.0,
            jitter=False,
            retry_on=ConnectionError,
        ),
        error_handler=payment_error_handler,
    )
    builder.add_node("finalize", finalize)
    builder.add_edge(START, "charge_payment")
    builder.add_edge("finalize", END)
    return builder.compile()


def main() -> None:
    result = build_graph().invoke({"order_id": "order-001"})
    print("最终状态：", result)

    assert result["status"] == "compensated: order order-001 finalized"
    assert result["error_message"] == "支付网关暂时不可用"


if __name__ == "__main__":
    main()
