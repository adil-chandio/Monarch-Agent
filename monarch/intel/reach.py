"""Agent-Reach bridge — wraps upstream CLI tools for zero-config internet access.

Agent-Reach installs and health-checks platform tools (yt-dlp, twitter-cli,
rdt-cli, mcporter, gh, etc.). This module calls those tools directly and
returns structured data for Monarch's intel layer.

Zero-config channels (tier 0): YouTube (yt-dlp), Web (Jina Reader), GitHub (gh), Exa (mcporter).
Login-required channels (tier 1): Twitter, Reddit, Bilibili, XiaoHongShu.

Usage:
    from monarch.intel.reach import doctor, yt_search, yt_transcript, web_read
"""

from __future__ import annotations

import json
import shutil
import subprocess
import re
from dataclasses import dataclass
from typing import Any


# ---------------------------------------------------------------------------
# Tool detection
# ---------------------------------------------------------------------------

def _has(cmd: str) -> bool:
    """Check if a CLI tool is on PATH."""
    return shutil.which(cmd) is not None


def _run(cmd: list[str], timeout: int = 30) -> subprocess.CompletedProcess:
    """Run a subprocess with timeout and capture output."""
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def _run_ok(cmd: list[str], timeout: int = 30) -> str | None:
    """Run a command; return stdout if exit 0, else None."""
    try:
        r = _run(cmd, timeout=timeout)
        return r.stdout.strip() if r.returncode == 0 else None
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None


# ---------------------------------------------------------------------------
# Doctor — health check for all upstream tools
# ---------------------------------------------------------------------------

@dataclass
class ToolStatus:
    name: str
    available: bool
    backend: str
    message: str


def doctor() -> list[ToolStatus]:
    """Check which upstream tools are available.

    Returns a list of ToolStatus for each platform Monarch can use.
    """
    checks: list[tuple[str, str, list[str]]] = [
        ("yt-dlp", "YouTube video info + transcripts", ["yt-dlp", "--version"]),
        ("twitter-cli", "Twitter/X search", ["twitter", "--version"]),
        ("rdt-cli", "Reddit search", ["rdt", "--version"]),
        ("mcporter", "Exa semantic search", ["mcporter", "--version"]),
        ("gh", "GitHub CLI", ["gh", "--version"]),
        ("bili", "Bilibili video search", ["bili", "--version"]),
        ("deno", "JS runtime for yt-dlp", ["deno", "--version"]),
        ("node", "JS runtime for yt-dlp", ["node", "--version"]),
    ]
    results: list[ToolStatus] = []
    for name, desc, cmd in checks:
        has = _has(cmd[0])
        if has:
            out = _run_ok(cmd, timeout=10)
            ok = out is not None
        else:
            ok = False
        results.append(ToolStatus(
            name=name,
            available=ok,
            backend=name if ok else "missing",
            message=desc if ok else f"{name} not installed",
        ))
    # hosted API row — youtube-transcript.io (no local tool, token-gated)
    from monarch.intel.ytt import has_token as ytt_has_token

    ytt_ok = ytt_has_token()
    results.append(ToolStatus(
        name="youtube-transcript.io",
        available=ytt_ok,
        backend="hosted API" if ytt_ok else "no token",
        message="hosted transcripts" if ytt_ok
        else "set YOUTUBE_TRANSCRIPT_IO_TOKEN in .env",
    ))
    return results


def doctor_dict() -> dict[str, dict[str, Any]]:
    """Doctor as a dict keyed by tool name."""
    return {
        s.name: {
            "available": s.available,
            "backend": s.backend,
            "message": s.message,
        }
        for s in doctor()
    }


# ---------------------------------------------------------------------------
# YouTube — via yt-dlp (zero config, no API key)
# ---------------------------------------------------------------------------

def yt_search(query: str, max_results: int = 10) -> list[dict]:
    """Search YouTube via yt-dlp.

    Returns list of dicts with: video_id, title, channel, url, duration.
    Requires yt-dlp on PATH.
    """
    if not _has("yt-dlp"):
        raise RuntimeError("yt-dlp not installed. Run: pip install yt-dlp")
    cmd = [
        "yt-dlp",
        f"ytsearch{max_results}:{query}",
        "--flat-playlist",
        "--dump-json",
        "--no-warnings",
    ]
    try:
        r = _run(cmd, timeout=30)
    except subprocess.TimeoutExpired:
        raise RuntimeError("yt-dlp search timed out")
    if r.returncode != 0:
        raise RuntimeError(f"yt-dlp search failed: {r.stderr[:300]}")
    results = []
    for line in r.stdout.strip().splitlines():
        if not line.strip():
            continue
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            continue
        vid = data.get("id", "")
        if not vid:
            continue
        results.append({
            "video_id": vid,
            "title": data.get("title", ""),
            "channel": data.get("channel", data.get("uploader", "")),
            "url": data.get("url", f"https://www.youtube.com/watch?v={vid}"),
            "duration": data.get("duration"),
            "view_count": data.get("view_count"),
        })
    return results


