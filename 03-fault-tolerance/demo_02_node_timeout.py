"""场景 2：使用 TimeoutPolicy 限制单次异步节点执行时间。"""

import asyncio
from typing import TypedDict

from langgraph.errors import NodeTimeoutError
from langgraph.graph import END, START, StateGraph
from langgraph.types import TimeoutPolicy


class TimeoutState(TypedDict, total=False):
    result: str


async def slow_api(_: TimeoutState) -> dict[str, str]:
    print("开始调用慢速 API")
    await asyncio.sleep(0.2)
    return {"result": "不应该执行到这里"}


def build_graph():
    builder = StateGraph(TimeoutState)
    builder.add_node(
        "slow_api",
        slow_api,
        timeout=TimeoutPolicy(run_timeout=0.05),
    )
    builder.add_edge(START, "slow_api")
    builder.add_edge("slow_api", END)
    return builder.compile()


async def run_demo() -> None:
    try:
        await build_graph().ainvoke({})
    except NodeTimeoutError as error:
        print(
            f"捕获超时：node={error.node}, kind={error.kind}, "
            f"elapsed={error.elapsed:.3f}s"
        )
        assert error.node == "slow_api"
        assert error.kind == "run"
    else:
        raise AssertionError("slow_api 应该触发 NodeTimeoutError")


if __name__ == "__main__":
    asyncio.run(run_demo())
