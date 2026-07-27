from langgraph.graph import StateGraph, START
from langgraph.checkpoint.base import BaseCheckpointSaver

from core.graph.research.state import ResearchState
from core.graph.research.supervisor import supervisor
from core.graph.research.planner_agent import planner_agent, dispatch_search
from core.graph.research.search_agent import search_agent
from core.graph.research.writer_agent import writer_agent
from core.graph.research.reviewer_agent import reviewer_agent


class ResearchGraphBuilder:
    """Production-grade Multi-Agent Research StateGraph Builder."""

    def __init__(self, checkpointer: BaseCheckpointSaver = None):
        self._checkpointer = checkpointer

    def build(self):
        builder = StateGraph(ResearchState)

        # 1. Add All Specialized Agents
        builder.add_node("supervisor", supervisor)
        builder.add_node("planner_agent", planner_agent)
        builder.add_node("dispatch_search", dispatch_search)
        builder.add_node("search_agent", search_agent)
        builder.add_node("writer_agent", writer_agent)
        builder.add_node("reviewer_agent", reviewer_agent)

        # 2. Add Routing Edges
        builder.add_edge(START, "supervisor")
        # Explicit edges so LangGraph can validate the full graph topology
        builder.add_edge("planner_agent", "dispatch_search")

        if self._checkpointer:
            return builder.compile(checkpointer=self._checkpointer)
        return builder.compile()
