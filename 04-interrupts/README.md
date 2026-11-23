# LangGraph Interrupts Demo

本目录参考 LangGraph Interrupts 官方文档，展示动态暂停、恢复值校验、输入校验循环和并行 interrupt。

## 示例

| 文件 | 场景 | 关键 API |
| --- | --- | --- |
| `demo_01_approval_console.py` | 控制台人工审批 | `interrupt`、`Command(resume=...)` |
| `demo_02_typed_response.py` | 恢复值类型校验 | `response_schema`、Pydantic |
| `demo_03_validation_loop.py` | 无效输入后重新询问 | 条件边、重复 `interrupt` |
| `demo_04_parallel_interrupts.py` | 同时恢复多个暂停点 | interrupt ID、resume map |

## 运行

请使用 `langgraph-1.2` Conda 环境：

```bash
conda activate langgraph-1.2
python 04-interrupts/demo_01_approval_console.py
python 04-interrupts/demo_02_typed_response.py
python 04-interrupts/demo_03_validation_loop.py
python 04-interrupts/demo_04_parallel_interrupts.py
```

第一个 Demo 会在控制台等待输入 `approve` 或 `reject`。

## 关键规则

1. 图必须配置 checkpointer，并且首次执行与恢复使用相同的 `thread_id`。
2. 恢复时使用 `Command(resume=value)`；该值会成为对应 `interrupt()` 的返回值。
3. 恢复后节点会从函数开头重新执行，因此 `interrupt()` 前面的副作用必须可重复执行或具有幂等性。
4. 一个节点中的多个 `interrupt()` 调用顺序必须保持稳定，不要放在可能改变执行次数的条件分支或循环中。
5. 并行分支可能同时产生多个 interrupt，应使用 `{interrupt_id: value}` 映射精确恢复。

## 官方文档

- [Interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts)
