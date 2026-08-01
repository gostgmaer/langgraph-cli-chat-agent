# tests/test_research_nodes.py
from core.graph.research.supervisor import supervisor
from core.graph.research.coverage_agent import create_coverage_assessor, MAX_RESEARCH_ROUNDS

def test_supervisor_routes_to_planner_when_no_subquestions():
    state = {"question": "x", "sub_questions": [], "search_results": [], "draft": "", "final_answer": "", "messages": []}
    cmd = supervisor(state)
    assert cmd.goto == "planner_agent"

def test_supervisor_routes_to_coverage_check_when_results_but_no_draft():
    state = {"question": "x", "sub_questions": ["q1"], "search_results": ["found stuff"], "draft": "", "final_answer": "", "messages": []}
    cmd = supervisor(state)
    assert cmd.goto == "assess_coverage"

def test_supervisor_routes_to_reviewer_when_draft_present():
    state = {"question": "x", "sub_questions": ["q1"], "search_results": ["found stuff"], "draft": "polished", "final_answer": "", "messages": []}
    cmd = supervisor(state)
    assert cmd.goto == "reviewer_agent"

def test_assess_coverage_skips_llm_when_round_budget_exhausted():
    # No llm passed (None) -- this branch must return before ever touching it.
    assess_coverage = create_coverage_assessor(llm=None)
    state = {
        "question": "x",
        "sub_questions": ["q1"],
        "search_results": ["found stuff"],
        "research_rounds": MAX_RESEARCH_ROUNDS,
        "messages": [],
    }
    cmd = assess_coverage(state)
    assert cmd.goto == "writer_agent"