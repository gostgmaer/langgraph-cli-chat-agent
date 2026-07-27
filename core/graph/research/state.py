import operator
from typing import Annotated, TypedDict

from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage


class ResearchState(TypedDict, total=False):
    """Shared state for production-grade research operations."""
    messages: Annotated[list[AnyMessage], add_messages]
    question: str
    sub_questions: list[str]
    search_results: Annotated[list[str], operator.add]
    draft: str
    revision_count: int
    final_answer: str

