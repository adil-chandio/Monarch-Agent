"""YouTube intel — dual-path: YouTube Data API or yt-dlp (Agent-Reach).

Priority:
1. If YOUTUBE_API_KEY is set → use official API (faster, structured).
2. Else if yt-dlp is available → use yt-dlp (zero-config, no API key).
3. Else → raise with clear install instructions.
"""

from __future__ import annotations

import json
import shutil
from urllib.parse import urlencode

from monarch.core.config import secrets
from monarch.core.missing import missing


def _has_ytdlp() -> bool:
    return shutil.which("yt-dlp") is not None


def search_videos(query: str, max_results: int = 10) -> list[dict]:
    """Search YouTube videos. Auto-detects best available backend."""
    key = secrets().youtube
    if key:
        return _api_search(query, max_results, key)
    if _has_ytdlp():
        from monarch.intel.reach import yt_search
        return yt_search(query, max_results)
    raise ValueError(
        "No YouTube backend available. Set YOUTUBE_API_KEY in .env "
        "or install yt-dlp: pip install yt-dlp"
    )


def video_info(url: str) -> dict:
    """Get video metadata. Auto-detects best available backend."""
    if _has_ytdlp():
        from monarch.intel.reach import yt_video_info
        return yt_video_info(url)
    key = secrets().youtube
    if key:
        # API path: extract video ID and query
        import re
        m = re.search(r"(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})", url)
        if not m:
            raise ValueError(f"Cannot extract video ID from {url}")
        vid = m.group(1)
        return _api_video_info(vid, key)
    raise ValueError("No YouTube backend available")


def video_transcript(url: str, lang: str = "en") -> str:
    """Get video transcript/subtitles. Requires yt-dlp."""
    from monarch.intel.reach import yt_transcript
    return yt_transcript(url, lang)


# ---------------------------------------------------------------------------
# Private: YouTube Data API path
# ---------------------------------------------------------------------------

def _api_search(query: str, max_results: int, key: str) -> list[dict]:
    from monarch.intel.http import get_json

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


def _api_video_info(video_id: str, key: str) -> dict:
    from monarch.intel.http import get_json

    qs = urlencode(
        {
            "part": "snippet,statistics,contentDetails",
            "id": video_id,
            "key": key,
        }
    )
    data = get_json(f"https://www.googleapis.com/youtube/v3/videos?{qs}")
    items = data.get("items") or []
    if not items:
        raise ValueError(f"Video {video_id} not found")
    it = items[0]
    sn = it.get("snippet", {})
    st = it.get("statistics", {})
    cd = it.get("contentDetails", {})
    return {
        "video_id": video_id,
        "title": sn.get("title", ""),
        "description": sn.get("description", ""),
        "channel": sn.get("channelTitle", ""),
        "published": sn.get("publishedAt", ""),
        "tags": sn.get("tags", []),
        "view_count": st.get("viewCount", "0"),
        "like_count": st.get("likeCount", "0"),
        "duration": cd.get("duration", ""),
        "url": f"https://www.youtube.com/watch?v={video_id}",
    }
