
from sqlalchemy.ext.asyncio import AsyncSession

from app.retrieval.hybrid_search import hybrid_search
from app.retrieval.reranker import rerank
from app.services.gemini import generate_answer


async def answer_from_documents(
    db: AsyncSession,
    query: str,
) -> dict:
    candidates = await hybrid_search(
        db=db,
        query=query,
        candidate_k=20,
        top_k=20,
    )

    if not candidates:
        return {
            "answer": (
                "I couldn't find relevant information "
                "in the uploaded documents."
            ),
            "sources": [],
        }

    top_chunks = rerank(
        query=query,
        candidates=candidates,
        top_k=5,
    )

    context = "\n\n".join(
        f"[Source {index}]\n{item['content']}"
        for index, item in enumerate(top_chunks, start=1)
    )

    answer = await generate_answer(
        question=query,
        context=context,
    )

    return {
        "answer": answer,
        "sources": [
            {
                "document_id": item["document_id"],
                "chunk_index": item["chunk_index"],
                "content": item["content"],
                "rerank_score": item["rerank_score"],
            }
            for item in top_chunks
        ],
    }
