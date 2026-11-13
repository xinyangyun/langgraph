# LangGraph Fault Tolerance Demo

本目录对应 LangGraph Fault Tolerance 官方文档，展示节点级重试、超时、错误补偿和幂等副作用。

> `timeout` 和 `error_handler` 需要 `langgraph>=1.2`。

## 示例

| 文件 | 场景 | 关键 API |
| --- | --- | --- |
| `demo_01_retry_policy.py` | 瞬时网络错误自动重试 | `RetryPolicy` |
| `demo_02_node_timeout.py` | 限制异步节点单次执行时间 | `TimeoutPolicy`、`NodeTimeoutError` |
| `demo_03_error_handler.py` | 重试耗尽后执行补偿流程 | `NodeError`、`error_handler`、`Command` |
| `demo_04_idempotent_side_effect.py` | 避免重试造成重复扣款 | 稳定 idempotency key |

## 安装

在项目根目录创建或激活虚拟环境：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## 运行

```bash
python 03-fault-tolerance/demo_01_retry_policy.py
python 03-fault-tolerance/demo_02_node_timeout.py
python 03-fault-tolerance/demo_03_error_handler.py
python 03-fault-tolerance/demo_04_idempotent_side_effect.py
```

## 执行顺序

节点失败后的处理顺序是：

```text
节点执行
  -> 超时或抛出异常
  -> RetryPolicy 判断是否重试
  -> 重试全部耗尽
  -> error_handler 执行补偿或路由
```

节点重试会从函数开头重新执行，因此支付、发邮件、外部数据库写入等副作用必须具有幂等性。第四个示例从已经存在的 `order_id` 派生稳定幂等键，使第一次扣款成功但响应丢失时，第二次调用不会重复扣款。

## 官方文档

- [Fault tolerance](https://docs.langchain.com/oss/python/langgraph/fault-tolerance)
