"""场景 1：瞬时错误触发 RetryPolicy，节点成功后继续执行。"""

from typing import TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.types import RetryPolicy


class RetryState(TypedDict, total=False):
    result: str


def make_unstable_api():
    attempts = 0

    def call_api(_: RetryState) -> dict[str, str]:
        nonlocal attempts
        attempts += 1
        print(f"第 {attempts} 次调用外部 API")
        if attempts < 3:
            raise ConnectionError("模拟临时网络错误")
        return {"result": "API 调用成功"}

    return call_api


def build_graph():
    builder = StateGraph(RetryState)
    builder.add_node(
        "call_api",
        make_unstable_api(),
        retry_policy=RetryPolicy(
            max_attempts=3,
            initial_interval=0.01,
            backoff_factor=1.0,
            jitter=False,
            retry_on=ConnectionError,
        ),
    )
    builder.add_edge(START, "call_api")
    builder.add_edge("call_api", END)
    return builder.compile()


def main() -> None:
    result = build_graph().invoke({})
    print("最终结果：", result["result"])
    assert result["result"] == "API 调用成功"


if __name__ == "__main__":
    main()
