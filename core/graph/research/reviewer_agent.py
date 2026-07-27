from typing import Literal
from langgraph.types import Command
from pydantic import BaseModel, Field

from core.graph.research.state import ResearchState
from core.llm.manager import LLMManager
from config.enums import LLMProvider
from core.llm.models import SupportedModel

MAX_REVISIONS = 2


class ConsistencyReview(BaseModel):
    is_consistent: bool = Field(
        description="True if the draft is fully supported by the research findings."
    )
    issues: list[str] = Field(
        default_factory=list, description="Specific unsupported claims or inaccuracies, if any."
    )


_llm = LLMManager(
    provider=LLMProvider.GOOGLE, model_name=SupportedModel.GEMINI_3_1_FLASH_LITE
)
_reviewer_llm = _llm.model.with_structured_output(ConsistencyReview)


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
        review = _reviewer_llm.invoke(
            f"Research findings:\n{findings}\n\nDraft answer:\n{draft}\n\n"
            f"Does the draft make any claim NOT supported by the findings?"
        )
        is_consistent = review.is_consistent if review and hasattr(review, "is_consistent") else True
        issues = review.issues if review and hasattr(review, "issues") else []
    except Exception:
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
