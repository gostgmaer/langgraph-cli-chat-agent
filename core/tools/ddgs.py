# ============================================================
# core/tools/search.py — DuckDuckGo Search Tool
# ============================================================

from typing import List

from ddgs import DDGS
from langchain_core.tools import tool

from shared.logger import logger


def _format_results(results: List[dict]) -> str:
    """Format DDGS search results into an LLM-friendly response."""

    if not results:
        return "No search results found."

    output = []

    for index, item in enumerate(results, start=1):
        title = item.get("title", "N/A")
        url = item.get("href", "N/A")
        snippet = item.get("body", "No description available.")

        output.append(
            "\n".join(
                [
                    f"## Result {index}",
                    f"Title: {title}",
                    f"URL: {url}",
                    f"Snippet: {snippet}",
                ]
            )
        )

    return "\n\n---\n\n".join(output)


@tool(
    "web_search",
    description="Search the web using DuckDuckGo and return the most relevant results.",
    return_direct=False,
)
def web_search(query: str, max_results: int = 5) -> str:
    """
    Search the web using DuckDuckGo.

    Args:
        query: Search query.
        max_results: Maximum number of search results.

    Returns:
        Formatted search results.
    """

    try:
        with DDGS() as ddgs:
            results = list(
                ddgs.text(
                    query,
                    max_results=max_results,
                )
            )

        return _format_results(results)

    except Exception as e:
        logger.exception("DuckDuckGo search failed")
        return f"Search failed: {str(e)}"