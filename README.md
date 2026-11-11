# LangGraph Checkpointer 四场景 Demo

这组示例对应 LangGraph checkpointer 的四个核心使用场景：

| 文件 | 场景 | 关键 API |
| --- | --- | --- |
| `checkpoint/demo_01_conversation_memory.py` | 同一会话的多轮记忆 | `InMemorySaver`、`thread_id`、`get_state` |
| `checkpoint/demo_02_human_in_the_loop.py` | 人工审批后恢复执行 | `interrupt`、`Command(resume=...)` |
| `checkpoint/demo_03_time_travel.py` | 查看历史并从旧状态创建分支 | `get_state_history`、`update_state` |
| `checkpoint/demo_04_fault_recovery.py` | 节点失败后从 checkpoint 续跑 | `get_state`、`invoke(None, config)` |

四个脚本都不调用大模型，不需要 API Key。业务节点是确定性的，便于专注观察 checkpoint 的行为。

## 安装

建议使用 Python 3.10 或更高版本：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## 运行

```bash
python checkpoint/demo_01_conversation_memory.py
python checkpoint/demo_02_human_in_the_loop.py
python checkpoint/demo_03_time_travel.py
python checkpoint/demo_04_fault_recovery.py
```

每个脚本末尾都有断言。脚本无异常退出即表示对应流程运行成功。

运行 `checkpoint/demo_02_human_in_the_loop.py` 时，图会在人工审批节点暂停，并在控制台等待输入：

```text
请输入审批结果（approve/reject）：
```

输入 `approve` 会进入付款节点，输入 `reject` 会进入取消节点；其他输入会要求重新输入。

每个 demo 运行完成后还会把流程结构图保存到 `checkpoint/graph_images/`：

```text
checkpoint/
├── demo_01_conversation_memory.py
├── demo_02_human_in_the_loop.py
├── demo_03_time_travel.py
├── demo_04_fault_recovery.py
├── diagram_utils.py
└── graph_images/
    ├── demo_01_conversation_memory.png
    ├── demo_02_human_in_the_loop.png
    ├── demo_03_time_travel.png
    └── demo_04_fault_recovery.png
```

PNG 使用 Mermaid 在线渲染，因此生成图片时需要网络。若渲染失败，脚本仍会正常结束，在同一目录保留 `.mmd` Mermaid 源文件，并提示检查网络；网络恢复后重新运行即可生成 PNG。

## 核心概念

### 1. Checkpointer 和 thread_id

图只有在 `compile(checkpointer=...)` 时传入 checkpointer，才会在每个 super-step 保存状态。调用图时还要在配置中提供 `thread_id`：

```python
config = {"configurable": {"thread_id": "example-001"}}
```

相同的 `thread_id` 会读取并继续同一条执行线程；换一个 `thread_id` 就会得到一条独立线程。

### 2. InMemorySaver 的适用范围

`InMemorySaver` 适合教学和测试。进程退出后数据会消失，生产环境应替换为持久化后端，例如 PostgreSQL 对应的 checkpointer。

### 3. 恢复执行时为什么传入 None

当状态已经在 checkpoint 中时，`graph.invoke(None, config=...)` 表示不再提交新的输入，而是从该 checkpoint 记录的下一节点继续运行。

### 4. interrupt 的恢复方式

`interrupt(...)` 会暂停图并把信息返回给调用方。人工在控制台输入结果后，使用输入值恢复同一条线程：

```python
decision = input("请输入审批结果（approve/reject）：").strip().lower()
graph.invoke(Command(resume=decision), config=config)
```

恢复时必须使用原来的 `thread_id`。

## 官方文档

- [Checkpointer libraries](https://docs.langchain.com/oss/python/langgraph/checkpointers)
- [Persistence](https://docs.langchain.com/oss/python/langgraph/persistence)
- [Interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts)
