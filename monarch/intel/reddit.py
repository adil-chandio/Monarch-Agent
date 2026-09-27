"""Reddit intel — audience language and pain point extraction via Agent-Reach.

Requires: rdt-cli or OpenCLI installed + Reddit login.
Run: pipx install rdt-cli && rdt login
"""

from __future__ import annotations

from monarch.intel.reach import reddit_search


def search_niche(niche: str, limit: int = 10) -> list[dict]:
    """Search Reddit for niche-related posts.

    Returns list of dicts with: title, url, subreddit, score, comments.
    Used for audience language analysis and pain point extraction.
    """
    return reddit_search(niche, limit)


def extract_pain_points(results: list[dict]) -> list[str]:
    """Extract audience pain points from Reddit post titles.

    Reddit titles are often direct questions/problems — perfect for idea seeds.
    """
    pain_points = []
    for r in results:
        title = r.get("title", "").strip()
        if not title:
            continue
        # High-score posts indicate real pain points
        score = r.get("score", 0)
        if score > 10 or "?" in title:
            pain_points.append(title)
    return pain_points


def extract_language_patterns(results: list[dict]) -> dict:
    """Extract audience language from Reddit results.

    Reddit uses authentic human language — ideal for niche voice lock.
    """
    titles = [r.get("title", "") for r in results if r.get("title")]
    subreddits = list(set(r.get("subreddit", "") for r in results if r.get("subreddit")))
    return {
        "titles": titles[:15],
        "subreddits": subreddits,
        "sample_size": len(results),
    }
