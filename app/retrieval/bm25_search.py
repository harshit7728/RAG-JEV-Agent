
from sqlalchemy import func, select,UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.models.document_chunk import DocumentChunk


async def keyword_search(
    db: AsyncSession,
    query: str,
     tenant_id: UUID,
    top_k: int = 20,
) -> list[dict]:
    tsquery = func.websearch_to_tsquery(
        "english",
        query,
    )

    rank = func.ts_rank_cd(
        DocumentChunk.search_vector,
        tsquery,
    ).label("rank")

    statement = (
        select(DocumentChunk, rank)
        .join(
            Document,
            Document.id == DocumentChunk.document_id,
        )
        .where(
            Document.tenant_id == tenant_id,
            Document.status == "embedded",
            DocumentChunk.search_vector.op("@@")(tsquery),
        )
        .order_by(rank.desc())
        .limit(top_k)
    )

    result = await db.execute(statement)

    return [
        {
            "id": str(chunk.id),
            "document_id": str(chunk.document_id),
            "chunk_index": chunk.chunk_index,
            "content": chunk.content,
            "keyword_score": float(score),
        }
        for chunk, score in result.all()
    ]
