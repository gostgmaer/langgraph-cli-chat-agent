import json
import re
from typing import Literal
from langgraph.types import Command

from core.graph.research.state import ResearchState
from core.llm.manager import LLMManager
from shared.logger import logger

MAX_REVISIONS = 2


_llm = LLMManager()


def reviewer_agent(
    state: ResearchState,
) -> Command[Literal["writer_agent", "supervisor"]]:
    """Fact-checker node: verifies draft consistency against aggregated search results."""
    raw_findings = state.get("search_results", [])
    if isinstance(raw_findings, list):
        findings = "\n".join(str(f) for f in raw_findings)
    else:
        findings = str(raw_findings)

    draft = str(state.get("draft", ""))

    try:
        # Use plain LLM with explicit JSON instruction to avoid raw JSON leaking into state messages
        raw = _llm.model.invoke(
            f"Research findings:\n{findings}\n\nDraft answer:\n{draft}\n\n"
            f"Reply ONLY with a JSON object: {{\"is_consistent\": true/false, \"issues\": [\"list of issues if any\"]}}.\n"
            f"Set is_consistent=true if draft is fully supported. Set false and list issues if not."
        )
        # Some models/providers (e.g. certain Gemini variants) return
        # content as a list of content blocks rather than a plain string --
        # extract the text instead of stringifying the whole block list.
        if isinstance(raw.content, list):
            raw_text = "".join(
                b.get("text", "") if isinstance(b, dict) else str(b) for b in raw.content
            )
        else:
            raw_text = str(raw.content)

        match = re.search(r'\{.*\}', raw_text, re.DOTALL)
        if match:
            parsed = json.loads(match.group())
            is_consistent = bool(parsed.get("is_consistent", True))
            issues = parsed.get("issues", [])
        else:
            logger.warning("Reviewer agent found no JSON object in model output; treating draft as consistent.")
            is_consistent = True
            issues = []
    except Exception:
        logger.exception("Reviewer agent failed to review draft; treating draft as consistent.")
        is_consistent = True
        issues = []

    revision_count = state.get("revision_count", 0)
    if is_consistent or revision_count >= MAX_REVISIONS:
        # Mark as reviewed so supervisor can finalise
        return Command(update={"revision_count": revision_count + 1}, goto="supervisor")

    feedback = "Revise to remove unsupported claims: " + "; ".join(issues)
    q = state.get("question", "")
    return Command(
        update={
            "revision_count": revision_count + 1,
            "question": str(q) + f"\n\n[Reviewer feedback: {feedback}]",
            "draft": "",  # Clear draft so writer generates revised version
        },
        goto="writer_agent",
    )
