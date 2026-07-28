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

    prompt = f"{WRITER_AGENT_PROMPT}\n\nQuestion: {question}\n\nFindings:\n{findings}"

    # Use astream so on_chat_model_stream events flow through subgraphs=True
    draft_parts = []
    async for chunk in _llm.model.astream(prompt):
        content = chunk.content
        if isinstance(content, str):
            draft_parts.append(content)
        elif isinstance(content, list):
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    draft_parts.append(block.get("text", ""))

    draft = "".join(draft_parts)

    return Command(
        update={
            "draft": draft,
            "messages": [HumanMessage(content=draft, name="writer_agent")],
        },
        goto="supervisor",
    )
