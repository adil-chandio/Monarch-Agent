"""Tests for transcript ingest — agent-fetched text -> forensic records."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from monarch.cli import main
from monarch.intel.ingest import (
    detect_kind,
    ingest_file,
    ingest_text,
    parse_fetch_page,
    parse_srt,
    parse_vtt,
    save_transcript,
    video_id_from,
)

# Real shape the platform page-fetcher returns for a YouTube watch page.
FETCH_MD = """# [Me at the zoo](https://www.youtube.com/watch?v=jNQXAC9IVRw)

![Thumbnail (480x360)](https://i.ytimg.com/vi/jNQXAC9IVRw/hqdefault.jpg)

**Visibility**: Public
**Uploaded by**: [jawed](https://www.youtube.com/@jawed)
**Uploaded at**: 2005-04-24
**Length**: 00:19
**Views**: 435,858,102
**Likes**: 19,914,149

## Description

```
00:00 Intro
00:05 The cool thing
```

## Transcript

All right, so here we are, in front of the elephants
the cool thing about these guys is that they have really...
really really long trunks
and that's cool
(baaaaaaaaaaahhh!!)
and that's pretty much all there is to say
"""

VTT = """WEBVTT
Kind: captions
Language: en

00:00:00.000 --> 00:00:02.500
All right, so here we are

00:00:02.500 --> 00:00:05.000
in front of the elephants

00:00:05.000 --> 00:00:08.000
and that's cool
"""

SRT = """1
00:00:00,000 --> 00:00:02,500
All right, so here we are

2
00:00:02,500 --> 00:00:05,000
in front of the elephants

3
00:00:05,000 --> 00:00:08,000
and that's cool
"""


# ---------------------------------------------------------------------------
# detection
# ---------------------------------------------------------------------------


def test_detect_kinds():
    assert detect_kind(FETCH_MD) == "fetch_page"
    assert detect_kind(VTT) == "vtt"
    assert detect_kind(SRT) == "srt"
    assert detect_kind("just some spoken words on a line") == "plain"


# ---------------------------------------------------------------------------
# parsers
# ---------------------------------------------------------------------------


def test_parse_fetch_page_metadata_and_transcript():
    parsed = parse_fetch_page(FETCH_MD)
    assert parsed["title"] == "Me at the zoo"
    assert parsed["channel"] == "jawed"          # link label kept, url dropped
    assert parsed["view_count"] == "435858102"   # commas stripped
    assert parsed["duration"] == "00:19"
    assert "elephants" in parsed["transcript"]
    assert "Intro" in parsed["description"]


def test_parse_vtt_strips_timestamps_and_headers():
    text = parse_vtt(VTT)
    assert "WEBVTT" not in text
    assert "-->" not in text
    assert "00:00" not in text
    assert text == "All right, so here we are in front of the elephants and that's cool"


def test_parse_srt_strips_indexes_and_timestamps():
    text = parse_srt(SRT)
    assert "-->" not in text
    assert text == "All right, so here we are in front of the elephants and that's cool"


def test_video_id_from_urls():
    assert video_id_from("https://www.youtube.com/watch?v=jNQXAC9IVRw") == "jNQXAC9IVRw"
    assert video_id_from("https://youtu.be/jNQXAC9IVRw?t=3") == "jNQXAC9IVRw"
    assert video_id_from("no url here") == ""


# ---------------------------------------------------------------------------
# ingest — the forensic record
# ---------------------------------------------------------------------------


def test_ingest_fetch_page_full_record():
    rec = ingest_text(FETCH_MD)
    assert rec["kind"] == "fetch_page"
    assert rec["title"] == "Me at the zoo"
    assert rec["channel"] == "jawed"
    assert rec["view_count"] == "435858102"
    assert rec["has_transcript"] is True
    assert rec["video_id"] == "jNQXAC9IVRw"
    assert rec["transcript_words"] > 10
    assert rec["url"] == "https://www.youtube.com/watch?v=jNQXAC9IVRw"


def test_ingest_vtt_and_srt_records():
    for raw in (VTT, SRT):
        rec = ingest_text(raw, source="agent")
        assert rec["has_transcript"] is True
        assert rec["transcript_words"] == 14
        assert len(rec["video_id"]) == 11  # content hash fallback
        assert rec["url"] == ""            # no url in captions — honest


def test_ingest_plain_text_passthrough():
    rec = ingest_text("one two three four five")
    assert rec["kind"] == "plain"
    assert rec["transcript"] == "one two three four five"
    assert rec["has_transcript"] is True


def test_ingest_fetch_page_without_transcript_is_honest():
    md = FETCH_MD.split("## Transcript")[0]  # metadata only
    rec = ingest_text(md)
    assert rec["has_transcript"] is False
    assert rec["transcript"] == ""
    assert rec["title"] == "Me at the zoo"   # metadata still extracted


def test_ingest_file_missing_fails(tmp_path):
    with pytest.raises(ValueError):
        ingest_file(tmp_path / "nope.txt")


# ---------------------------------------------------------------------------
# save
# ---------------------------------------------------------------------------


def test_save_transcript_writes_pipeline_ready_txt(tmp_path):
    rec = ingest_text(FETCH_MD)
    p = save_transcript(rec, tmp_path)
    assert p.name == "jNQXAC9IVRw.txt"
    text = p.read_text(encoding="utf-8")
    assert "# Me at the zoo" in text
    assert "elephants" in text


def test_save_transcript_refuses_empty(tmp_path):
    rec = ingest_text(FETCH_MD.split("## Transcript")[0])
    with pytest.raises(ValueError):
        save_transcript(rec, tmp_path)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def test_cli_ingest_file(tmp_path, capsys):
    src = tmp_path / "fetch.txt"
    src.write_text(FETCH_MD, encoding="utf-8")
    rc = main(["transcript-ingest", str(src)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "OK [fetch_page]" in out
    assert "jawed" in out


def test_cli_ingest_json_and_save(tmp_path, capsys):
    src = tmp_path / "fetch.txt"
    src.write_text(FETCH_MD, encoding="utf-8")
    rc = main(["transcript-ingest", str(src), "--json",
               "--save", str(tmp_path / "tx")])
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert data["video_id"] == "jNQXAC9IVRw"
    assert (tmp_path / "tx" / "jNQXAC9IVRw.txt").is_file()


def test_cli_ingest_stdin(tmp_path, capsys, monkeypatch):
    import sys

    monkeypatch.setattr(sys, "stdin", type("S", (), {"read": lambda self: VTT})())
    rc = main(["transcript-ingest", "-"])
    assert rc == 0
    assert "OK [vtt]" in capsys.readouterr().out


def test_cli_ingest_missing_file_fails(capsys):
    rc = main(["transcript-ingest", "/nonexistent/fetch.txt"])
    assert rc == 2
    assert "FAIL" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# skills accuracy: the documented path must reference real commands
# ---------------------------------------------------------------------------


def test_forensic_hunt_skill_documents_ingest_path():
    skill = Path(__file__).resolve().parents[1] / "monarch" / "skills" / "forensic-hunt" / "SKILL.md"
    text = skill.read_text(encoding="utf-8")
    assert "transcript-ingest" in text
