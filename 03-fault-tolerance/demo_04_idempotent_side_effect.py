"""场景 4：使用稳定幂等键避免节点重试造成重复扣款。"""

from typing import TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.types import RetryPolicy


class OrderState(TypedDict, total=False):
    order_id: str
    customer_id: str
    amount: int
    payment_key: str
    charged: bool


class FakePaymentProvider:
    def __init__(self) -> None:
        self.processed_keys: set[str] = set()
        self.charge_count = 0

    def charge(
        self,
        customer_id: str,
        amount: int,
        idempotency_key: str,
    ) -> bool:
        if idempotency_key in self.processed_keys:
            print(f"支付平台识别到重复请求：{idempotency_key}")
            return False

        self.processed_keys.add(idempotency_key)
        self.charge_count += 1
        print(f"实际扣款：customer={customer_id}, amount={amount}")
        return True


def build_graph(provider: FakePaymentProvider):
    attempts = 0

    def charge_customer(state: OrderState) -> dict:
        nonlocal attempts
        attempts += 1

        payment_key = f"charge:{state['order_id']}"
        provider.charge(
            customer_id=state["customer_id"],
            amount=state["amount"],
            idempotency_key=payment_key,
        )

        if attempts == 1:
            raise ConnectionError("扣款成功，但响应在返回前丢失")

        return {
            "payment_key": payment_key,
            "charged": True,
        }

    builder = StateGraph(OrderState)
    builder.add_node(
        "charge_customer",
        charge_customer,
        retry_policy=RetryPolicy(
            max_attempts=2,
            initial_interval=0.01,
            jitter=False,
            retry_on=ConnectionError,
        ),
    )
    builder.add_edge(START, "charge_customer")
    builder.add_edge("charge_customer", END)
    return builder.compile()


def main() -> None:
    provider = FakePaymentProvider()
    result = build_graph(provider).invoke(
        {
            "order_id": "order-001",
            "customer_id": "customer-001",
            "amount": 1200,
        }
    )
    print("最终状态：", result)
    print("支付平台实际扣款次数：", provider.charge_count)

    assert result["payment_key"] == "charge:order-001"
    assert result["charged"] is True
    assert provider.charge_count == 1


if __name__ == "__main__":
    main()
