
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.retrieval.answering import answer_from_documents

router = APIRouter(prefix="/rag", tags=["RAG"])


class RAGRequest(BaseModel):
    question: str = Field(min_length=1, max_length=5000)


@router.post("/ask")
async def ask_rag(
    body: RAGRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await answer_from_documents(
            db=db,
            query=body.question,
        )
    except Exception as exc:
        # Log the exception internally in production.
        raise HTTPException(
            status_code=502,
            detail="RAG processing failed.",
        ) from exc
