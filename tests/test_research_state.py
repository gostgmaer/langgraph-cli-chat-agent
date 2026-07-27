from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage

def test_add_messages_appends_not_overwrites():
    existing = [HumanMessage(content="first", name="search_agent")]
    incoming = [HumanMessage(content="second", name="writer_agent")]
    merged = add_messages(existing, incoming)
    assert len(merged) == 2
    assert merged[0].content == "first"
    assert merged[1].content == "second"

def test_operator_add_concatenates_parallel_branch_results():
    import operator
    branch_a = ["result from sub-question 1"]
    branch_b = ["result from sub-question 2"]
    assert operator.add(branch_a, branch_b) == [
        "result from sub-question 1",
        "result from sub-question 2",
    ]