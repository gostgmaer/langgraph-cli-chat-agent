
from typing import Annotated

from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage
from typing_extensions import TypedDict


class ResearchState(TypedDict):
    """Share state for research operations"""
    messages: Annotated[list[AnyMessage],add_messages]
    question: str
    search_results:str
    draft:str
    final_answer:str


