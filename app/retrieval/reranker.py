
from functools import lru_cache

from sentence_transformers import CrossEncoder


@lru_cache(maxsize=1)
def get_reranker() -> CrossEncoder:
    return CrossEncoder("BAAI/bge-reranker-base")


def rerank(
    query: str,
    candidates: list[dict],
    top_k: int = 5,
) -> list[dict]:
    if not candidates:
        return []

    model = get_reranker()

    pairs = [
        (query, item["content"])
        for item in candidates
    ]

    scores = model.predict(pairs)

    ranked = []

    for item, score in zip(candidates, scores):
        result = item.copy()
        result["rerank_score"] = float(score)
        ranked.append(result)

    ranked.sort(
        key=lambda item: item["rerank_score"],
        reverse=True,
    )

    return ranked[:top_k]
