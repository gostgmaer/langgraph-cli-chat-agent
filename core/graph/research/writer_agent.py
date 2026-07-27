from typing import Literal

from langchain_core.messages import HumanMessage
from langgraph.types import Command

from config.enums import LLMProvider
from core.graph.research.state import ResearchState
from core.graph.research.prompts import WRITER_AGENT_PROMPT
from core.llm.manager import LLMManager
from core.llm.models import SupportedModel

_llm = LLMManager(
    provider=LLMProvider.GOOGLE, model_name=SupportedModel.GEMINI_3_1_FLASH_LITE
)


async def writer_agent(state: ResearchState) -> Command[Literal["supervisor"]]:
    findings = state.get("search_results", "")
    if isinstance(findings, list):
        findings = "\n".join(str(f) for f in findings)
    
    question = state.get("question", "")
    if isinstance(question, list):
        question = "".join(str(q) for q in question)

    response = await _llm.ainvoke(
        f"{WRITER_AGENT_PROMPT}\n\nQuestion: {question}\n\nFindings:\n{findings}"
    )
    
    draft = response.content
    if isinstance(draft, list):
        draft = "".join(b.get("text", "") if isinstance(b, dict) else str(b) for b in draft)

    return Command(
        update={
            "draft": str(draft),
            "messages": [HumanMessage(content=str(draft), name="writer_agent")],
        },
        goto="supervisor",
    )
