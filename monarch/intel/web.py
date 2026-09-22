"""Web intel — universal URL reading and semantic search via Agent-Reach.

Zero-config: Jina Reader (any URL) + Exa (semantic search).
"""

from __future__ import annotations

from monarch.intel.reach import exa_search, web_read


def read_url(url: str) -> str:
    """Read any URL as clean markdown via Jina Reader.

    Zero-config: works without any API key.
    Used for competitor video pages, articles, etc.
    """
    return web_read(url)


def search_web(query: str, num_results: int = 5) -> list[dict]:
    """Semantic web search via Exa.

    Returns list of dicts with: title, url, snippet.
    Requires: mcporter installed + Exa configured.
    """
    return exa_search(query, num_results)


def extract_competitor_page(url: str) -> dict:
    """Extract structured data from a competitor's page.

    Returns dict with: title, content, word_count, key_phrases.
    """
    text = web_read(url)
    lines = text.splitlines()
    title = ""
    for line in lines:
        s = line.strip()
        if s.startswith("# "):
            title = s[2:].strip()
            break
    words = text.split()
    return {
        "url": url,
        "title": title,
        "content": text,
        "word_count": len(words),
        "lines": len(lines),
    }
