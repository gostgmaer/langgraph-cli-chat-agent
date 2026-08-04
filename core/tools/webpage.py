import io

import httpx
import trafilatura
from langchain.tools import tool
from pypdf import PdfReader

from shared.logger import logger
from utils.retries import async_retry

client = httpx.AsyncClient(
    timeout=15,
    follow_redirects=True,
    headers={
        # httpx's default UA ("python-httpx/x.x") is a well-known bot
        # signature that many sites block outright regardless of actual
        # scraping intent. A realistic browser UA + Accept headers clears
        # basic bot-detection (not sophisticated JS-challenge/paywall
        # protection, which no header spoof can bypass).
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": (
            "text/html,application/xhtml+xml,application/xml;q=0.9,"
            "application/pdf;q=0.9,*/*;q=0.8"
        ),
        "Accept-Language": "en-US,en;q=0.9",
    },
)

# Bounded so one fetch can't blow the token budget of the search agent that
# calls it -- this is meant to supplement search snippets with the most
# relevant part of a page, not ingest it wholesale.
MAX_CHARS = 4000
MAX_PDF_PAGES = 10
MAX_DOWNLOAD_BYTES = 15 * 1024 * 1024  # 15MB safety cap


def _truncate(text: str) -> str:
    text = text.strip()
    if len(text) > MAX_CHARS:
        return text[:MAX_CHARS] + "\n\n[... truncated ...]"
    return text


def _extract_pdf_text(content: bytes) -> str:
    reader = PdfReader(io.BytesIO(content))
    parts = []
    for page in reader.pages[:MAX_PDF_PAGES]:
        parts.append(page.extract_text() or "")
    return "\n".join(parts)


@tool(
    "get_page_content",
    description=(
        "Fetch and read the full text of a specific web page or PDF URL, "
        "e.g. one returned by get_google_search or web_search. Use this routinely for "
        "your 1-2 most promising sources per sub-question to get real "
        "depth beyond a search snippet -- not just as a last resort. Some "
        "sites (paywalled/bot-protected) will fail to fetch; that's "
        "expected, fall back to the snippet for those."
    ),
    return_direct=False,
)
async def get_page_content(url: str) -> str:
    """Fetch a URL and return its main readable text content (truncated)."""
    if not url.lower().startswith(("http://", "https://")):
        return "Invalid URL -- only http/https URLs are supported."

    async def _fetch() -> tuple[str, bytes]:
        async with client.stream("GET", url) as response:
            response.raise_for_status()
            content_type = response.headers.get("content-type", "")
            chunks = []
            total = 0
            async for chunk in response.aiter_bytes():
                total += len(chunk)
                if total > MAX_DOWNLOAD_BYTES:
                    break
                chunks.append(chunk)
            return content_type, b"".join(chunks)

    try:
        content_type, body = await async_retry(_fetch, max_attempts=2)

        if "application/pdf" in content_type or url.lower().endswith(".pdf"):
            text = _extract_pdf_text(body)
        else:
            html = body.decode("utf-8", errors="replace")
            text = trafilatura.extract(html) or ""

        if not text.strip():
            return f"No readable content could be extracted from {url}."

        return f"Content from {url}:\n\n{_truncate(text)}"

    except httpx.HTTPStatusError as e:
        return f"Page returned HTTP {e.response.status_code}: {url}"
    except httpx.RequestError as e:
        return f"Unable to reach {url}: {e}"
    except Exception as e:
        logger.exception("Page fetch failed for %s", url)
        return f"Unable to read content from {url}: {e}"
