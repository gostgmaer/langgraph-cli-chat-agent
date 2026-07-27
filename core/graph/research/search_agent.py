from typing import Literal
from langchain_core.messages import HumanMessage
from langgraph.types import Command

from config.enums import LLMProvider
from core.graph.research.state import ResearchState
from core.graph.research.prompts import SEARCH_AGENT_PROMPT
from core.llm.manager import LLMManager
from core.llm.models import SupportedModel
from core.tools.search import get_google_search
from core.tools.news import get_news

search_tools = [get_google_search, get_news]
_llm = LLMManager(
    provider=LLMProvider.GOOGLE, model_name=SupportedModel.GEMINI_3_1_FLASH_LITE
)
_llm_with_tools = _llm.bind_tools(search_tools)


async def search_agent(state: ResearchState) -> Command[Literal["supervisor"]]:
    messages = [
        {"role": "system", "content": SEARCH_AGENT_PROMPT},
        {"role": "user", "content": state["question"]},
    ]
    response = await _llm_with_tools.ainvoke(messages)

    tool_outputs = []
    for call in getattr(response, "tool_calls", []) or []:
        tool_fn = next(t for t in search_tools if t.name == call["name"])
        result = (
            await tool_fn.ainvoke(call["args"])
            if call["name"] == "get_news"
            else tool_fn.invoke(call["args"])
        )
        tool_outputs.append(f"[{call['name']}] {result}")

    if tool_outputs:
        tool_messages = [
            {"role": "tool", "tool_call_id": tc["id"], "content": str(out)}
            for tc, out in zip(getattr(response, "tool_calls", []), tool_outputs)
        ]
        
        # Build prompt history explicitly with BaseMessage / dict conversion
        history = [
            {"role": "system", "content": SEARCH_AGENT_PROMPT},
            {"role": "user", "content": str(state["question"])},
            response,
        ] + tool_messages

        followup = await _llm_with_tools.ainvoke(history)
        summary = followup.content
    else:
        summary = response.content

    if isinstance(summary, list):
        summary = "".join(b.get("text", "") if isinstance(b, dict) else str(b) for b in summary)

    return Command(
        update={
            "search_results": [str(summary)],
            "messages": [HumanMessage(content=str(summary), name="search_agent")],
        },
        goto="supervisor",
    )
