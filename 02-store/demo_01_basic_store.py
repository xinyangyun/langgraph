"""场景 1：直接使用 InMemoryStore 完成 CRUD、过滤和 namespace 查询。"""

from langgraph.store.memory import InMemoryStore


def main() -> None:
    store = InMemoryStore()
    namespace = ("users", "alice", "preferences")

    store.put(
        namespace,
        "language",
        {"value": "Python", "category": "programming"},
    )
    store.put(
        namespace,
        "editor",
        {"value": "PyCharm", "category": "tool"},
    )

    language = store.get(namespace, "language")
    print("读取单条记录：", language.value)

    programming_preferences = store.search(
        ("users", "alice"),
        filter={"category": "programming"},
    )
    print("按条件搜索：", [item.value for item in programming_preferences])

    namespaces = store.list_namespaces(prefix=("users", "alice"))
    print("Alice 的 namespaces：", namespaces)

    store.delete(namespace, "editor")
    remaining = store.search(("users", "alice"))
    print("删除后的记录：", [item.value for item in remaining])

    assert language.value["value"] == "Python"
    assert namespaces == [("users", "alice", "preferences")]
    assert [item.key for item in remaining] == ["language"]


if __name__ == "__main__":
    main()
