import json
import re
from typing import Literal

from langgraph.types import Command, Send, interrupt

from core.graph.research.prompts import PLLANER_PROMPT, current_date_context
from core.graph.research.state import ResearchState
from core.llm.manager import LLMManager
from shared.logger import logger
from utils.retries import with_retry

def create_planner_agent(llm: LLMManager):
    def planner_agent(
        state: ResearchState,
    ) -> Command[Literal["plan_review"]]:
        """Breaks the main question into sub-questions with one LLM call,
        then hands off to plan_review for human approval. Kept as its own
        node (rather than calling interrupt() here directly) because
        LangGraph reruns an interrupted node from the top on every resume --
        putting the expensive LLM call before interrupt() would re-invoke it
        (and could silently swap out the plan the user already approved) on
        every approve/reject/modify resume."""
        q = state.get("question", "")
        if isinstance(q, list):
            q = "".join(str(item) for item in q)

        questions = [q]
        try:
            raw = with_retry(max_attempts=2)(llm.model.invoke)(PLLANER_PROMPT(q))
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

        return Command(update={"question": q, "sub_questions": questions}, goto="plan_review")

    return planner_agent


def plan_review(state: ResearchState) -> Command[Literal["dispatch_search", "supervisor"]]:
    """Pauses for human review (approve / reject / modify) of the plan
    planner_agent already generated, then hands off to parallel search.
    Deliberately does no LLM work of its own -- rerunning this node from the
    top on resume just re-reads the already-checkpointed sub_questions."""
    q = state.get("question", "")
    questions = state.get("sub_questions") or [q]

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

    return Command(
        update={"sub_questions": questions, "pending_questions": questions},
        goto="dispatch_search",
    )


def dispatch_search(state: ResearchState) -> Command[Literal["search_agent"]]:
    """Map step: dynamic parallel fan-out sending sub-questions to search_agent.

    Reads `pending_questions` (this round's work) rather than `sub_questions`
    (the full cumulative plan) -- coverage_agent.py reuses this same node for
    an adaptive follow-up round, and only wants to dispatch the new
    gap-filling questions, not re-search everything from scratch.
    """
    sub_qs = (
        state.get("pending_questions")
        or state.get("sub_questions")
        or [state.get("question", "")]
    )
    sends = [Send("search_agent", {"question": sq, "messages": []}) for sq in sub_qs]
    return Command(goto=sends)
