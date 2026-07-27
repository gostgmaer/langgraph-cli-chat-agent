from typing import Literal
from langgraph.types import Command
from langgraph.graph import END
from core.graph.research.state import ResearchState

MAX_REVISIONS = 2


def supervisor(
    state: ResearchState,
) -> Command[Literal["planner_agent", "writer_agent", "reviewer_agent", "__end__"]]:
    """Production supervisor with step budgets, parallel search routing, and reviewer loop."""
    revision_count = state.get("revision_count", 0)
    search_results = state.get("search_results") or []
    draft = state.get("draft", "")
    final_answer = state.get("final_answer", "")

    # 1. Already has a final answer — done
    if final_answer:
        return Command(goto=END)

    # 2. Budget Guard — too many revisions
    if revision_count > MAX_REVISIONS:
        return Command(
            update={"final_answer": draft or "Research completed (max revisions reached)."},
            goto=END,
        )

    # 3. No search yet — go plan & search
    if not search_results:
        return Command(goto="planner_agent")

    # 4. Have results but no draft yet — write
    if search_results and not draft:
        return Command(goto="writer_agent")

    # 5. Have draft, not yet reviewed (revision_count == 0 means no review has happened)
    if draft and revision_count == 0:
        return Command(goto="reviewer_agent")

    # 6. Reviewed at least once — finalise
    return Command(
        update={
            "final_answer": draft,
            "search_results": [],
            "sub_questions": [],
            "draft": "",
            "revision_count": 0,
        },
        goto=END,
    )
