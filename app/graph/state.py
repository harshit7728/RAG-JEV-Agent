from typing import Any, TypedDict


class RAGState(TypedDict, total=False):
    question: str
    query_for_retrieval: str

    intent: str
    route_confidence: float

    retrieved_chunks: list[dict[str, Any]]
    context: str

    evidence_sufficient: bool
    evidence_reason: str

    answer: str
    attempts: int
    needs_human_review: bool
    error: str | None