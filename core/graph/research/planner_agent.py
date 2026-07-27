from typing import Literal

from langgraph.types import Command
from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage, HumanMessage
from config.enums import LLMProvider
from core.graph.research.state import ResearchState
from core.graph.research.prompts import PLANNER_AGENT_PROMPT
from core.llm.manager import LLMManager
from core.llm.models import SupportedModel


class SubQuestions(BaseModel):
    sub_questions: list[str] = Field(
        description="List of sub-questions to be addressed"
        "2-4 focused, independently-searchable sub-questions "
        "that together cover the original question."
    )


_llm = LLMManager(
    provider=LLMProvider.GOOGLE, model_name=SupportedModel.GEMINI_3_1_FLASH_LITE
)
_planner_llm = _llm.model.with_structured_output(
    SubQuestions
)  # returns a bound chat model, not an LLMManager


def planner_agent(state: ResearchState) -> Command[Literal["dispatch_search"]]:
    result = _planner_llm.invoke(
        f"Break this question into 2-4 independent, web-searchable "
        f"sub-questions:\n\n{state['question']}"
    )
    return Command(
        update={"sub_questions": result.sub_questions}, goto="dispatch_search"
    )

