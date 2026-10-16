
from collections import defaultdict


def reciprocal_rank_fusion(
    result_lists: list[list[dict]],
    k: int = 60,
    top_k: int = 20,
) -> list[dict]:
    fused = {}
    scores = defaultdict(float)

    for results in result_lists:
        seen_in_list = set()

        for rank, item in enumerate(results, start=1):
            chunk_id = item["id"]

            if chunk_id in seen_in_list:
                continue

            seen_in_list.add(chunk_id)

            if chunk_id not in fused:
                fused[chunk_id] = item.copy()

            scores[chunk_id] += 1.0 / (k + rank)

    ranked = []

    for chunk_id, item in fused.items():
        item["rrf_score"] = scores[chunk_id]
        ranked.append(item)

    ranked.sort(
        key=lambda item: item["rrf_score"],
        reverse=True,
    )

    return ranked[:top_k]
