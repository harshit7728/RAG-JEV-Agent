import asyncio
from typing import Any

from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.retrieval.hybrid_search import hybrid_search
from app.retrieval.reranker import rerank
from app.services.gemini import generate_answer, rewrite_query
from app.services.jev import JevService


MAX_ATTEMPTS = 2


def _extract_choice(result: dict[str, Any], question_key: str) -> str | None:
    """Extract a choice from common response shapes; validate the result."""
    answers = result.get("answers", {})
    answer = answers.get(question_key) if isinstance(answers, dict) else None

    if isinstance(answer, str):
        return answer.lower()

    if isinstance(answer, dict):
        for key in ("choice", "value", "answer"):
            value = answer.get(key)
            if isinstance(value, str):
                return value.lower()

    return None


async def route_query(state: dict) -> dict:
    question = state["question"]

    try:
        jev = JevService()

        # Keep this question schema aligned with the payload that works
        # in your existing /api/jev/route endpoint.
        result = await jev.decide(
            state={"user_question": question},
            questions={
                "intent": {
                    "type": "choice",
                    "question": "Choose the best route for this user message.",
                    "options": ["knowledge", "greeting", "unsupported"],
                }
            },
        )

        choice = _extract_choice(result, "intent")
        if choice not in {"knowledge", "greeting", "unsupported"}:
            raise ValueError("JEV returned an unrecognized intent")

        return {
            "intent": choice,
            "route_confidence": 0.0,
            "query_for_retrieval": question,
        }

    except Exception as exc:
        # Fail safely: do not pretend JEV successfully routed the request.
        return {
            "intent": "knowledge",
            "route_confidence": 0.0,
            "query_for_retrieval": question,
            "error": f"JEV routing unavailable: {type(exc).__name__}",
        }


async def retrieve_context(state: dict) -> dict:
    query = state.get("query_for_retrieval") or state["question"]

    async with AsyncSessionLocal() as db:
        candidates = await hybrid_search(
            db=db,
            query=query,
            candidate_k=20,
            top_k=20,
        )

    # CrossEncoder prediction is synchronous, so run it off the event loop.
    ranked = await asyncio.to_thread(rerank, query, candidates, 5)

    chunks = [
        {
            "id": item["id"],
            "document_id": item["document_id"],
            "chunk_index": item["chunk_index"],
            "content": item["content"],
            "rerank_score": float(item["rerank_score"]),
        }
        for item in ranked
    ]

    context = "\n\n".join(
        f"[Source {i} | document={chunk['document_id']} "
        f"| chunk={chunk['chunk_index']}]\n{chunk['content']}"
        for i, chunk in enumerate(chunks, start=1)
    )

    return {
        "retrieved_chunks": chunks,
        "context": context,
        "attempts": state.get("attempts", 0) + 1,
    }


async def assess_evidence(state: dict) -> dict:
    chunks = state.get("retrieved_chunks", [])

    # Empty retrieval must never be treated as sufficient evidence.
    if not chunks:
        return {
            "evidence_sufficient": False,
            "evidence_reason": "No relevant document chunks were retrieved.",
        }

    try:
        jev = JevService()

        # Adapt this question payload to the schema used by your working
        # JEV endpoint. The answer parser accepts common response shapes.
        result = await jev.decide(
            state={
                "user_question": state["question"],
                "retrieved_evidence": state.get("context", ""),
            },
            questions={
                "evidence": {
                    "type": "choice",
                    "question": (
                        "Does the retrieved evidence directly support "
                        "answering the user's question?"
                    ),
                    "options": ["sufficient", "insufficient"],
                }
            },
        )

        choice = _extract_choice(result, "evidence")
        sufficient = choice == "sufficient"

        return {
            "evidence_sufficient": sufficient,
            "evidence_reason": (
                "JEV judged the retrieved evidence sufficient."
                if sufficient
                else "JEV did not confirm sufficient evidence."
            ),
        }

    except Exception:
        # Conservative fallback: require a strong lexical overlap.
        # This is only a basic fallback, not a semantic relevance model.
        query_terms = {
            word.lower().strip(".,?!:;()[]{}")
            for word in state["question"].split()
            if len(word) > 3
        }
        evidence = state.get("context", "").lower()
        overlap = sum(term in evidence for term in query_terms)

        sufficient = bool(query_terms) and overlap >= min(
            2, len(query_terms)
        )

        return {
            "evidence_sufficient": sufficient,
            "evidence_reason": (
                "Fallback keyword check used because JEV was unavailable."
            ),
        }


async def rewrite_search_query(state: dict) -> dict:
    try:
        rewritten = await rewrite_query(
            question=state["question"],
            previous_query=state.get("query_for_retrieval", state["question"]),
            evidence_summary=state.get("context", "")[:4000],
        )
    except Exception:
        # Avoid an infinite retry if the rewrite service is unavailable.
        rewritten = state["question"]

    return {"query_for_retrieval": rewritten}


async def produce_answer(state: dict) -> dict:
    if state.get("intent") == "greeting":
        return {
            "answer": "Hello! Ask me a question about the documents in your knowledge base.",
            "needs_human_review": False,
        }

    if state.get("intent") == "unsupported":
        return {
            "answer": "I can help with questions related to the knowledge base. Please ask about its documents.",
            "needs_human_review": False,
        }

    if not state.get("evidence_sufficient", False):
        return {
            "answer": (
                "I couldn't find enough reliable evidence in the uploaded "
                "documents to answer that confidently. Try rephrasing your "
                "question or uploading a relevant document."
            ),
            "needs_human_review": True,
        }

    answer = await generate_answer(
        question=state["question"],
        context=state.get("context", ""),
    )

    return {
        "answer": answer,
        "needs_human_review": False,
    }