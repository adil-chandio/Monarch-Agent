"""Transcript ingest — turn agent-fetched text into forensic records.

The sandbox story (Phase: "tabahi next level"): Monarch's runtime network is
restricted, but the **agent's page-fetch tool** runs on the platform network
and opens YouTube watch pages — returning clean markdown with title, views,
description and a ``## Transcript`` section.

This module closes the loop *inside* Monarch:

* agent fetches ``https://www.youtube.com/watch?v=<id>`` with its page tool
* agent saves the text and runs ``monarch transcript-ingest fetch.txt``
* Monarch parses it into the same forensic record shape ``scrape`` produces,
  so F0 forensics, DNA extraction and script work proceed unchanged.

Accepted inputs (auto-detected, never guessed silently — unknown is ``plain``):

* fetch-page markdown — ``# [Title](url)`` + ``## Transcript``
* WebVTT (``WEBVTT`` header, ``HH:MM:SS.mmm -->`` cues)
* SRT (``1`` + ``00:00:00,000 -->`` cues)
* plain text (passthrough)

Fail-closed: a fetch-page document without a transcript still yields full
metadata but ``has_transcript: false`` — the caller decides what to do.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

_TS_VTT = r"\d{1,2}:\d{2}:\d{2}\.\d{3}"
_TS_SRT = r"\d{1,2}:\d{2}:\d{2},\d{3}"
_CUE = re.compile(rf"({ _TS_VTT}|{_TS_SRT}) --> ({_TS_VTT}|{_TS_SRT})")
_VTT_JUNK = re.compile(
    r"^(WEBVTT.*|NOTE.*|Kind:.*|Language:.*|STYLE|REGION|\d+$)$", re.M
)
_INLINE_TS = re.compile(rf"\[?({_TS_VTT}|{_TS_SRT})\]?")


# ---------------------------------------------------------------------------
# detectors
# ---------------------------------------------------------------------------


def detect_kind(text: str) -> str:
    """fetch_page markdown | vtt | srt | plain"""
    has_md_heading = re.search(r"^# \[", text or "", re.M) is not None
    if has_md_heading and ("## Transcript" in text or "**Uploaded by**" in text):
        return "fetch_page"
    if "WEBVTT" in (text or "")[:200]:
        return "vtt"
    if _CUE.search(text) and re.search(r"^\d+\s*$", text, re.M):
        return "srt"
    if _CUE.search(text):
        return "vtt"
    return "plain"


# ---------------------------------------------------------------------------
# parsers — every one returns plain transcript text
# ---------------------------------------------------------------------------


def parse_vtt(text: str) -> str:
    body = _VTT_JUNK.sub("", text)
    out: list[str] = []
    for line in body.splitlines():
        if _CUE.search(line) or not line.strip():
            continue
        out.append(_INLINE_TS.sub("", line).strip())
    return " ".join(p for p in out if p)


def parse_srt(text: str) -> str:
    out: list[str] = []
    for line in text.splitlines():
        if not line.strip() or line.strip().isdigit() or _CUE.search(line):
            continue
        out.append(line.strip())
    return " ".join(p for p in out if p)


_NUM = r"([\d,\.]+)\s*([KMB]?)"

def _count(s: str) -> str:
    """'435,858,102 views' / '1.2M' -> digits-only string (best effort)."""
    m = re.search(r"\d[\d,\.]*", s or "")
    return m.group(0).replace(",", "") if m else "0"


def parse_fetch_page(text: str) -> dict:
    """fetch-page markdown -> {title, url, channel, views, description, transcript}."""
    title = ""
    url = ""
    m = re.search(r"^# \[([^\]]+)\]\((https?://[^\)]+)\)", text, re.M)
    if m:
        title, url = m.group(1).strip(), m.group(2)

    def field(name: str) -> str:
        mm = re.search(rf"\*\*{name}\*\*: (.+)", text)
        return mm.group(1).strip() if mm else ""

    channel = field("Uploaded by")
    # channel comes as a markdown link — keep the label
    channel = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", channel)

    desc = ""
    md = re.search(r"## Description\s*\n+```[^\n]*\n(.*?)```", text, re.S)
    if md:
        desc = md.group(1).strip()

    transcript = ""
    mt = re.search(r"## Transcript\s*\n+(.*?)(?=\n## |\Z)", text, re.S)
    if mt:
        transcript = mt.group(1).strip()

    return {
        "title": title,
        "url": url or (f"https://www.youtube.com/watch?v={video_id_from(url or text)}" if url else ""),
        "channel": channel,
        "view_count": _count(field("Views")),
        "duration": field("Length"),
        "description": desc[:500],
        "transcript": transcript,
    }


# ---------------------------------------------------------------------------
# forensic record — same shape dissect_url produces
# ---------------------------------------------------------------------------


def video_id_from(text: str) -> str:
    """Best-effort YouTube id from a URL in the text (else content hash)."""
    for pat in (
        r"(?:v=)([A-Za-z0-9_-]{11})",
        r"(?:youtu\.be/)([A-Za-z0-9_-]{11})",
        r"(?:shorts/)([A-Za-z0-9_-]{11})",
    ):
        m = re.search(pat, text or "")
        if m:
            return m.group(1)
    return ""


def ingest_text(text: str, *, source: str = "") -> dict:
    """Raw text -> forensic record (dissect_url-compatible keys)."""
    kind = detect_kind(text)
    vid = video_id_from(text)
    base = {
        "source": source or f"ingest:{kind}",
        "url": f"https://www.youtube.com/watch?v={vid}" if vid else "",
        "title": "",
        "channel": "",
        "description": "",
        "view_count": "0",
        "duration": "",
        "has_transcript": False,
    }
    if kind == "fetch_page":
        parsed = parse_fetch_page(text)
        base.update({
            "title": parsed["title"],
            "url": parsed["url"] or base["url"],
            "channel": parsed["channel"],
            "view_count": parsed["view_count"],
            "duration": parsed["duration"],
            "description": parsed["description"],
        })
        transcript = parsed["transcript"]
    elif kind == "vtt":
        transcript = parse_vtt(text)
    elif kind == "srt":
        transcript = parse_srt(text)
    else:
        transcript = text.strip()
    words = transcript.split()
    base.update({
        "transcript_chars": len(transcript),
        "transcript_words": len(words),
        "transcript": transcript[:5000],
        "has_transcript": bool(transcript),
        "kind": kind,
    })
    if not vid:
        digest = hashlib.sha1(transcript.encode("utf-8")).hexdigest()[:11]
        base["video_id"] = digest
    else:
        base["video_id"] = vid
    return base


def ingest_file(path: str | Path) -> dict:
    p = Path(path)
    if not p.is_file():
        raise ValueError(f"This is missing, could you provide it: {p}")
    return ingest_text(p.read_text(encoding="utf-8-sig"), source=f"ingest:{p.name}")


def save_transcript(record: dict, out_dir: str | Path) -> Path:
    """record -> transcripts/<video_id>.txt (plain text, pipeline-ready)."""
    if not record.get("has_transcript"):
        raise ValueError("record has no transcript to save")
    d = Path(out_dir)
    d.mkdir(parents=True, exist_ok=True)
    p = d / f"{record.get('video_id', 'unknown')}.txt"
    header = (
        f"# {record.get('title', '')}\n"
        f"# {record.get('url', '')}\n"
        f"# {record.get('channel', '')} | views {record.get('view_count', '0')}"
        f" | {record.get('duration', '')}\n\n"
    )
    p.write_text(header + record["transcript"] + "\n", encoding="utf-8")
    return p
