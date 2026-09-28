"""Tests for the youtube-transcript.io client (monarch.intel.ytt) — offline."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from monarch.cli import main
from monarch.intel import ytt


# ---------------------------------------------------------------------------
# id parsing
# ---------------------------------------------------------------------------


def test_parse_raw_ids_and_urls():
    ids = ytt.parse_video_ids([
        "jNQXAC9IVRw",
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://youtu.be/jNQXAC9IVRw?t=3",
        "https://www.youtube.com/shorts/abcdefghijk",
    ])
    assert ids == ["jNQXAC9IVRw", "dQw4w9WgXcQ", "abcdefghijk"]  # deduped


def test_parse_rejects_garbage():
    with pytest.raises(ValueError):
        ytt.parse_video_ids(["not a video id at all"])


def test_parse_empty_ok_for_fetch_guard():
    assert ytt.parse_video_ids([]) == []
    with pytest.raises(ValueError):
        ytt.fetch_transcripts([])  # guard raises before any network


# ---------------------------------------------------------------------------
# flatten — the vendor-agnostic transcript extractor
# ---------------------------------------------------------------------------


def test_flatten_shapes():
    assert ytt.flatten_transcript({"transcript": "hello world"}) == "hello world"
    assert ytt.flatten_transcript(
        {"transcript": [{"text": "one"}, {"text": "two"}]}
    ) == "one two"
    assert ytt.flatten_transcript(
        {"lines": [{"line": "alpha"}, {"line": "beta"}]}
    ) == "alpha beta"
    assert ytt.flatten_transcript({"text": "  spaced  "}) == "spaced"
    assert ytt.flatten_transcript({"nope": 1}) == ""
    assert ytt.flatten_transcript("plain") == "plain"


# ---------------------------------------------------------------------------
# fetch — chunking, ids fallback, 429 retry (injected transport)
# ---------------------------------------------------------------------------


def _capture_transport(calls: list, responses: list):
    def t(endpoint, payload, token):
        calls.append((endpoint, list(payload["ids"]), token))
        return responses[len(calls) - 1]
    return t


def test_fetch_normal_response():
    calls: list = []
    raw = [{"id": "jNQXAC9IVRw",
            "transcript": [{"text": "hello"}, {"text": "world"}]}]
    recs = ytt.fetch_transcripts(["jNQXAC9IVRw"], token="tok",
                                 transport=_capture_transport(calls, [raw]))
    assert calls[0][0] == "transcripts"          # correct endpoint
    assert calls[0][1] == ["jNQXAC9IVRw"]
    assert calls[0][2] == "tok"
    assert recs[0]["transcript"] == "hello world"


def test_fetch_chunks_at_50():
    calls: list = []
    ids = [f"a{i:010}b"[:11] for i in range(105)]
    transport = _capture_transport(calls, [
        [{"id": i, "transcript": "x"} for i in ids[:50]],
        [{"id": i, "transcript": "x"} for i in ids[50:100]],
        [{"id": i, "transcript": "x"} for i in ids[100:]],
    ])
    recs = ytt.fetch_transcripts(ids, token="tok", transport=transport)
    assert [len(c[1]) for c in calls] == [50, 50, 5]  # vendor limit respected
    assert len(recs) == 105


def test_fetch_missing_ids_become_empty_records():
    transport = _capture_transport([], [[{"id": "jNQXAC9IVRw", "transcript": "hi"}]])
    recs = ytt.fetch_transcripts(["jNQXAC9IVRw", "dQw4w9WgXcQ"], token="tok",
                                 transport=transport)
    assert recs[0]["transcript"] == "hi"
    assert recs[1]["transcript"] == ""  # vendor said nothing — empty, not crash


def test_fetch_wrapped_response_shape():
    transport = _capture_transport([], [
        {"transcripts": [{"videoId": "jNQXAC9IVRw", "text": "wrapped"}]}
    ])
    recs = ytt.fetch_transcripts(["jNQXAC9IVRw"], token="tok", transport=transport)
    assert recs[0]["id"] == "jNQXAC9IVRw"
    assert recs[0]["transcript"] == "wrapped"


def test_fetch_retries_once_after_429(monkeypatch):
    import time as _time

    sleeps: list[float] = []
    monkeypatch.setattr(_time, "sleep", lambda s: sleeps.append(s))
    monkeypatch.setattr(ytt.time, "sleep", lambda s: sleeps.append(s))
    attempts = {"n": 0}

    def flaky(endpoint, payload, token):
        attempts["n"] += 1
        if attempts["n"] == 1:
            raise ytt.RateLimited(7)
        return [{"id": "jNQXAC9IVRw", "transcript": "ok"}]

    recs = ytt.fetch_transcripts(["jNQXAC9IVRw"], token="tok", transport=flaky)
    assert attempts["n"] == 2  # exactly one retry
    assert recs[0]["transcript"] == "ok"
    assert sleeps == [7.0]


def test_fetch_channels_endpoint_and_at_strip():
    calls: list = []
    transport = _capture_transport(calls, [[{"id": "jawed", "subs": 1}]])
    out = ytt.fetch_channels(["@jawed", "jawed"], token="tok", transport=transport)
    assert calls[0][0] == "channels"
    assert calls[0][1] == ["jawed"]  # deduped, @ stripped
    assert out == [{"id": "jawed", "subs": 1}]


def test_no_token_fails_closed(monkeypatch):
    monkeypatch.delenv(ytt.TOKEN_ENV, raising=False)
    with pytest.raises(ValueError) as exc:
        ytt.fetch_transcripts(["jNQXAC9IVRw"])
    assert ytt.TOKEN_ENV in str(exc.value)


def test_has_token(monkeypatch):
    monkeypatch.delenv(ytt.TOKEN_ENV, raising=False)
    assert ytt.has_token() is False
    monkeypatch.setenv(ytt.TOKEN_ENV, "tok")
    assert ytt.has_token() is True


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def test_cli_transcript_text_and_save(tmp_path, capsys, monkeypatch):
    monkeypatch.setenv(ytt.TOKEN_ENV, "tok")

    def fake(endpoint, payload, token):
        return [{"id": "jNQXAC9IVRw", "transcript": "the deep sea keeps secrets"}]

    monkeypatch.setattr(ytt, "_post_json", fake)
    out = tmp_path / "tx"
    rc = main(["transcript", "jNQXAC9IVRw", "--save", str(out)])
    assert rc == 0
    text = capsys.readouterr().out
    assert "jNQXAC9IVRw" in text and "deep sea" in text
    assert (out / "jNQXAC9IVRw.txt").is_file()


def test_cli_transcript_json(tmp_path, capsys, monkeypatch):
    monkeypatch.setenv(ytt.TOKEN_ENV, "tok")
    monkeypatch.setattr(ytt, "_post_json", lambda e, p, t:
                        [{"id": "jNQXAC9IVRw", "transcript": "hi"}])
    rc = main(["transcript", "https://youtu.be/jNQXAC9IVRw", "--json"])
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert data[0]["chars"] == 2


def test_cli_transcript_no_token_fails(capsys, monkeypatch):
    monkeypatch.delenv(ytt.TOKEN_ENV, raising=False)
    rc = main(["transcript", "jNQXAC9IVRw"])
    assert rc == 2
    assert "FAIL" in capsys.readouterr().out


def test_cli_transcript_bad_id_fails(capsys, monkeypatch):
    monkeypatch.setenv(ytt.TOKEN_ENV, "tok")
    rc = main(["transcript", "garbage-input"])
    assert rc == 2
    assert "FAIL" in capsys.readouterr().out


def test_cli_keys_reports_transcript_backend(capsys, monkeypatch):
    monkeypatch.setenv(ytt.TOKEN_ENV, "tok")
    rc = main(["keys"])
    assert rc == 0
    assert json.loads(capsys.readouterr().out)["youtube_transcript_io"] is True


# ---------------------------------------------------------------------------
# forensic fallback
# ---------------------------------------------------------------------------


def test_forensic_uses_hosted_transcript_fallback(monkeypatch):
    """scrape --transcript works without yt-dlp when the token exists."""
    from monarch.pipelines import forensic

    class FakeYT:
        @staticmethod
        def video_info(url):
            return {"title": "T", "channel": "C", "description": "d",
                    "view_count": "1", "duration": "60"}

        @staticmethod
        def video_transcript(url, lang="en"):
            raise RuntimeError("yt-dlp missing")

    monkeypatch.setitem(__import__("sys").modules,
                        "monarch.intel.youtube", FakeYT)
    monkeypatch.setattr(ytt, "has_token", lambda: True)
    monkeypatch.setattr(ytt, "fetch_transcripts",
                        lambda ids, **kw: [{"id": ids[0], "transcript": "hosted words"}])
    result = forensic._dissect_youtube("https://youtu.be/jNQXAC9IVRw")
    assert result["has_transcript"] is True
    assert "hosted words" in result["transcript"]


def test_forensic_fallback_silent_without_token(monkeypatch):
    from monarch.pipelines import forensic

    class FakeYT:
        @staticmethod
        def video_info(url):
            return {"title": "T"}

        @staticmethod
        def video_transcript(url, lang="en"):
            raise RuntimeError("yt-dlp missing")

    monkeypatch.setitem(__import__("sys").modules,
                        "monarch.intel.youtube", FakeYT)
    monkeypatch.delenv(ytt.TOKEN_ENV, raising=False)
    result = forensic._dissect_youtube("https://youtu.be/jNQXAC9IVRw")
    assert result["has_transcript"] is False  # honest empty, no crash
