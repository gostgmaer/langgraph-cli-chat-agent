# tests/test_research_nodes.py
from core.graph.research.supervisor import supervisor

def test_supervisor_routes_to_search_when_no_results():
    state = {"question": "x", "search_results": "", "draft": "", "final_answer": "", "messages": []}
    cmd = supervisor(state)
    assert cmd.goto == "search_agent"

def test_supervisor_routes_to_writer_when_results_but_no_draft():
    state = {"question": "x", "search_results": "found stuff", "draft": "", "final_answer": "", "messages": []}
    cmd = supervisor(state)
    assert cmd.goto == "writer_agent"

def test_supervisor_finishes_when_draft_present():
    state = {"question": "x", "search_results": "found stuff", "draft": "polished", "final_answer": "", "messages": []}
    cmd = supervisor(state)
    assert cmd.goto == "__end__"
    assert cmd.update["final_answer"] == "polished"