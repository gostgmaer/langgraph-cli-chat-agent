from langgraph.graph import StateGraph, START
from langgraph.checkpoint.base import BaseCheckpointSaver

from core.graph.research.state import ResearchState
from core.graph.research.supervisor import supervisor
from core.graph.research.planner_agent import create_planner_agent, dispatch_search, plan_review
from core.graph.research.search_agent import create_search_agent
from core.graph.research.writer_agent import create_writer_agent
from core.graph.research.reviewer_agent import create_reviewer_agent
from core.graph.research.coverage_agent import create_coverage_assessor
from core.llm.manager import LLMManager


class ResearchGraphBuilder:
    """Production-grade Multi-Agent Research StateGraph Builder."""

    def __init__(self, llm: LLMManager, checkpointer: BaseCheckpointSaver = None):
        self._llm = llm
        self._checkpointer = checkpointer

    def build(self):
        builder = StateGraph(ResearchState)

        builder.add_node("supervisor", supervisor)
        builder.add_node("planner_agent", create_planner_agent(self._llm))
        builder.add_node("plan_review", plan_review)
        builder.add_node("dispatch_search", dispatch_search)
        builder.add_node("search_agent", create_search_agent(self._llm))
        builder.add_node("assess_coverage", create_coverage_assessor(self._llm))
        builder.add_node("writer_agent", create_writer_agent(self._llm))
        builder.add_node("reviewer_agent", create_reviewer_agent(self._llm))

        builder.add_edge(START, "supervisor")

        if self._checkpointer:
            return builder.compile(checkpointer=self._checkpointer)
        return builder.compile()
