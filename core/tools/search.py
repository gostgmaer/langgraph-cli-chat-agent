# ============================================================
# core/tools/search.py — Web Search Tool
# ============================================================
# TODO: Define `web_search(query, num_results)` tool function
# TODO: Support DuckDuckGo, SerpAPI, and Tavily backends
# TODO: Return ranked list of (title, url, snippet) tuples
# TODO: Handle provider selection from SEARCH_PROVIDER env
# ============================================================


import os

from langchain_core.tools import tool
from config.settings import settings
from langchain_community.utilities import GoogleSerperAPIWrapper

from shared import logger

# k=5 -- the raw API defaults to 10 results; the extra 5 rarely add
# information a research agent needs and just cost tokens to carry around.
search = GoogleSerperAPIWrapper(serper_api_key=settings.serper_api_key, k=5)


def _format_results(res: dict) -> str:
    """Extract just title/link/snippet per result -- the raw response also
    includes searchParameters, credits, position, relatedSearches, etc.,
    none of which a research agent uses but which roughly triple the token
    cost of every search call."""
    organic = res.get("organic") or []
    if not organic:
        return "No results found."

    lines = []
    for item in organic:
        title = item.get("title", "")
        link = item.get("link", "")
        snippet = item.get("snippet", "")
        lines.append(f"- {title}\n  {snippet}\n  Source: {link}")
    return "\n".join(lines)


@tool(
    "get_google_search",
    description="Search Google for general, up-to-date information on a topic.",
    return_direct=False,
)
def get_google_search(topic: str) -> str:
    """
    Search Google for the given topic and return live search results.

    Args:
        topic: The search query or topic.

    Returns:
        Structured Google search results.
    """

    try:
        res = search.results(query=topic)
        return _format_results(res)
    except Exception as e:
        logger.exception("Google search tool failed")
        return f"Unable to reach the search service: {e}"
