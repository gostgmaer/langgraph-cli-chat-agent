from typing import Annotated, TypedDict

from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage


def _accumulate_search_results(existing: list[str] | None, new: list[str] | None) -> list[str]:
    """Concatenate non-empty writes (needed for parallel Send() fan-in from
    search_agent); an empty-list write is treated as an explicit reset,
    since plain operator.add can never clear this field (concatenating
    with [] is a no-op), which left stale results from a prior /research
    turn visible to the next one."""
    if not new:
        return []
    return (existing or []) + new


class ResearchState(TypedDict, total=False):
    """Shared state for production-grade research operations."""
    messages: Annotated[list[AnyMessage], add_messages]
    question: str
    sub_questions: list[str]
    search_results: Annotated[list[str], _accumulate_search_results]
    draft: str
    revision_count: int
    final_answer: str

