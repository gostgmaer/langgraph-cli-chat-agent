from traceback import StackSummary

from langchain_core.messages import SystemMessage, HumanMessage
from config.enums import LLMProvider
from core.graph.research.state import ResearchState
from core.graph.research.prompts import SEARCH_AGENT_PROMPT
from core.llm.manager import LLMManager
from core.llm.models import SupportedModel
from core.tools.search import get_google_search
from core.tools.news import get_news
from typing import Literal
from langgraph.types import Command

search_tools = [get_google_search, get_news]
_llm = LLMManager(
    provider=LLMProvider.GOOGLE, model_name=SupportedModel.GEMINI_3_1_FLASH_LITE
)
_llm_with_tools = _llm.bind_tools(
    search_tools
)  # returns a bound chat model, not an LLMManager

async def search_agent(state: ResearchState) -> Command[Literal["supervisor"]]:
    # ... same tool-calling logic as before to produce `summary` ...
    return Command(
        update={
            "search_results": [StackSummary],  # one-element list; operator.add concatenates branches
            "messages": [HumanMessage(content=summary, name="search_agent")],
        },
        goto="supervisor",
    )   

# async def search_agent(state: ResearchState) -> Command[Literal["supervisor"]]:
#     messages = [
#         {"role": "user", "content": state["question"]},
#         {"role": "system", "content": SEARCH_AGENT_PROMPT},
#     ]
#     response = await _llm_with_tools.ainvoke(messages)

#     tool_outputs = []
#     for call in getattr(response, "tool_calls", []) or []:
#         tool_fn = next(t for t in search_tools if t.name == call["name"])
#         result = (
#             await tool_fn.ainvoke(call["args"])
#             if call["name"] == "get_news"
#             else tool_fn.invoke(call["args"])
#         )
#         tool_outputs.append(f"[{call['name']}] {result}")

#     if tool_outputs:
#         followup = await _llm_with_tools.ainvoke(
#             messages
#             + [response]
#             + [
#                 {"role": "tool", "tool_call_id": tc["id"], "content": out}
#                 for tc, out in zip(response.tool_calls, tool_outputs)
#             ]
#         )
#         summary = followup.content
#     else:
#         summary = response.content

#     return Command(
#         update={
#             "search_results": summary,
#             "messages": [HumanMessage(content=summary, name="search_agent")],
#         },
#         goto="supervisor",
#     )
