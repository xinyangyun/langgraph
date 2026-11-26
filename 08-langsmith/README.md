# LangGraph 接入 LangSmith

本目录演示如何把 LangGraph 的一次完整运行以及内部节点自动上传到 LangSmith。示例不调用大模型，只需要 LangSmith API Key。

## 配置

在 LangSmith 创建 API Key。推荐先把模板复制为本地配置文件：

```bash
cp 08-langsmith/.env.example 08-langsmith/.env
```

然后填写 `08-langsmith/.env`：

```ini
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=你的LangSmith API Key
LANGSMITH_PROJECT=langgraph-python-demo
```

脚本会通过 `python-dotenv` 主动加载这个文件，PyCharm 直接断点运行也能读取。

也可以不使用 `.env`，改为在 PyCharm 中打开：

`Run | Edit Configurations | Environment variables`

添加以下变量：

```ini
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=你的LangSmith API Key
LANGSMITH_PROJECT=langgraph-python-demo
```

如果组织级 API Key 可以访问多个 workspace，再增加：

```ini
LANGSMITH_WORKSPACE_ID=对应的workspace ID
```

不要把真实 API Key 写进 Python 文件、`.env.example` 或提交到 Git。`.env.example` 只是配置模板，项目根目录的 `.gitignore` 已忽略所有目录中的 `.env`。

## PyCharm 断点运行

1. 使用项目现有的 `langgraph-1.2` Conda 解释器。
2. 打开 `demo_01_tracing.py`。
3. 可在 `check_risk`、`create_result` 和 `graph.invoke` 行设置断点。
4. 右键脚本，选择 `Debug 'demo_01_tracing'`。

运行完成后，在 LangSmith 的 `langgraph-python-demo` project 中查看名为 `demo_order_001` 的 trace。展开它可以看到 `check_risk` 和 `create_result` 两个节点的输入、输出、耗时和执行顺序。

流程图会写入：

```text
08-langsmith/graph_images/demo_01_tracing.png
```

PNG 使用 Mermaid 在线渲染；网络不可用时会保留同名 `.mmd` 文件。

## 运行

```bash
conda activate langgraph-1.2
python 08-langsmith/demo_01_tracing.py
```

## 关键点

- LangGraph 原生支持 LangSmith tracing，不需要给每个节点手工添加上传代码。
- `LANGSMITH_PROJECT` 用于把不同应用或环境的 traces 分组。
- `run_name` 是本次顶层运行名称，`tags` 和 `metadata` 用于筛选与定位。
- `wait_for_all_tracers()` 确保短脚本退出前，后台 trace 已经上传完成。

## 官方文档

- [LangSmith observability quickstart](https://docs.langchain.com/langsmith/observability-quickstart)
- [Trace a LangGraph application](https://docs.langchain.com/langsmith/trace-with-langgraph)
