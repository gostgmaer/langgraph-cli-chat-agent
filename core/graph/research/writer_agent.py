from typing import Literal

from langgraph.types import Command

from core.graph.research.state import ResearchState
from core.graph.research.prompts import WRITER_AGENT_PROMPT, current_date_context
from core.llm.manager import LLMManager
from shared.logger import logger

def create_writer_agent(llm: LLMManager):
    async def writer_agent(state: ResearchState) -> Command[Literal["supervisor"]]:
        findings = state.get("search_results", "")
        if isinstance(findings, list):
            findings = "\n".join(str(f) for f in findings)

        question = state.get("question", "")
        if isinstance(question, list):
            question = "".join(str(q) for q in question)

        prompt = (
            f"{WRITER_AGENT_PROMPT}\n\n{current_date_context()}\n\n"
            f"Question: {question}\n\nFindings:\n{findings}"
        )

        try:
            # Use astream so on_chat_model_stream events flow through subgraphs=True
            draft_parts = []
            async for chunk in llm.model.astream(prompt):
                content = chunk.content
                if isinstance(content, str):
                    draft_parts.append(content)
                elif isinstance(content, list):
                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "text":
                            draft_parts.append(block.get("text", ""))

            draft = "".join(draft_parts)
        except Exception:
            # A hung/failed writer-model call must not stall the whole graph.
            logger.exception("Writer agent failed for question: %s", question)
            draft = (
                "I wasn't able to generate a written answer due to a model error. "
                "Here is the raw research summary instead:\n\n" + str(findings)
            )

        # Not appended to `messages` here -- the draft may still be revised
        # by reviewer_agent. supervisor appends the one clean final answer
        # to `messages` once the whole research run actually completes.
        return Command(
            update={"draft": draft},
            goto="supervisor",
        )

    return writer_agent
