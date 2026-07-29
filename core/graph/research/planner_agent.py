import json
import re
from typing import Literal

from langgraph.types import Command, Send, interrupt

from core.graph.research.prompts import PLLANER_PROMPT, current_date_context
from core.graph.research.state import ResearchState
from core.llm.manager import LLMManager
from shared.logger import logger

def create_planner_agent(llm: LLMManager):
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
            raw = llm.model.invoke(PLLANER_PROMPT(q))
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

    return planner_agent


def dispatch_search(state: ResearchState) -> Command[Literal["search_agent"]]:
    """Map step: dynamic parallel fan-out sending sub-questions to search_agent."""
    sub_qs = state.get("sub_questions") or [state.get("question", "")]
    sends = [Send("search_agent", {"question": sq, "messages": []}) for sq in sub_qs]
    return Command(goto=sends)
