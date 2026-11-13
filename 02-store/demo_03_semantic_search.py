"""场景 3：使用本地 embedding 对 Store 中的记忆进行语义检索。"""

import math

from langchain_core.embeddings import Embeddings
from langgraph.store.memory import InMemoryStore


class LocalKeywordEmbeddings(Embeddings):
    """教学用本地 embedding，避免示例依赖外部模型和 API Key。"""

    vocabulary = ("python", "fastapi", "api", "旅行", "爬山", "川菜")

    def _embed(self, text: str) -> list[float]:
        normalized_text = text.lower()
        vector = [
            float(normalized_text.count(keyword)) for keyword in self.vocabulary
        ]
        length = math.sqrt(sum(value * value for value in vector))
        if length == 0:
            return [0.0] * len(vector)
        return [value / length for value in vector]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)


def main() -> None:
    embeddings = LocalKeywordEmbeddings()
    store = InMemoryStore(
        index={
            "embed": embeddings,
            "dims": len(embeddings.vocabulary),
            "fields": ["text"],
        }
    )
    namespace = ("users", "alice", "memories")

    store.put(namespace, "programming", {"text": "我喜欢用 Python 和 FastAPI 开发 API"})
    store.put(namespace, "outdoor", {"text": "周末喜欢爬山和旅行"})
    store.put(namespace, "food", {"text": "最喜欢川菜"})

    results = store.search(namespace, query="Python API", limit=3)
    for rank, item in enumerate(results, start=1):
        print(
            f"{rank}. key={item.key}, score={item.score:.3f}, "
            f"text={item.value['text']}"
        )

    assert results[0].key == "programming"
    assert results[0].score is not None and results[0].score > 0.8


if __name__ == "__main__":
    main()
