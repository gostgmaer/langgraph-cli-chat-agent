# ============================================================
# core/graph/state.py — LangGraph Agent State Schema
# ============================================================
# TODO: Define AgentState TypedDict or Pydantic model
# TODO: Include fields: messages, session_id, user_id
# TODO: Include fields: memory_summary, retrieved_docs
# TODO: Include fields: tool_calls, tool_results
# TODO: Include fields: current_node, error, metadata
# ============================================================



from typing import Annotated, TypedDict

from langgraph.graph.message import add_messages
from langgraph.graph import MessagesState
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    """Shared state flowing through the graph."""

    messages: Annotated[list[BaseMessage], add_messages]

class GraphState(MessagesState):
    """Shared state for the AI Agent."""
    pass