def yt_video_info(url: str) -> dict:
    """Get full video metadata from a YouTube URL via yt-dlp.

    Returns dict with: title, description, channel, duration, subtitles, etc.
    """
    if not _has("yt-dlp"):
        raise RuntimeError("yt-dlp not installed")
    cmd = ["yt-dlp", "--dump-json", "--no-download", "--no-warnings", url]
    try:
        r = _run(cmd, timeout=30)
    except subprocess.TimeoutExpired:
        raise RuntimeError("yt-dlp info timed out")
    if r.returncode != 0:
        raise RuntimeError(f"yt-dlp info failed: {r.stderr[:300]}")
    return json.loads(r.stdout)


def yt_transcript(url: str, lang: str = "en") -> str:
    """Extract subtitles/transcript from a YouTube video via yt-dlp.

    Tries manual subs first, then auto-generated.
    Returns the subtitle text as a plain string.
    """
    if not _has("yt-dlp"):
        raise RuntimeError("yt-dlp not installed")
    import tempfile, os
    with tempfile.TemporaryDirectory() as tmpdir:
        out_tpl = os.path.join(tmpdir, "%(id)s")
        cmd = [
            "yt-dlp",
            "--write-sub", "--write-auto-sub",
            "--sub-lang", lang,
            "--sub-format", "vtt",
            "--skip-download",
            "--no-warnings",
            "-o", out_tpl,
            url,
        ]
        try:
            r = _run(cmd, timeout=30)
        except subprocess.TimeoutExpired:
            raise RuntimeError("yt-dlp transcript timed out")
        if r.returncode != 0:
            raise RuntimeError(f"yt-dlp transcript failed: {r.stderr[:300]}")
        # Find the subtitle file
        files = [f for f in os.listdir(tmpdir) if f.endswith(".vtt")]
        if not files:
            raise RuntimeError(f"No subtitles found for {url}")
        vtt_path = os.path.join(tmpdir, files[0])
        raw = open(vtt_path, encoding="utf-8").read()
        return _vtt_to_text(raw)


def _vtt_to_text(vtt: str) -> str:
    """Strip VTT formatting, return plain transcript text."""
    lines = []
    for line in vtt.splitlines():
        s = line.strip()
        if not s:
            continue
        if s.startswith("WEBVTT") or s.startswith("Kind:") or s.startswith("Language:"):
            continue
        if re.match(r"^\d{2}:\d{2}", s):
            continue
        if re.match(r"^\d+$", s):
            continue
        # Strip HTML tags
        s = re.sub(r"<[^>]+>", "", s)
        if s:
            lines.append(s)
    # Deduplicate consecutive identical lines (common in auto-subs)
    deduped = []
    for line in lines:
        if not deduped or line != deduped[-1]:
            deduped.append(line)
    return "\n".join(deduped)


# ---------------------------------------------------------------------------
# Web — via Jina Reader (zero config)
# ---------------------------------------------------------------------------

def web_read(url: str) -> str:
    """Read any URL as clean markdown via Jina Reader.

    Zero-config: just curl https://r.jina.ai/URL
    """
    jina_url = f"https://r.jina.ai/{url}"
    cmd = ["curl", "-sL", "--max-time", "20", jina_url]
    try:
        r = _run(cmd, timeout=25)
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"Jina Reader timed out for {url}")
    if r.returncode != 0:
        raise RuntimeError(f"curl failed for {jina_url}")
    text = r.stdout.strip()
    if not text:
        raise RuntimeError(f"Empty response from Jina Reader for {url}")
    return text


# ---------------------------------------------------------------------------
# Search — via Exa / mcporter (zero config if installed)
# ---------------------------------------------------------------------------

def exa_search(query: str, num_results: int = 5) -> list[dict]:
    """Semantic web search via Exa (mcporter).

    Returns list of dicts with: title, url, snippet.
    """
    if not _has("mcporter"):
        raise RuntimeError("mcporter not installed. Run: npm install -g mcporter")
    cmd = [
        "mcporter", "call", "exa.web_search_exa",
        f"query={query}", f"numResults={num_results}",
    ]
    try:
        r = _run(cmd, timeout=30)
    except subprocess.TimeoutExpired:
        raise RuntimeError("Exa search timed out")
    if r.returncode != 0:
        raise RuntimeError(f"Exa search failed: {r.stderr[:300]}")
    # Parse mcporter output (JSON or YAML)
    text = r.stdout.strip()
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        # mcporter may return YAML-ish; try to extract results
        return [{"title": "raw", "url": "", "snippet": text[:500]}]
    results = []
    items = data if isinstance(data, list) else data.get("results", data.get("items", []))
    for item in items:
        if isinstance(item, dict):
            results.append({
                "title": item.get("title", ""),
                "url": item.get("url", item.get("link", "")),
                "snippet": item.get("snippet", item.get("text", ""))[:300],
            })
    return results


