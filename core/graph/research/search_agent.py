from typing import Literal
from langgraph.types import Command

from core.graph.research.state import ResearchState
from core.graph.research.prompts import SEARCH_AGENT_PROMPT, current_date_context
from core.llm.manager import LLMManager
from core.tools.search import get_google_search
from core.tools.news import get_news
from shared.logger import logger

search_tools = [get_google_search, get_news]
# 1 extra round (not 2) -- each round resends the full ~600-token
# SEARCH_AGENT_PROMPT, multiplied across every parallel sub-question, so
# this is the single biggest lever on /research input-token cost. Still
# allows one refinement search if the first attempt comes back empty.
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
                response = await llm_with_tools.ainvoke(history)
                calls = getattr(response, "tool_calls", []) or []
                if not calls:
                    break

                history = history + [response]
                for call in calls:
                    tool_fn = next(t for t in search_tools if t.name == call["name"])
                    result = (
                        await tool_fn.ainvoke(call["args"])
                        if call["name"] == "get_news"
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

        # Intentionally not appended to `messages` -- this is scratch
        # research data (one entry per parallel sub-question), not something
        # that should be replayed as context on every later chat turn in
        # this thread. `search_results` is what reviewer_agent/writer_agent
        # actually read; supervisor appends the one clean final answer to
        # `messages` once the whole research run completes.
        return Command(
            update={"search_results": [summary]},
            goto="supervisor",
        )

    return search_agent
