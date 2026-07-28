import json
import re
from typing import Literal

from langgraph.types import Command, Send

from core.graph.research.state import ResearchState
from core.llm.manager import LLMManager
from shared.logger import logger

_llm = LLMManager()


def planner_agent(state: ResearchState) -> Command[Literal["dispatch_search"]]:
    """Breaks main question into sub-questions for parallel search execution."""
    q = state.get("question", "")
    if isinstance(q, list):
        q = "".join(str(item) for item in q)

    questions = [q]
    try:
        # A manual JSON-instruction + regex-parse, rather than
        # with_structured_output(), matches what reviewer_agent already
        # does -- structured-output tool schemas aren't reliably honored
        # by every provider/model (e.g. local/cloud Ollama models).
        raw = _llm.model.invoke(
            "Break this research topic into 7-10 focused, independently "
            "web-searchable sub-questions that together cover it.\n\n"
            f"Topic: {q}\n\n"
            'Reply ONLY with a JSON object: {"sub_questions": ["...", "..."]}.'
        )
        raw_text = raw.content if isinstance(raw.content, str) else str(raw.content)
        match = re.search(r"\{.*\}", raw_text, re.DOTALL)
        if match:
            parsed = json.loads(match.group())
            parsed_questions = parsed.get("sub_questions")
            if isinstance(parsed_questions, list) and parsed_questions:
                questions = [str(sq) for sq in parsed_questions]
            else:
                logger.warning(
                    "Planner agent got no usable sub_questions from model output; "
                    "falling back to the original question."
                )
        else:
            logger.warning(
                "Planner agent found no JSON object in model output; "
                "falling back to the original question."
            )
    except Exception:
        logger.exception(
            "Planner agent failed to generate sub-questions; falling back to the original question."
        )

    return Command(update={"sub_questions": questions})


def dispatch_search(state: ResearchState) -> Command:
    """Map step: dynamic parallel fan-out sending sub-questions to search_agent."""
    sub_qs = state.get("sub_questions") or [state.get("question", "")]
    sends = [
        Send("search_agent", {"question": sq, "messages": []})
        for sq in sub_qs
    ]
    return Command(goto=sends)