# ---------------------------------------------------------------------------
# Twitter — via twitter-cli (needs login)
# ---------------------------------------------------------------------------

def twitter_search(query: str, count: int = 10) -> list[dict]:
    """Search Twitter/X via twitter-cli.

    Requires: pipx install twitter-cli + login.
    Returns list of dicts with: text, author, url, likes, retweets.
    """
    if not _has("twitter"):
        raise RuntimeError("twitter-cli not installed. Run: pipx install twitter-cli")
    cmd = ["twitter", "search", query, "-n", str(count), "--json"]
    try:
        r = _run(cmd, timeout=30)
    except subprocess.TimeoutExpired:
        raise RuntimeError("Twitter search timed out")
    if r.returncode != 0:
        raise RuntimeError(f"Twitter search failed: {r.stderr[:300]}")
    try:
        data = json.loads(r.stdout)
    except json.JSONDecodeError:
        return [{"text": r.stdout[:500], "author": "", "url": ""}]
    results = []
    items = data if isinstance(data, list) else data.get("tweets", data.get("results", []))
    for item in items:
        if isinstance(item, dict):
            results.append({
                "text": item.get("text", item.get("content", "")),
                "author": item.get("author", item.get("user", {}).get("screen_name", "")),
                "url": item.get("url", ""),
                "likes": item.get("likes", item.get("favorite_count", 0)),
                "retweets": item.get("retweets", item.get("retweet_count", 0)),
            })
    return results


# ---------------------------------------------------------------------------
# Reddit — via rdt-cli or OpenCLI (needs login)
# ---------------------------------------------------------------------------

def reddit_search(query: str, limit: int = 10) -> list[dict]:
    """Search Reddit via rdt-cli.

    Requires: rdt-cli installed + login.
    Returns list of dicts with: title, url, subreddit, score, comments.
    """
    if _has("rdt"):
        cmd = ["rdt", "search", query, "--limit", str(limit), "--json"]
    elif _has("opencli"):
        cmd = ["opencli", "reddit", "search", query, "-f", "json"]
    else:
        raise RuntimeError("No Reddit tool available. Install rdt-cli or OpenCLI")
    try:
        r = _run(cmd, timeout=30)
    except subprocess.TimeoutExpired:
        raise RuntimeError("Reddit search timed out")
    if r.returncode != 0:
        raise RuntimeError(f"Reddit search failed: {r.stderr[:300]}")
    try:
        data = json.loads(r.stdout)
    except json.JSONDecodeError:
        return [{"title": r.stdout[:500], "url": "", "subreddit": ""}]
    results = []
    items = data if isinstance(data, list) else data.get("results", data.get("posts", []))
    for item in items:
        if isinstance(item, dict):
            results.append({
                "title": item.get("title", ""),
                "url": item.get("url", item.get("permalink", "")),
                "subreddit": item.get("subreddit", ""),
                "score": item.get("score", item.get("upvotes", 0)),
                "comments": item.get("num_comments", item.get("comments", 0)),
            })
    return results


# ---------------------------------------------------------------------------
# GitHub — via gh CLI (zero config if installed)
# ---------------------------------------------------------------------------

def gh_search_repos(query: str, limit: int = 10) -> list[dict]:
    """Search GitHub repos via gh CLI.

    Returns list of dicts with: name, url, description, stars, language.
    """
    if not _has("gh"):
        raise RuntimeError("gh not installed")
    cmd = ["gh", "search", "repos", query, "--sort", "stars", "--limit", str(limit), "--json",
           "name,url,description,stargazersCount,primaryLanguage"]
    try:
        r = _run(cmd, timeout=20)
    except subprocess.TimeoutExpired:
        raise RuntimeError("gh search timed out")
    if r.returncode != 0:
        # Fallback: simpler command
        cmd2 = ["gh", "search", "repos", query, "--sort", "stars", "--limit", str(limit)]
        r2 = _run_ok(cmd2, timeout=20)
        if r2:
            return [{"name": line, "url": "", "description": "", "stars": 0}
                    for line in r2.splitlines() if line.strip()]
        raise RuntimeError(f"gh search failed: {r.stderr[:300]}")
    data = json.loads(r.stdout)
    return [
        {
            "name": item.get("name", ""),
            "url": item.get("url", ""),
            "description": item.get("description", "") or "",
            "stars": item.get("stargazersCount", 0),
            "language": (item.get("primaryLanguage") or {}).get("name", ""),
        }
        for item in data
    ]
