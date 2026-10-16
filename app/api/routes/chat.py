
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.gemini import generate_answer

router = APIRouter(prefix="/chat", tags=["Chat"])


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=5000)
    context: str = Field(default="", max_length=30000)


class ChatResponse(BaseModel):
    answer: str


@router.post("/answer", response_model=ChatResponse)
async def chat_answer(body: ChatRequest):
    try:
        answer = await generate_answer(
            question=body.question,
            context=body.context,
        )

        return ChatResponse(answer=answer)

    except ValueError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        # Log the exception internally in a production application.
        raise HTTPException(
            status_code=502,
            detail="The language model request failed.",
        ) from exc
