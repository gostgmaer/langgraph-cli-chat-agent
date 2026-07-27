# core/graph/research/supervisor.py — as it already exists in this repo
from typing import Literal
from langgraph.types import Command
from langgraph.graph import END
from core.graph.research.state import ResearchState

# END = "__end__"
def supervisor(
    state: ResearchState,
) -> Command[Literal["search_agent", "writer_agent", '"__end__"']]:
    if not state.get("search_results"):
        return Command(goto="search_agent")
    if not state.get("draft"):
        return Command(goto="writer_agent")
    return Command(update={"final_answer": state.get("draft")}, goto=END)
