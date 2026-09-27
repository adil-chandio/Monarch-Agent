"""Tests for Agent-Reach integration — bridge layer + intel modules."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from monarch.intel.reach import (
    ToolStatus,
    _has,
    _vtt_to_text,
    doctor,
)


# ---------------------------------------------------------------------------
# Tool detection
# ---------------------------------------------------------------------------


def test_has_finds_common_tools():
    """Python should always be available in the test env."""
    assert _has("python") or _has("python3")


def test_has_missing_tool():
    assert not _has("definitely_not_a_real_tool_xyz_123")


# ---------------------------------------------------------------------------
# VTT parser
# ---------------------------------------------------------------------------


def test_vtt_to_text_basic():
    vtt = """WEBVTT

Kind: captions
Language: en

00:00:01.000 --> 00:00:04.000
Hello world

00:00:04.000 --> 00:00:08.000
This is a test
"""
    text = _vtt_to_text(vtt)
    assert "Hello world" in text
    assert "This is a test" in text
    assert "WEBVTT" not in text
    assert "00:00" not in text


def test_vtt_to_text_strips_html():
    vtt = """WEBVTT

00:00:01.000 --> 00:00:04.000
<b>Bold text</b> and <i>italic</i>
"""
    text = _vtt_to_text(vtt)
    assert "<b>" not in text
    assert "</b>" not in text
    assert "Bold text" in text


def test_vtt_to_text_deduplicates():
    vtt = """WEBVTT

00:00:01.000 --> 00:00:04.000
same line

00:00:04.000 --> 00:00:08.000
same line

00:00:08.000 --> 00:00:12.000
different line
"""
    text = _vtt_to_text(vtt)
    lines = text.splitlines()
    # "same line" should appear only once
    assert lines.count("same line") == 1
    assert "different line" in text


# ---------------------------------------------------------------------------
# Doctor
# ---------------------------------------------------------------------------


def test_doctor_returns_statuses():
    statuses = doctor()
    assert len(statuses) >= 5
    names = [s.name for s in statuses]
    assert "yt-dlp" in names
    assert "gh" in names
    for s in statuses:
        assert isinstance(s, ToolStatus)
        assert isinstance(s.available, bool)
        assert isinstance(s.message, str)


def test_doctor_dict_format():
    from monarch.intel.reach import doctor_dict

    d = doctor_dict()
    assert "yt-dlp" in d
    assert "available" in d["yt-dlp"]
    assert "backend" in d["yt-dlp"]


# ---------------------------------------------------------------------------
# YouTube (yt-dlp path) — mocked
# ---------------------------------------------------------------------------


@patch("monarch.intel.reach._has", return_value=True)
@patch("monarch.intel.reach._run")
def test_yt_search_mock(mock_run, mock_has):
    from monarch.intel.reach import yt_search

    mock_run.return_value = MagicMock(
        returncode=0,
        stdout=json.dumps({
            "id": "abc123",
            "title": "Test Video",
            "channel": "Test Channel",
            "url": "https://youtube.com/watch?v=abc123",
            "duration": 120,
        }),
        stderr="",
    )
    results = yt_search("test query", max_results=1)
    assert len(results) == 1
    assert results[0]["video_id"] == "abc123"
    assert results[0]["title"] == "Test Video"


@patch("monarch.intel.reach._has", return_value=False)
def test_yt_search_no_ytdlp(mock_has):
    from monarch.intel.reach import yt_search

    with pytest.raises(RuntimeError, match="yt-dlp not installed"):
        yt_search("test")


# ---------------------------------------------------------------------------
# Web (Jina Reader) — mocked
# ---------------------------------------------------------------------------


@patch("monarch.intel.reach._run")
def test_web_read_mock(mock_run):
    from monarch.intel.reach import web_read

    mock_run.return_value = MagicMock(
        returncode=0,
        stdout="# Test Page\n\nHello world content.",
        stderr="",
    )
    text = web_read("https://example.com")
    assert "Test Page" in text
    assert "Hello world" in text


# ---------------------------------------------------------------------------
# Intel modules — integration smoke tests
# ---------------------------------------------------------------------------


def test_intel_modules_importable():
    """All new intel modules should be importable."""
    from monarch.intel import reach
    from monarch.intel.twitter import extract_language_patterns, extract_titles, search_niche
    from monarch.intel.reddit import extract_language_patterns, extract_pain_points, search_niche
    from monarch.intel.web import extract_competitor_page, read_url, search_web

    assert callable(search_niche)
    assert callable(read_url)
    assert callable(search_web)


def test_twitter_extract_titles():
    from monarch.intel.twitter import extract_titles

    results = [
        {"text": "This is a great hook for a video about cats", "likes": 100},
        {"text": "Short", "likes": 5},
        {"text": "A perfectly sized hook that works well as title", "likes": 50},
    ]
    titles = extract_titles(results)
    assert len(titles) >= 1
    assert all(isinstance(t, str) for t in titles)


def test_reddit_extract_pain_points():
    from monarch.intel.reddit import extract_pain_points

    results = [
        {"title": "Why does nobody talk about this?", "score": 50},
        {"title": "Meme", "score": 1},
        {"title": "How do I fix this problem with X?", "score": 5},
    ]
    points = extract_pain_points(results)
    assert any("?" in p for p in points)


# ---------------------------------------------------------------------------
# Forensic pipeline — URL analysis
# ---------------------------------------------------------------------------


@patch("monarch.intel.youtube.video_info")
@patch("monarch.intel.youtube.video_transcript")
def test_dissect_youtube_mock(mock_transcript, mock_info):
    from monarch.pipelines.forensic import dissect_url

    mock_info.return_value = {
        "title": "Test Video",
        "channel": "Test Channel",
        "description": "A test video",
        "view_count": "1000",
        "duration": "PT2M",
    }
    mock_transcript.return_value = "Hello world this is a test transcript"
    result = dissect_url("https://www.youtube.com/watch?v=abc123")
    assert result["source"] == "youtube"
    assert result["title"] == "Test Video"
    assert result["has_transcript"] is True


def test_dissect_url_web_fallback():
    """Non-YouTube URLs should attempt web_read."""
    from monarch.pipelines.forensic import dissect_url

    with patch("monarch.intel.web.web_read", return_value="# Page Title\nContent here"):
        result = dissect_url("https://example.com")
        assert "title" in result or "content" in result
