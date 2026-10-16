import uuid

from fastapi import APIRouter, HTTPException, Request
from langgraph.types import Command
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/agent", tags=["Agent"])



class AgentRequest(BaseModel):
    question: str = Field(min_length=1, max_length=5000)


class ReviewRequest(BaseModel):
    action: str = Field(pattern="^(approve|reject)$")
    revised_answer: str | None = Field(default=None, max_length=10000)


def format_result(result: dict, thread_id: str) -> dict:
    interrupts = result.get("__interrupt__", ())
    paused = bool(interrupts)

    review_data = None
    if paused:
        value = interrupts[0].value
        review_data = value if isinstance(value, dict) else {
            "message": str(value)
        }

    return {
        "thread_id": thread_id,
        "status": "paused_for_review" if paused else "completed",
        "answer": result.get("answer", ""),
        "intent": result.get("intent", "knowledge"),
        "attempts": result.get("attempts", 0),
        "needs_human_review": result.get("needs_human_review", False),
        "sources": [
            {
                "document_id": chunk["document_id"],
                "chunk_index": chunk["chunk_index"],
                "rerank_score": chunk["rerank_score"],
            }
            for chunk in result.get("retrieved_chunks", [])
        ],
        "review": review_data,
    }


@router.post("/ask")
async def ask_agent(payload: AgentRequest, request: Request):
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    try:
        result = await request.app.state.agent_graph.ainvoke(
            {
                "question": payload.question.strip(),
                "query_for_retrieval": payload.question.strip(),
                "attempts": 0,
                "retrieved_chunks": [],
                "context": "",
            },
            config=config,
        )

        return format_result(result, thread_id)

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="The agent could not complete the request.",
        ) from exc


@router.post("/{thread_id}/review")
async def review_agent(
    thread_id: str,
    payload: ReviewRequest,
    request: Request,
):
    config = {"configurable": {"thread_id": thread_id}}

    try:
        result = await request.app.state.agent_graph.ainvoke(
            Command(resume={
                "action": payload.action,
                "revised_answer": payload.revised_answer,
            }),
            config=config,
        )

        return format_result(result, thread_id)

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail="Could not resume this workflow. Check its thread ID and status.",
        ) from exc