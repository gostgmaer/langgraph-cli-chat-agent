from typing import Literal
from langgraph.types import Command

from core.graph.research.state import ResearchState
from core.graph.research.prompts import SEARCH_AGENT_PROMPT, current_date_context
from core.llm.manager import LLMManager
from core.tools.search import get_google_search
from core.tools.news import get_news
from core.tools.webpage import get_page_content
from core.tools.academic import get_academic_search
from shared.logger import logger
from utils.retries import async_retry

search_tools = [get_google_search, get_news, get_page_content, get_academic_search]
# Tools with a genuinely async implementation -- everything else is sync and
# goes through tool_fn.invoke() directly.
ASYNC_TOOL_NAMES = {"get_news", "get_page_content"}
# 1 extra round -- typically: round 1 searches, round 2 either refines the
# query (empty/insufficient results) or fetches the full text of the most
# promising result via get_page_content.
MAX_TOOL_ROUNDS = 1


def _extract_text(content) -> str:
    if isinstance(content, list):
        return "".join(b.get("text", "") if isinstance(b, dict) else str(b) for b in content)
    return str(content)


def create_search_agent(llm: LLMManager):
    llm_with_tools = llm.bind_tools(search_tools)

    async def search_agent(state: ResearchState) -> Command[Literal["supervisor"]]:
        question = state["question"]
        history = [
            {"role": "system", "content": f"{SEARCH_AGENT_PROMPT}\n\n{current_date_context()}"},
            {"role": "user", "content": question},
        ]

        try:
            all_tool_outputs = []
            response = None

            for _ in range(MAX_TOOL_ROUNDS + 1):
                response = await async_retry(llm_with_tools.ainvoke, history)
                calls = getattr(response, "tool_calls", []) or []
                if not calls:
                    break

                history = history + [response]
                for call in calls:
                    tool_fn = next(t for t in search_tools if t.name == call["name"])
                    result = (
                        await tool_fn.ainvoke(call["args"])
                        if call["name"] in ASYNC_TOOL_NAMES
                        else tool_fn.invoke(call["args"])
                    )
                    all_tool_outputs.append(f"[{call['name']}] {result}")
                    history = history + [
                        {"role": "tool", "tool_call_id": call["id"], "content": str(result)}
                    ]

            summary = _extract_text(response.content if response is not None else "").strip()

            if not summary and all_tool_outputs:
                summary = "\n".join(all_tool_outputs)
            elif not summary:
                summary = f"No reliable search results found for: {question}"
        except Exception:
            logger.exception("Search agent failed for question: %s", question)
            summary = f"No reliable search results found for: {question}"

        # `messages` once the whole research run completes.
        return Command(
            update={"search_results": [summary]},
            goto="supervisor",
        )

    return search_agent
