
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.jev import JevService, JevServiceError

router = APIRouter(prefix="/jev", tags=["JEV"])


class RouteRequest(BaseModel):
    query: str = Field(min_length=1, max_length=5000)


@router.get("/models")
async def get_models():
    try:
        return await JevService().list_models()
    except JevServiceError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc


@router.post("/route")
async def route_query(body: RouteRequest) -> dict[str, Any]:
    questions = {
        "intent": {
            "type": "choice",
            "instructions": (
                "Classify the user's message for an enterprise "
                "knowledge assistant."
            ),
            "criteria": {
                "knowledge": (
                    "A question requesting information, explanation, "
                    "or help that could use a knowledge base."
                ),
                "greeting": (
                    "A simple greeting or conversational pleasantry."
                ),
                "unsupported": (
                    "A request unrelated to the knowledge assistant's "
                    "supported information tasks."
                ),
            },
        }
    }

    try:
        result = await JevService().decide(
            state={"user_query": body.query},
            questions=questions,
        )

        answer = result["answers"]["intent"]

        return {
            "model": result["model"],
            "category": answer["choice"],
            "confidence": answer["confidence"],
            "probabilities": answer["probabilities"],
            "usage": result["usage"],
        }

    except JevServiceError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc
    except (KeyError, TypeError) as exc:
        raise HTTPException(
            status_code=502,
            detail="Unexpected JEV response format",
        ) from exc
