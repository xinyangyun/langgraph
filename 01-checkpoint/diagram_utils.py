"""Utilities for exporting LangGraph diagrams beside the demo scripts."""

from pathlib import Path


def save_graph_image(graph, filename: str) -> Path:
    output_dir = Path(__file__).resolve().parent / "graph_images"
    output_dir.mkdir(parents=True, exist_ok=True)

    image_path = output_dir / filename
    try:
        graph.get_graph().draw_mermaid_png(output_file_path=str(image_path))
    except Exception:
        mermaid_path = image_path.with_suffix(".mmd")
        mermaid_path.write_text(graph.get_graph().draw_mermaid(), encoding="utf-8")
        print(
            f"PNG 渲染失败；已保存 Mermaid 源文件：{mermaid_path}。"
            "请检查网络后重新运行以生成 PNG。"
        )
        return mermaid_path

    print(f"流程图已保存：{image_path}")
    return image_path
