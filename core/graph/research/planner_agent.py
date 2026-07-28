from typing import Literal

from langgraph.types import Command, Send
from pydantic import BaseModel, Field
from config.enums import LLMProvider
from core.graph.research.state import ResearchState
from core.llm.manager import LLMManager
from core.llm.models import SupportedModel


class SubQuestions(BaseModel):
    sub_questions: list[str] = Field(
        description="7-10 focused, independently-searchable sub-questions that together cover the main question."
    )


_llm = LLMManager()
_planner_llm = _llm.model.with_structured_output(SubQuestions)


def planner_agent(state: ResearchState) -> Command[Literal["dispatch_search"]]:
    """Breaks main question into sub-questions for parallel search execution."""
    q = state.get("question", "")
    if isinstance(q, list):
        q = "".join(str(item) for item in q)

    try:
        result = _planner_llm.invoke(
            f"Break this research topic into 7-10 focused sub-questions for parallel web search:\n\n{q}"
        )
        questions = result.sub_questions if result and hasattr(result, "sub_questions") else [q]
    except Exception:
        questions = [q]

    return Command(update={"sub_questions": questions})


def dispatch_search(state: ResearchState) -> Command:
    """Map step: dynamic parallel fan-out sending sub-questions to search_agent."""
    sub_qs = state.get("sub_questions") or [state.get("question", "")]
    sends = [
        Send("search_agent", {"question": sq, "messages": []})
        for sq in sub_qs
    ]
    return Command(goto=sends)

