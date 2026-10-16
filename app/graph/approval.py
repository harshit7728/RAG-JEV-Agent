from typing import Any

from langgraph.types import interrupt


def human_review(state: dict[str, Any]) -> dict[str, Any]:
    decision = interrupt({
        "type": "answer_review",
        "message": "A human must review this response before it is released.",
        "question": state["question"],
        "draft_answer": state.get("answer", ""),
        "sources": state.get("retrieved_chunks", []),
        "options": ["approve", "reject"],
    })

    if not isinstance(decision, dict):
        return {
            "review_decision": "invalid",
            "needs_human_review": True,
        }

    action = decision.get("action")

    if action == "approve":
        revised_answer = decision.get("revised_answer")

        return {
            "answer": (
                revised_answer.strip()
                if isinstance(revised_answer, str) and revised_answer.strip()
                else state.get("answer", "")
            ),
            "review_decision": "approved",
            "needs_human_review": False,
        }

    return {
        "review_decision": "rejected",
        "needs_human_review": True,
        "answer": (
            "This response was not approved and has been held for review."
        ),
    }