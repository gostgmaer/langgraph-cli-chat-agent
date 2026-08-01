import httpx
from langchain.tools import tool

from config.settings import settings
from shared.logger import logger
from utils.retries import with_retry

client = httpx.Client(timeout=15)

SEMANTIC_SCHOLAR_URL = "https://api.semanticscholar.org/graph/v1/paper/search"


def _format_results(papers: list[dict]) -> str:
    if not papers:
        return "No academic papers found."

    lines = []
    for p in papers:
        title = p.get("title", "")
        year = p.get("year", "")
        venue = p.get("venue", "")
        authors = ", ".join(a.get("name", "") for a in (p.get("authors") or [])[:3])
        abstract = (p.get("abstract") or "").strip()
        if len(abstract) > 400:
            abstract = abstract[:400] + "..."
        url = p.get("url", "")
        meta = " · ".join(x for x in [authors, venue, str(year) if year else ""] if x)
        lines.append(f"- {title}\n  {meta}\n  {abstract}\n  Source: {url}")
    return "\n".join(lines)


@tool(
    "get_academic_search",
    description=(
        "Search academic/scientific papers (via Semantic Scholar, covering "
        "arXiv and most peer-reviewed venues) for a topic. Use for "
        "scientific, technical, or research-backed claims that need a "
        "peer-reviewed or preprint source rather than a general web page."
    ),
    return_direct=False,
)
def get_academic_search(topic: str) -> str:
    """Search academic papers for a topic and return title/abstract/source results."""

    def _fetch() -> list[dict]:
        headers = (
            {"x-api-key": settings.semantic_scholar_api_key}
            if settings.semantic_scholar_api_key
            else {}
        )
        response = client.get(
            SEMANTIC_SCHOLAR_URL,
            params={
                "query": topic,
                "limit": 5,
                "fields": "title,abstract,url,year,authors,venue",
            },
            headers=headers,
        )
        response.raise_for_status()
        return response.json().get("data") or []

    try:
        papers = with_retry(max_attempts=2)(_fetch)()
        return _format_results(papers)
    except Exception as e:
        logger.exception("Academic search tool failed")
        return f"Unable to reach the academic search service: {e}"
