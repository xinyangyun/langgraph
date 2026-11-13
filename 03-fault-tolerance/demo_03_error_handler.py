"""场景 3：重试耗尽后由 error_handler 执行补偿并路由。"""

from typing import TypedDict

from langgraph.errors import NodeError
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, RetryPolicy


class PaymentState(TypedDict, total=False):
    order_id: str
    status: str
    error_message: str


def make_charge_payment():
    attempts = 0

    def charge_payment(state: PaymentState) -> dict[str, str]:
        nonlocal attempts
        attempts += 1
        print(f"charge_payment 第 {attempts} 次执行：订单 {state['order_id']}")
        raise ConnectionError("支付网关暂时不可用")

    return charge_payment


def payment_error_handler(
    state: PaymentState,
    error: NodeError,
) -> Command:
    print(f"进入 payment_error_handler：节点 {error.node} 重试耗尽")
    print(f"失败原因：{error.error}")
    print("补偿完成后通过 Command(goto='finalize') 进入 finalize")
    return Command(
        update={
            "status": "compensated",
            "error_message": str(error.error),
        },
        goto="finalize",
    )


def finalize(state: PaymentState) -> dict[str, str]:
    print("进入 finalize 节点")
    return {"status": f"{state['status']}: order {state['order_id']} finalized"}


def build_graph():
    builder = StateGraph(PaymentState)
    builder.add_node(
        "charge_payment",
        make_charge_payment(),
        retry_policy=RetryPolicy(
            max_attempts=3,
            initial_interval=0.01,
            backoff_factor=1.0,
            jitter=False,
            retry_on=ConnectionError,
        ),
        # RetryPolicy 耗尽后，LangGraph 才会调用这个错误处理节点。
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
