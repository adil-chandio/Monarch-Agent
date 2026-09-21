from __future__ import annotations

from urllib.parse import urlencode

from monarch.core.config import secrets
from monarch.core.missing import missing
from monarch.intel.http import get_json


def search_videos(query: str, max_results: int = 10) -> list[dict]:
    key = secrets().youtube
    if not key:
        raise ValueError(missing("YOUTUBE_API_KEY in .env"))
    qs = urlencode(
        {
            "part": "snippet",
            "q": query,
            "type": "video",
            "order": "viewCount",
            "maxResults": max(1, min(max_results, 15)),
            "key": key,
        }
    )
    data = get_json(f"https://www.googleapis.com/youtube/v3/search?{qs}")
    out = []
    for it in data.get("items") or []:
        sn = it.get("snippet") or {}
        vid = (it.get("id") or {}).get("videoId")
        if not vid:
            continue
        out.append(
            {
                "video_id": vid,
                "title": sn.get("title", ""),
                "channel": sn.get("channelTitle", ""),
                "published": sn.get("publishedAt", ""),
                "url": f"https://www.youtube.com/watch?v={vid}",
            }
        )
    return out
