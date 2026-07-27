# tests/test_research_graph.py
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command
from core.graph.research import supervisor
from core.graph.research.state import ResearchState

def mock_search(state):
    return Command(update={"search_results": ["mocked findings"]}, goto="supervisor")

def mock_writer(state):
    return Command(update={"draft": "mocked draft"}, goto="supervisor")

def build_test_graph():
    builder = StateGraph(ResearchState)
    builder.add_node("supervisor", supervisor)
    builder.add_node("search_agent", mock_search)
    builder.add_node("writer_agent", mock_writer)
    builder.add_edge(START, "supervisor")
    return builder.compile()

def test_full_graph_reaches_end_with_final_answer():
    test_graph = build_test_graph()
    result = test_graph.invoke({"question": "irrelevant", "search_results": "", "draft": "", "final_answer": "", "messages": []})
    assert result["final_answer"] == "mocked draft"