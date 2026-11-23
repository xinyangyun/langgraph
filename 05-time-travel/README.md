# LangGraph Time Travel Demo

本目录参考 LangGraph Time Travel 官方文档，展示历史 checkpoint 重放、状态分叉，以及回到 interrupt 之前重新选择。

## 示例

| 文件 | 场景 | 关键 API |
| --- | --- | --- |
| `demo_01_replay_checkpoint.py` | 从历史 checkpoint 重放后续节点 | `get_state_history`、`invoke(None, checkpoint_config)` |
| `demo_02_fork_state.py` | 修改历史状态并创建新分支 | `update_state`、`as_node` |
| `demo_03_replay_interrupt.py` | 回到 interrupt 前创建新的人工输入分支 | `interrupt`、`Command(resume=...)` |

## 运行

```bash
conda activate langgraph-1.2
python 05-time-travel/demo_01_replay_checkpoint.py
python 05-time-travel/demo_02_fork_state.py
python 05-time-travel/demo_03_replay_interrupt.py
```

## Replay 与 Fork

Replay 从历史 checkpoint 继续执行：

```python
graph.invoke(None, config=historical_snapshot.config)
```

checkpoint 之前的节点不会重新执行，checkpoint 之后的节点会重新执行。

Fork 先修改历史 checkpoint，再执行后续节点：

```python
fork_config = graph.update_state(
    historical_snapshot.config,
    {"topic": "鸡"},
    as_node="generate_topic",
)
graph.invoke(None, config=fork_config)
```

`as_node` 表示这次状态更新应被视为哪个节点的输出，它会影响下一步执行的节点。

## 注意事项

1. 图必须配置 checkpointer，并使用稳定的 `thread_id`。
2. 历史快照的 `config` 中包含 `checkpoint_id`，用于定位具体历史状态。
3. Replay 会重新执行 checkpoint 之后的节点，因此外部副作用必须具有幂等性。
4. 从 interrupt 之前重放时，interrupt 会再次触发，需要新的 `Command(resume=...)`。

## 官方文档

- [Use time travel](https://docs.langchain.com/oss/python/langgraph/use-time-travel)
