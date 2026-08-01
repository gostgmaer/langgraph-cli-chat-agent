import json
import re
from typing import Literal

from langgraph.types import Command

from core.graph.research.prompts import COVERAGE_PROMPT
from core.graph.research.state import ResearchState
from core.llm.manager import LLMManager
from shared.logger import logger
from utils.retries import with_retry

# Adaptive research is capped at 1 extra round -- bounds worst-case cost to
# 2x the search phase instead of letting the planner/writer loop
# indefinitely chasing diminishing-returns follow-up questions.
MAX_RESEARCH_ROUNDS = 1

MAX_FOLLOW_UPS = 3


def _extract_text(content) -> str:
    if isinstance(content, list):
        return "".join(b.get("text", "") if isinstance(b, dict) else str(b) for b in content)
    return str(content)


def create_coverage_assessor(llm: LLMManager):
    def assess_coverage(
        state: ResearchState,
    ) -> Command[Literal["dispatch_search", "writer_agent"]]:
        """After a search round, decides whether the findings have a real
        gap worth one more targeted search round, or whether it's time to
        write. Runs at most MAX_RESEARCH_ROUNDS times per research turn."""
        research_rounds = state.get("research_rounds", 0)
        if research_rounds >= MAX_RESEARCH_ROUNDS:
            return Command(goto="writer_agent")

        question = state.get("question", "")
        if isinstance(question, list):
            question = "".join(str(q) for q in question)

        sub_questions = state.get("sub_questions") or []
        findings = state.get("search_results") or []
        findings_text = "\n\n".join(str(f) for f in findings)

        has_gaps = False
        follow_ups: list[str] = []
        try:
            raw = with_retry(max_attempts=2)(llm.model.invoke)(
                COVERAGE_PROMPT(question, sub_questions, findings_text)
            )
            raw_text = _extract_text(raw.content)
            match = re.search(r"\{.*\}", raw_text, re.DOTALL)
            if match:
                parsed = json.loads(match.group())
                has_gaps = bool(parsed.get("has_gaps", False))
                follow_ups = [
                    str(q) for q in (parsed.get("follow_up_questions") or []) if str(q).strip()
                ][:MAX_FOLLOW_UPS]
        except Exception:
            logger.exception(
                "Coverage assessor failed; proceeding to writing without a follow-up round."
            )

        if has_gaps and follow_ups:
            return Command(
                update={
                    "sub_questions": sub_questions + follow_ups,
                    "pending_questions": follow_ups,
                    "research_rounds": research_rounds + 1,
                },
                goto="dispatch_search",
            )

        return Command(goto="writer_agent")

    return assess_coverage
