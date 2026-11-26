"""场景 1：把一个确定性的 LangGraph 运行轨迹上传到 LangSmith。"""

import os
from pathlib import Path
from typing import TypedDict

from dotenv import load_dotenv
from langchain_core.tracers.langchain import wait_for_all_tracers
from langgraph.graph import END, START, StateGraph


DEFAULT_PROJECT = "langgraph-python-demo"
ENV_FILE = Path(__file__).resolve().with_name(".env")


class OrderState(TypedDict, total=False):
    order_id: str
    amount: float
    risk_level: str
    result: str


def check_risk(state: OrderState) -> dict[str, str]:
    """LangSmith 中会显示为 check_risk 节点。"""
    risk_level = "high" if state["amount"] >= 1000 else "low"
    print(f"[check_risk] order_id={state['order_id']}, risk={risk_level}")
    return {"risk_level": risk_level}


def create_result(state: OrderState) -> dict[str, str]:
    """根据上一个节点写入的状态生成最终结果。"""
    result = "需要人工复核" if state["risk_level"] == "high" else "自动通过"
    print(f"[create_result] result={result}")
    return {"result": result}


def build_graph():
    builder = StateGraph(OrderState)
    builder.add_node("check_risk", check_risk)
    builder.add_node("create_result", create_result)
    builder.add_edge(START, "check_risk")
    builder.add_edge("check_risk", "create_result")
    builder.add_edge("create_result", END)
    return builder.compile(name="langsmith_order_graph")


def configure_langsmith() -> str:
    """校验追踪配置，并返回本次运行使用的 LangSmith project。"""
    # override=False：PyCharm Run Configuration 中的变量优先于 .env。
    load_dotenv(ENV_FILE, override=False)

    api_key = os.getenv("LANGSMITH_API_KEY", "").strip()
    if not api_key or api_key == "your-langsmith-api-key":
        raise RuntimeError(
            f"没有配置 LANGSMITH_API_KEY。请填写 {ENV_FILE}，或者在 PyCharm "
            "Run Configuration 的 Environment variables 中配置。"
        )

    os.environ["LANGSMITH_TRACING"] = "true"
    project = os.getenv("LANGSMITH_PROJECT", DEFAULT_PROJECT).strip()
    os.environ["LANGSMITH_PROJECT"] = project or DEFAULT_PROJECT
    return os.environ["LANGSMITH_PROJECT"]


def save_graph_diagram(graph) -> None:
    """保存 PNG 流程图；网络渲染失败时保留 Mermaid 源文件。"""
    output_dir = Path(__file__).resolve().parent / "graph_images"
    output_dir.mkdir(parents=True, exist_ok=True)
    png_path = output_dir / "demo_01_tracing.png"
    mermaid_path = output_dir / "demo_01_tracing.mmd"
    mermaid_path.write_text(graph.get_graph().draw_mermaid(), encoding="utf-8")

    try:
        png_path.write_bytes(graph.get_graph().draw_mermaid_png())
        print(f"流程图已保存：{png_path}")
    except Exception as exc:
        print(f"PNG 生成失败，已保留 Mermaid 文件：{mermaid_path}")
        print(f"失败原因：{exc}")


def main() -> None:
    project = configure_langsmith()
    graph = build_graph()
    save_graph_diagram(graph)

    config = {
        "run_name": "demo_order_001",
        "tags": ["langgraph-demo", "pycharm"],
        "metadata": {
            "demo": "08-langsmith/demo_01_tracing.py",
            "environment": "local",
        },
    }
    result = graph.invoke(
        {"order_id": "ORDER-001", "amount": 1280.0},
        config=config,
    )

    # 短脚本退出前等待后台 tracing 线程完成上传。
    wait_for_all_tracers()

    print("最终状态：", result)
    print(f"LangSmith project：{project}")
    print("请在 LangSmith Tracing Projects 中查看 demo_order_001 这条 trace。")
    assert result["risk_level"] == "high"
    assert result["result"] == "需要人工复核"


if __name__ == "__main__":
    main()
