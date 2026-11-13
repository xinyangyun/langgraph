# LangGraph Store Demo

Store 用于保存可跨 thread 共享的长期数据；Checkpointer 保存的是某个 thread 的图执行状态。两者可以在同一张图中同时使用。

## 示例

| 文件 | 场景 | 关键 API |
| --- | --- | --- |
| `demo_01_basic_store.py` | CRUD、过滤和 namespace | `put`、`get`、`search`、`delete`、`list_namespaces` |
| `demo_02_cross_thread_memory.py` | 跨 thread、按用户隔离长期记忆 | `Runtime`、`context_schema`、`compile(store=...)` |
| `demo_03_semantic_search.py` | 使用 embedding 语义检索 | `InMemoryStore(index=...)`、`search(query=...)` |

## 运行

在项目根目录执行：

```bash
python 02-store/demo_01_basic_store.py
python 02-store/demo_02_cross_thread_memory.py
python 02-store/demo_03_semantic_search.py
```

三个示例都不需要 API Key。`InMemoryStore` 适合教学和测试，进程结束后数据会消失；生产环境应替换成持久化 Store 后端。

## Namespace 设计

示例使用元组组织数据：

```python
("users", user_id, "memories")
```

这样可以按用户隔离数据，也可以通过 namespace 前缀搜索或列出子 namespace。

## Store 与 Checkpointer

- Store：保存用户偏好、档案、长期记忆等跨 thread 数据。
- Checkpointer：保存图在某个 `thread_id` 下的状态、暂停位置和历史 checkpoint。
- `demo_02_cross_thread_memory.py` 同时使用两者，展示两个不同 thread 读取同一用户的长期记忆。

## 官方文档

- [LangGraph Stores](https://docs.langchain.com/oss/python/langgraph/stores)
