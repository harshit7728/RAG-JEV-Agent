from langgraph.graph import END, START, StateGraph

from app.graph.approval import human_review
from app.graph.nodes import (
    MAX_ATTEMPTS,
    assess_evidence,
    produce_answer,
    retrieve_context,
    rewrite_search_query,
    route_query,
)
from app.graph.state import RAGState


def after_routing(state: RAGState) -> str:
    if state.get("intent") in {"greeting", "unsupported"}:
        return "answer"
    return "retrieve"


def after_evidence_check(state: RAGState) -> str:
    if state.get("evidence_sufficient", False):
        return "answer"

    if state.get("attempts", 0) < MAX_ATTEMPTS:
        return "rewrite"

    return "answer"


def after_answer(state: RAGState) -> str:
    if state.get("needs_human_review", False):
        return "review"
    return "end"


def build_graph(checkpointer=None):
    builder = StateGraph(RAGState)

    builder.add_node("route", route_query)
    builder.add_node("retrieve", retrieve_context)
    builder.add_node("assess", assess_evidence)
    builder.add_node("rewrite", rewrite_search_query)
    builder.add_node("answer", produce_answer)
    builder.add_node("review", human_review)

    builder.add_edge(START, "route")

    builder.add_conditional_edges(
        "route",
        after_routing,
        {"retrieve": "retrieve", "answer": "answer"},
    )

    builder.add_edge("retrieve", "assess")

    builder.add_conditional_edges(
        "assess",
        after_evidence_check,
        {"rewrite": "rewrite", "answer": "answer"},
    )

    builder.add_edge("rewrite", "retrieve")

    builder.add_conditional_edges(
        "answer",
        after_answer,
        {"review": "review", "end": END},
    )

    builder.add_edge("review", END)

    return builder.compile(checkpointer=checkpointer)