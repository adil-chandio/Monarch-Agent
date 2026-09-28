"""youtube-transcript.io client — hosted transcripts when yt-dlp is missing.

Third backend in Monarch's dual... triple-path intel stack:

1. YOUTUBE_API_KEY            → official Data API (search / stats)
2. yt-dlp (Agent-Reach)       → transcripts, zero-config
3. youtube-transcript.io      → hosted transcripts, no local tooling —
   set ``YOUTUBE_TRANSCRIPT_IO_TOKEN`` in ``.env`` (token from their profile page)

API facts (from their docs):
* ``POST /api/transcripts`` — up to 50 video ids per call, Basic auth
* ``POST /api/channels``   — Plus/Pro plans only, channel ids without ``@``
* rate limit: 5 requests / 10s → on ``429`` we honor ``Retry-After`` once

Fail-closed: no token / bad ids / HTTP errors raise with the exact problem.
The response shape is not versioned by the vendor, so the flattener accepts
every known shape (plain string, segment lists, nested keys) and never
crashes on a new one — it returns what it can find.
"""

from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.request

#: env var name holding the Basic API token
TOKEN_ENV = "YOUTUBE_TRANSCRIPT_IO_TOKEN"
API_BASE = "https://www.youtube-transcript.io/api"
#: vendor limit — ids per request
MAX_IDS_PER_CALL = 50
#: vendor rate limit window
RETRY_DEFAULT_S = 10.0

VIDEO_ID = re.compile(r"^[A-Za-z0-9_-]{11}$")

_URL_PATTERNS = (
    re.compile(r"(?:youtube\.com/watch\?(?:.*&)?v=)([A-Za-z0-9_-]{11})"),
    re.compile(r"(?:youtu\.be/)([A-Za-z0-9_-]{11})"),
    re.compile(r"(?:youtube\.com/shorts/)([A-Za-z0-9_-]{11})"),
    re.compile(r"(?:youtube\.com/embed/)([A-Za-z0-9_-]{11})"),
    re.compile(r"(?:youtube\.com/live/)([A-Za-z0-9_-]{11})"),
)


class RateLimited(RuntimeError):
    """The vendor's 429 — carries the Retry-After seconds."""

    def __init__(self, retry_after_s: float) -> None:
        super().__init__(f"429 rate limited — retry after {retry_after_s:.0f}s")
        self.retry_after_s = retry_after_s


def _get_token() -> str:
    """Token from env (core.config loads .env on first import). Fail-closed."""
    from monarch.core import config  # noqa: F401 — ensures .env is loaded
    import os

    token = os.environ.get(TOKEN_ENV, "").strip()
    if not token:
        raise ValueError(
            f"No youtube-transcript.io token. Set {TOKEN_ENV} in .env "
            "(token: youtube-transcript.io/profile)"
        )
    return token


def parse_video_ids(items: list[str]) -> list[str]:
    """Raw 11-char ids or YouTube URLs → clean, deduped id list."""
    out: list[str] = []
    for raw in items or []:
        s = (raw or "").strip()
        if not s:
            continue
        if VIDEO_ID.match(s):
            vid = s
        else:
            vid = ""
            for pat in _URL_PATTERNS:
                m = pat.search(s)
                if m:
                    vid = m.group(1)
                    break
            if not vid:
                raise ValueError(f"cannot parse a video id from {raw!r}")
        if vid not in out:
            out.append(vid)
    return out


