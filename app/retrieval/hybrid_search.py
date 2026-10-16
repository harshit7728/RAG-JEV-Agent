from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.retrieval.vector_search import vector_search
from app.retrieval.bm25_search import keyword_search
from app.retrieval.fusion import reciprocal_rank_fusion


async def hybrid_search(
    db: AsyncSession,
    tenant_id: UUID,
    query: str,
    candidate_k: int = 20,
    top_k: int = 10,
) -> list[dict]:
    vector_results = await vector_search(
        db, tenant_id, query, candidate_k
    )
    keyword_results = await keyword_search(
        db, tenant_id, query, candidate_k
    )

    return reciprocal_rank_fusion(
        [vector_results, keyword_results],
        k=60,
        top_k=top_k,
    )