# tests/test_research_graph.py
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command
from core.graph.research.supervisor import supervisor
from core.graph.research.state import ResearchState

def mock_planner(state):
    return Command(update={"sub_questions": ["q1"]})

def mock_dispatch(state):
    return Command(update={"search_results": ["mocked findings"]}, goto="supervisor")

def mock_search(state):
    return Command(update={"search_results": ["mocked findings"]}, goto="supervisor")

def mock_writer(state):
    return Command(update={"draft": "mocked draft"}, goto="supervisor")

def mock_reviewer(state):
    # Simulate a clean review — increment revision_count so supervisor can finalise
    return Command(update={"revision_count": state.get("revision_count", 0) + 1}, goto="supervisor")

def build_test_graph():
    builder = StateGraph(ResearchState)
    builder.add_node("supervisor", supervisor)
    builder.add_node("planner_agent", mock_planner)
    builder.add_node("dispatch_search", mock_dispatch)
    builder.add_node("search_agent", mock_search)
    builder.add_node("writer_agent", mock_writer)
    builder.add_node("reviewer_agent", mock_reviewer)
    builder.add_edge(START, "supervisor")
    builder.add_edge("planner_agent", "dispatch_search")
    return builder.compile()

def test_full_graph_reaches_end_with_final_answer():
    test_graph = build_test_graph()
    # Start from having search results + draft ready, revision_count=0 → goes to reviewer → finalise
    result = test_graph.invoke({
        "question": "irrelevant",
        "sub_questions": ["q1"],
        "search_results": ["mocked findings"],
        "draft": "mocked draft",
        "revision_count": 0,
        "messages": [],
    })
    assert "mocked draft" in result["final_answer"]