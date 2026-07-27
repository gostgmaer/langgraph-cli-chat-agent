# core/graph/research/team_subgraph.py (illustrative -- build only when you add a second team)
from langgraph.graph import StateGraph, START
from core.graph.research.state import ResearchState
from core.graph.research.supervisor import supervisor
from core.graph.research.search_agent import search_agent
from core.graph.research.writer_agent import writer_agent

def build_research_team():
    builder = StateGraph(ResearchState)
    builder.add_node("supervisor", supervisor)
    builder.add_node("search_agent", search_agent)
    builder.add_node("writer_agent", writer_agent)
    builder.add_edge(START, "supervisor")
    return builder.compile()  # no checkpointer here -- the parent's checkpointer governs the whole run

research_team = build_research_team()
# a hypothetical top-level graph, using research_team as one node among several teams
from langgraph.graph import StateGraph, START, END
from core.graph.research.state import ResearchState
from core.graph.research.team_subgraph import research_team

def build_top_level_graph(checkpointer):
    builder = StateGraph(ResearchState)
    builder.add_node("research_team", research_team)  # a compiled graph used directly as a node
    builder.add_edge(START, "research_team")
    builder.add_edge("research_team", END)
    return builder.compile(checkpointer=checkpointer)  # pass the same AsyncSqliteSaver as everywhere else