"""场景 4：节点失败后，使用 checkpoint 从失败位置继续执行。"""

from operator import add
from typing import Annotated, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

from diagram_utils import save_graph_image


class JobState(TypedDict, total=False):
    raw_data: str
    processed_data: str
    saved: bool
    events: Annotated[list[str], add]


def fetch_data(_: JobState) -> dict:
    print("执行 fetch_data")
    return {"raw_data": "langgraph", "events": ["数据已获取"]}


def make_unstable_processor():
    attempts = 0

    def process_data(state: JobState) -> dict:
        nonlocal attempts
        attempts += 1
        print(f"执行 process_data，第 {attempts} 次尝试")
        if attempts == 1:
            raise ConnectionError("模拟外部服务暂时不可用")
        return {
            "processed_data": state["raw_data"].upper(),
            "events": ["数据已处理"],
        }

    return process_data


def save_data(state: JobState) -> dict:
    print("执行 save_data")
    assert state["processed_data"] == "LANGGRAPH"
    return {"saved": True, "events": ["数据已保存"]}


def build_graph():
    builder = StateGraph(JobState)
    builder.add_node("fetch_data", fetch_data)
    builder.add_node("process_data", make_unstable_processor())
    builder.add_node("save_data", save_data)
    builder.add_edge(START, "fetch_data")
    builder.add_edge("fetch_data", "process_data")
    builder.add_edge("process_data", "save_data")
    builder.add_edge("save_data", END)
    return builder.compile(checkpointer=InMemorySaver())


def main() -> None:
    graph = build_graph()
    config = {"configurable": {"thread_id": "job-001"}}

    try:
        graph.invoke({"events": []}, config=config)
    except ConnectionError as exc:
        print("捕获到预期错误：", exc)

    failed_snapshot = graph.get_state(config)
    print("失败后已保存的状态：", failed_snapshot.values)
    print("下一步待执行节点：", failed_snapshot.next)

    recovered = graph.invoke(None, config=config)
    print("恢复后的最终状态：", recovered)

    assert failed_snapshot.next == ("process_data",)
    assert recovered["saved"] is True
    assert recovered["events"] == ["数据已获取", "数据已处理", "数据已保存"]
    save_graph_image(graph, "demo_04_fault_recovery.png")


if __name__ == "__main__":
    main()
