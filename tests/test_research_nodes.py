# tests/test_research_nodes.py
from core.graph.research.supervisor import supervisor

def test_supervisor_routes_to_planner_when_no_subquestions():
    state = {"question": "x", "sub_questions": [], "search_results": [], "draft": "", "final_answer": "", "messages": []}
    cmd = supervisor(state)
    assert cmd.goto == "planner_agent"

def test_supervisor_routes_to_writer_when_results_but_no_draft():
    state = {"question": "x", "sub_questions": ["q1"], "search_results": ["found stuff"], "draft": "", "final_answer": "", "messages": []}
    cmd = supervisor(state)
    assert cmd.goto == "writer_agent"

def test_supervisor_routes_to_reviewer_when_draft_present():
    state = {"question": "x", "sub_questions": ["q1"], "search_results": ["found stuff"], "draft": "polished", "final_answer": "", "messages": []}
    cmd = supervisor(state)
    assert cmd.goto == "reviewer_agent"