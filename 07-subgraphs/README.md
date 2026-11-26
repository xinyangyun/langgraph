# LangGraph Subgraphs Demo

本目录参考 LangGraph Subgraphs 官方文档，使用无模型、确定性的节点演示子图接口和持久化模式。

## 示例

| 文件 | 场景 | 关键概念 |
| --- | --- | --- |
| `demo_01_different_schemas.py` | 父子图状态结构不同 | 包装节点映射输入和输出，并分别打印父图/子图拓扑 |
| `demo_02_shared_state.py` | 父子图共享状态键 | 编译后的子图直接作为父图节点 |
| `demo_03_subgraph_persistence.py` | 比较每次调用隔离与同 thread 累积 | `checkpointer=None`、`checkpointer=True` |

## 运行

```bash
conda activate langgraph-1.2
python 07-subgraphs/demo_01_different_schemas.py
python 07-subgraphs/demo_02_shared_state.py
python 07-subgraphs/demo_03_subgraph_persistence.py
```

## 两种调用接口

- 父图和子图的 state schema 不同时，在父图节点里调用 `subgraph.invoke()`，显式转换子图输入和输出。
- 父图和子图共享 state key 时，将已编译子图直接传给 `parent_builder.add_node()`。

`demo_01_different_schemas.py` 中，父图的 `call_research_subgraph` 节点调用独立编译的 `research_subgraph`。父图把 `question` 映射为子图的 `subject`，再把子图的 `summary` 映射回父图的 `answer`。运行时会分别打印父图与子图拓扑，包装节点是两张图之间的调用边界。

## 子图持久化

- `checkpointer=None`（默认）：每次调用子图状态独立；子图仍继承父图 checkpointer，支持单次调用中的中断和恢复。
- `checkpointer=True`：子图状态按父图 `thread_id` 在多次调用间累积，适合需要多轮记忆的子 agent。
- `checkpointer=False`：完全无 checkpoint，不支持子图内部中断和 durable execution。

启用 per-thread 子图时，同一子图不要并行调用，否则多个调用会竞争同一子图 checkpoint namespace。

## 官方文档

- [Use subgraphs](https://docs.langchain.com/oss/python/langgraph/use-subgraphs)
