"""Forensic pipeline — competitor DNA extraction using Agent-Reach tools.

Uses yt-dlp for YouTube transcripts, web_read for competitor pages,
and structured analysis for DNA extraction.
"""

from __future__ import annotations

import json
from pathlib import Path

from monarch.core.missing import missing


def dissect(transcript_path: str) -> dict:
    """Analyze a local transcript file."""
    p = Path(transcript_path)
    if not p.exists():
        raise FileNotFoundError(missing(f"transcript at {transcript_path}"))
    text = p.read_text(encoding="utf-8")
    words = text.split()
    return {"path": str(p), "chars": len(text), "words": len(words)}


def dissect_url(url: str) -> dict:
    """Analyze a YouTube video or web page via Agent-Reach.

    Auto-detects: YouTube URLs get transcripts, others get web_read.
    """
    if "youtube.com" in url or "youtu.be" in url:
        return _dissect_youtube(url)
    else:
        return _dissect_web(url)


def _dissect_youtube(url: str) -> dict:
    """Extract transcript + metadata from a YouTube video."""
    from monarch.intel.youtube import video_info, video_transcript

    info = video_info(url)
    transcript = ""
    try:
        transcript = video_transcript(url)
    except RuntimeError:
        pass  # transcript may not be available

    words = transcript.split() if transcript else []
    return {
        "source": "youtube",
        "url": url,
        "title": info.get("title", ""),
        "channel": info.get("channel", ""),
        "description": info.get("description", "")[:500],
        "view_count": info.get("view_count", "0"),
        "duration": info.get("duration", ""),
        "transcript_chars": len(transcript),
        "transcript_words": len(words),
        "transcript": transcript[:5000] if transcript else "",
        "has_transcript": bool(transcript),
    }


def _dissect_web(url: str) -> dict:
    """Extract content from a web page."""
    from monarch.intel.web import extract_competitor_page

    return extract_competitor_page(url)


def dissect_multiple(urls: list[str]) -> list[dict]:
    """Analyze multiple URLs. Stops on first error (fail-closed)."""
    results = []
    for url in urls:
        results.append(dissect_url(url))
    return results


def extract_dna_from_transcripts(results: list[dict]) -> dict:
    """Extract viral DNA patterns from competitor transcripts.

    Analyzes: hook patterns, sentence rhythm, retention structure.
    """
    hooks = []
    structures = []
    for r in results:
        transcript = r.get("transcript", "")
        if not transcript:
            continue
        lines = transcript.splitlines()
        # First line = hook
        if lines:
            hooks.append(lines[0].strip())
        # Structure = how many distinct beats
        structures.append(len([l for l in lines if l.strip()]))

    return {
        "hooks_sampled": hooks[:10],
        "avg_beats": sum(structures) / len(structures) if structures else 0,
        "sources_analyzed": len([r for r in results if r.get("has_transcript")]),
        "total_sources": len(results),
    }
