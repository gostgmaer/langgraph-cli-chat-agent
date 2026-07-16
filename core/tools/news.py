# ============================================================
# core/tools/news.py — News Tool
# ============================================================
# TODO: Define `get_news(query, category)` tool function
# TODO: Call NewsAPI using NEWS_API_KEY
# TODO: Parse and return top headlines as structured data
# TODO: Handle API errors and empty results
# ============================================================



from langchain_tavily import TavilySearch


from dataclasses import dataclass
from langchain.tools import tool

from config.settings import settings
from shared import logger



@dataclass
class NewsData:
    topic: str
    title: str
    url: str


@dataclass
class Context:
    topic: str


@dataclass
class ResponseFormat:
    summary: str
    temperature_celsius: float
    temperature_fahrenheit: float
    humidity: float


@tool(
    "get_news",
    description="Get the latest news for a given topic.",
    return_direct=False,
)
async def get_news(topic: str):
    """Get the latest news for a topic."""
    if not settings.tavily_api_key:
        return "News API key is missing."
    try:
        search_tool = TavilySearch(max_results=2, api_key=settings.tavily_api_key, topic=topic)

        logger.info("News tool executed for %s", topic)
        return search_tool

    except Exception as e:
        return f"Unable to reach the news service: {e}"

