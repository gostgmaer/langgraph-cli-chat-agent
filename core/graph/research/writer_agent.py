from langchain_core.messages import HumanMessage
from typing import Literal

from langgraph.types import Command
from config.enums import LLMProvider
from core.graph.research.state import ResearchState
from core.graph.research.prompts import WRITER_AGENT_PROMPT
from core.llm.manager import LLMManager
from core.llm.models import SupportedModel
from langgraph.types import Command, interrupt

_llm = LLMManager(
    provider=LLMProvider.GOOGLE, model_name=SupportedModel.GEMINI_3_1_FLASH_LITE
)


async def writer_agent(state: ResearchState) -> Command[Literal["supervisor"]]:
    findings = "\n".join(state["search_results"])
    response = await _llm.ainvoke(
        f"{WRITER_AGENT_PROMPT}\n\nQuestion: {state['question']}\n\nFindings:\n{findings}"
    )
    draft = response.content

    decision = interrupt({"draft_for_review": draft, "action": "approve_or_reject"})

    if decision.get("approved"):
        return Command(update={"draft": draft}, goto="supervisor")

    # Human rejected -- loop back to the Writer with their feedback folded
    # into the question so the next attempt addresses it directly.
    return Command(
        update={
            "question": state["question"]
            + f"\n\n[Human feedback: {decision.get('feedback', '')}]"
        },
        goto="writer_agent",
    )
