from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.services.embeddings import embed_query


async def vector_search(
    db: AsyncSession,
    tenant_id: UUID,
    query: str,
    top_k: int = 20,
) -> list[dict]:
    query_embedding = await embed_query(query)

    distance = DocumentChunk.embedding.cosine_distance(
        query_embedding
    ).label("distance")

    statement = (
        select(DocumentChunk, distance)
        .join(Document, Document.id == DocumentChunk.document_id)
        .where(
            Document.tenant_id == tenant_id,
            Document.status == "embedded",
        )
        .order_by(distance)
        .limit(top_k)
    )

    result = await db.execute(statement)

    return [
        {
            "id": str(chunk.id),
            "document_id": str(chunk.document_id),
            "chunk_index": chunk.chunk_index,
            "content": chunk.content,
            "distance": float(distance_value),
        }
        for chunk, distance_value in result.all()
    ]