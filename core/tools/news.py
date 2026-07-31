# ============================================================
# core/tools/news.py — News Tool
# ============================================================
# TODO: Define `get_news(query, category)` tool function
# TODO: Call NewsAPI using NEWS_API_KEY
# TODO: Parse and return top headlines as structured data
# TODO: Handle API errors and empty results
# ============================================================


from langchain_tavily import TavilySearch
from langchain.tools import tool

from config.settings import settings
from shared.logger import logger
from utils.retries import with_retry


def _format_results(results: dict) -> str:
    """Extract just title/content/url per result -- the raw response also
    wraps this in query echo, follow_up_questions, images, response_time,
    request_id, and a per-result relevance score, none of which a research
    agent uses but which still cost tokens to carry around."""
    items = results.get("results") or []
    if not items:
        return "No results found."

    lines = []
    for item in items:
        title = item.get("title", "")
        content = item.get("content", "")
        url = item.get("url", "")
        lines.append(f"- {title}\n  {content}\n  Source: {url}")
    return "\n".join(lines)


@tool(
    "get_news",
    description="Get the latest news for a given topic.",
)
async def get_news(topic: str):
    """Get the latest news for a topic."""

    if not settings.tavily_api_key:
        return "Tavily API key is missing."

    try:
        search = TavilySearch(
            max_results=5,
            tavily_api_key=settings.tavily_api_key,
        )

        results = with_retry(max_attempts=2)(search.invoke)(
            {"query": f"Latest news about {topic}"}
        )

        logger.debug("News tool executed for %s", topic)

        return _format_results(results)

    except Exception as e:
        logger.exception("News tool failed")
        return f"Unable to reach the news service: {e}"
