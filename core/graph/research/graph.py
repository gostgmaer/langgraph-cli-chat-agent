from langgraph.types import Send
from core.graph.research.state import ResearchState
from langgraph.types import Command
def dispatch_search(state: ResearchState) -> list[Send]:
    """Fan out: one independent search_agent invocation per sub-question.

    Returning a list of Send(...) from a node is how LangGraph triggers
    dynamic parallel execution -- the number of branches is determined
    at runtime by len(sub_questions), not hardcoded in the graph shape.
    """
    return [
        Send("search_agent", {"question": sub_q, "messages": []})
        for sub_q in state["sub_questions"]
    ]
