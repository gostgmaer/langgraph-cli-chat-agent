import json
import re
from typing import Literal

from langgraph.types import Command, Send, interrupt

from core.graph.research.prompts import PLLANER_PROMPT, current_date_context
from core.graph.research.state import ResearchState
from core.llm.manager import LLMManager
from shared.logger import logger

_llm = LLMManager()


def planner_agent(
    state: ResearchState,
) -> Command[Literal["dispatch_search", "supervisor"]]:
    """Breaks the main question into sub-questions, then pauses for human
    review (approve / reject / modify) before handing off to parallel search."""
    q = state.get("question", "")
    if isinstance(q, list):
        q = "".join(str(item) for item in q)

    questions = [q]
    try:
        # A manual JSON-instruction + regex-parse, rather than
        # with_structured_output(), matches what reviewer_agent already
        # does -- structured-output tool schemas aren't reliably honored
        # by every provider/model (e.g. local/cloud Ollama models).
        raw = _llm.model.invoke(PLLANER_PROMPT(q))
        # Some models/providers (e.g. certain Gemini variants) return
        # content as a list of content blocks rather than a plain string --
        # extract the text instead of stringifying the whole block list.
        if isinstance(raw.content, list):
            raw_text = "".join(
                b.get("text", "") if isinstance(b, dict) else str(b)
                for b in raw.content
            )
        else:
            raw_text = str(raw.content)
        match = re.search(r"\{.*\}", raw_text, re.DOTALL)
        if match:
            parsed = json.loads(match.group())
            # PLLANER_PROMPT's schema is {"research_plan": [{"query": "...", ...}]};
            # fall back to a flat {"sub_questions": [...]} for robustness against
            # future prompt tweaks.
            research_plan = parsed.get("research_plan")
            if isinstance(research_plan, list) and research_plan:
                parsed_questions = [
                    str(task.get("query", task)) if isinstance(task, dict) else str(task)
                    for task in research_plan
                ]
            else:
                parsed_questions = parsed.get("sub_questions")

            if isinstance(parsed_questions, list) and parsed_questions:
                questions = [str(sq) for sq in parsed_questions]
            else:
                logger.warning(
                    "Planner agent got no usable research tasks from model output; "
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

    decision = (
        interrupt({"type": "plan_review", "question": q, "sub_questions": questions})
        or {}
    )
    action = decision.get("action", "approve")

    if action == "reject":
        return Command(
            update={"final_answer": "Research cancelled by the user before execution."},
            goto="supervisor",
        )

    if action == "modify":
        modified = decision.get("sub_questions")
        if isinstance(modified, list) and modified:
            questions = [str(sq) for sq in modified]

    return Command(update={"sub_questions": questions}, goto="dispatch_search")


def dispatch_search(state: ResearchState) -> Command:
    """Map step: dynamic parallel fan-out sending sub-questions to search_agent."""
    sub_qs = state.get("sub_questions") or [state.get("question", "")]
    sends = [Send("search_agent", {"question": sq, "messages": []}) for sq in sub_qs]
    return Command(goto=sends)
