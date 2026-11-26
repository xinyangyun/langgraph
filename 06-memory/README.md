# LangGraph Add Memory Demo

本目录参考 LangGraph Add Memory 官方文档，展示短期记忆、长期记忆和消息历史管理。

## 示例

| 文件 | 场景 | 关键 API |
| --- | --- | --- |
| `demo_01_short_term_memory.py` | 同一 thread 的多轮对话记忆 | `MessagesState`、`InMemorySaver` |
| `demo_02_long_term_memory.py` | 跨 thread、按用户隔离的长期记忆 | `InMemoryStore`、`Runtime`、`context_schema` |
| `demo_03_manage_message_history.py` | 删除旧消息控制上下文长度 | `RemoveMessage`、`MessagesState` |
| `settings.py` | 以后接入真实服务的测试地址 | 模型地址、PostgreSQL 地址 |

## 运行

```bash
conda activate langgraph-1.2
python 06-memory/demo_01_short_term_memory.py
python 06-memory/demo_02_long_term_memory.py
python 06-memory/demo_03_manage_message_history.py
```

三个 Demo 都使用内存后端，不需要模型 API Key，也不会连接数据库。

## 测试地址

`settings.py` 暂时提供以下占位地址：

```python
TEST_MODEL_BASE_URL = "http://127.0.0.1:9999/v1"
TEST_POSTGRES_URI = "postgresql://demo:demo@127.0.0.1:5432/langgraph_memory_demo?sslmode=disable"
```

这些地址默认不会被访问。以后接入真实模型或 PostgreSQL 时，再替换成实际地址并安装对应依赖。

## Memory 类型

- 短期记忆：由 checkpointer 按 `thread_id` 保存，只属于一条执行线程。
- 长期记忆：由 Store 按 namespace 保存，可以跨 `thread_id` 读取。
- 消息管理：对过长的消息历史进行删除、裁剪或总结，避免上下文持续增长。

## 官方文档

- [Add memory](https://docs.langchain.com/oss/python/langgraph/add-memory)
