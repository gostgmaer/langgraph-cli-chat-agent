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
        description="True if the draft is fully supported by the research"
    )
    issues: list[str] = Field(
        default_factory=list, description="Specific unsupported claims, if any"
    )


_llm = LLMManager(
    provider=LLMProvider.GOOGLE, model_name=SupportedModel.GEMINI_3_1_FLASH_LITE
)
_reviewer_llm = _llm.model.with_structured_output(ConsistencyReview)


def reviewer_agent(
    state: ResearchState,
) -> Command[Literal["writer_agent", "supervisor"]]:
    findings = "\n".join(state["search_results"])
    review = _reviewer_llm.invoke(
        f"Research findings:\n{findings}\n\nDraft answer:\n{state['draft']}\n\n"
        f"Does the draft make any claim NOT supported by the findings?"
    )

    revision_count = state.get("revision_count", 0)
    if review.is_consistent or revision_count >= MAX_REVISIONS:
        return Command(goto="supervisor")

    feedback = "Revise to remove unsupported claims: " + "; ".join(review.issues)
    return Command(
        update={
            "revision_count": revision_count + 1,
            "question": state["question"] + f"\n\n[Reviewer feedback: {feedback}]",
        },
        goto="writer_agent",
    )
