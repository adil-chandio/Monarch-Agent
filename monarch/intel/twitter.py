"""Twitter/X intel — competitor analysis and trend detection via Agent-Reach.

Requires: twitter-cli installed + login.
Run: pipx install twitter-cli && agent-reach configure twitter-cookies
"""

from __future__ import annotations

from monarch.intel.reach import twitter_search


def search_niche(niche: str, count: int = 10) -> list[dict]:
    """Search Twitter for niche-related discussions.

    Returns list of dicts with: text, author, url, likes, retweets.
    Used for competitor DNA extraction and audience language analysis.
    """
    return twitter_search(niche, count)


def extract_titles(results: list[dict]) -> list[str]:
    """Extract potential title ideas from Twitter search results.

    Looks for tweets with high engagement that contain hook-worthy phrases.
    """
    titles = []
    for r in results:
        text = r.get("text", "").strip()
        if not text:
            continue
        # Use first sentence as potential title seed
        first_line = text.split("\n")[0].strip()
        if len(first_line) >= 10 and len(first_line) <= 100:
            titles.append(first_line)
    return titles


def extract_language_patterns(results: list[dict]) -> dict:
    """Extract audience language patterns from Twitter results.

    Returns dict with: common_phrases, tone, engagement_patterns.
    """
    phrases = []
    for r in results:
        text = r.get("text", "").strip()
        if not text:
            continue
        # Extract short punchy phrases (potential hooks)
        words = text.split()
        if 4 <= len(words) <= 12:
            phrases.append(text)
    return {
        "common_phrases": phrases[:10],
        "sample_size": len(results),
        "top_engagement": max((r.get("likes", 0) for r in results), default=0),
    }
