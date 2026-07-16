# ============================================================
# core/graph/router.py — Conditional Edge Router
# ============================================================
# TODO: Define routing function that inspects agent state
# TODO: Route to `tool_node` if tool_calls are present
# TODO: Route to `rag_node` if RAG context needed
# TODO: Route to `planner_node` if complex task detected
# TODO: Route to `END` when response is final
# ============================================================
# core/graph/router.py

from core.graph.state import GraphState


def route_after_chatbot(
    state: GraphState,
) -> str:
    """Determine the next node after the chatbot."""

    return state["route"]