def _post_json(endpoint: str, payload: dict, token: str) -> dict:
    """One authenticated POST. Raises :class:`RateLimited` on 429."""
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{API_BASE}/{endpoint}",
        data=data,
        headers={
            "User-Agent": "monarch-agent/0.1",
            "Content-Type": "application/json",
            "Authorization": f"Basic {token}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            body = r.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        if e.code == 429:
            retry = e.headers.get("Retry-After") if e.headers else None
            try:
                seconds = float(retry) if retry else RETRY_DEFAULT_S
            except ValueError:
                seconds = RETRY_DEFAULT_S
            raise RateLimited(seconds) from e
        detail = e.read().decode("utf-8", errors="replace")[:300]
        raise RuntimeError(f"youtube-transcript.io HTTP {e.code}: {detail}") from e
    return json.loads(body)


def flatten_transcript(item: dict) -> str:
    """Vendor-agnostic: whatever shape came back → one plain text blob."""
    if not isinstance(item, dict):
        return str(item).strip() if isinstance(item, str) else ""
    for key in ("transcript", "transcripts", "text", "content", "lines", "subtitles"):
        value = item.get(key)
        if value is None:
            continue
        if isinstance(value, str):
            return value.strip()
        if isinstance(value, list):
            parts: list[str] = []
            for seg in value:
                if isinstance(seg, str):
                    parts.append(seg)
                elif isinstance(seg, dict):
                    for sub in ("text", "line", "content", "caption"):
                        if isinstance(seg.get(sub), str) and seg[sub].strip():
                            parts.append(seg[sub].strip())
                            break
            return " ".join(p for p in parts if p)
    return ""


def _normalize_response(raw, ids: list[str]) -> list[dict]:
    """``[{"id": ..., "transcript": ...}]`` (or wrapped) → per-id records."""
    items = raw
    if isinstance(raw, dict):
        for key in ("transcripts", "data", "results", "items"):
            if isinstance(raw.get(key), list):
                items = raw[key]
                break
        else:
            items = [raw]
    if not isinstance(items, list):
        raise RuntimeError("youtube-transcript.io: unexpected response shape")
    by_id: dict[str, dict] = {}
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        vid = str(item.get("id") or item.get("videoId") or item.get("video_id")
                  or (ids[i] if i < len(ids) and str(item.get("id", "")) == "" else i))
        by_id[vid] = {"id": vid, "transcript": flatten_transcript(item),
                      "raw": item}
    return [by_id.get(vid, {"id": vid, "transcript": "", "raw": {}}) for vid in ids]


def fetch_transcripts(
    ids: list[str],
    *,
    token: str | None = None,
    transport=None,
) -> list[dict]:
    """Transcripts for up to N*50 ids, chunked; retries 429 once per chunk.

    ``transport`` is injectable for tests: ``fn(payload, token) -> dict``.
    """
    token = token or _get_token()
    ids = parse_video_ids(ids)
    if not ids:
        raise ValueError("This is missing, could you provide it: video ids.")
    post = transport or _post_json
    out: list[dict] = []
    for start in range(0, len(ids), MAX_IDS_PER_CALL):
        chunk = ids[start:start + MAX_IDS_PER_CALL]
        try:
            raw = post("transcripts", {"ids": chunk}, token)
        except RateLimited as e:
            time.sleep(min(e.retry_after_s, 30.0))
            raw = post("transcripts", {"ids": chunk}, token)  # one polite retry
        out.extend(_normalize_response(raw, chunk))
    return out


def transcripts_text(ids: list[str], **kw) -> dict[str, str]:
    """ids → {id: plain transcript text} (empty string when unavailable)."""
    return {r["id"]: r["transcript"] for r in fetch_transcripts(ids, **kw)}


# ---------------------------------------------------------------------------
# channels (Plus/Pro plans)
# ---------------------------------------------------------------------------


def fetch_channels(ids: list[str], *, token: str | None = None, transport=None) -> list[dict]:
    """Channel info for public ids without ``@`` (jawed → @jawed)."""
    token = token or _get_token()
    clean: list[str] = []
    for raw in ids or []:
        s = (raw or "").strip().lstrip("@")
        s = s.rsplit("/", 1)[-1] if "/" in s else s  # tolerate full URLs
        if not s:
            continue
        if s not in clean:
            clean.append(s)
    if not clean:
        raise ValueError("This is missing, could you provide it: channel ids.")
    post = transport or _post_json
    out: list[dict] = []
    for start in range(0, len(clean), MAX_IDS_PER_CALL):
        chunk = clean[start:start + MAX_IDS_PER_CALL]
        try:
            out.extend(post("channels", {"ids": chunk}, token))
        except RateLimited as e:
            time.sleep(min(e.retry_after_s, 30.0))
            out.extend(post("channels", {"ids": chunk}, token))
    return out


def has_token() -> bool:
    """True when a token is configured — used by ``monarch keys`` / doctor."""
    try:
        return bool(_get_token())
    except ValueError:
        return False
