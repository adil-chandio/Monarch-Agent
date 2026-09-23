"""Tests for the deep-forensic pipeline — dossier -> DNA -> ideas."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from monarch.cli import main
from monarch.pipelines.deep_forensic import (
    MIN_VIDEOS,
    CompetitorVideo,
    analyze_dossier,
    classify_title,
    load_dossier,
    report_card,
    run_deep_forensic,
)


def _vid(i: int, views: float, **kw) -> dict:
    base = {
        "id": f"v{i:010d}",
        "title": f"Why the deep sea hides monster {i}...",
        "channel": f"channel{i % 3}",
        "views": views,
        "likes": views * 0.04,
        "duration_s": 480.0 + i * 10,
        "date": "2025-06-01",
        "thumb_note": "one face, high contrast",
        # pace ~75 words/30s for even i (in band), ~40 for odd (below band);
        # hooks carry open-loop markers; body has you/numbers
        "transcript": (
            "nobody shows you what is actually down there... "  # hook, open
            "and that secret is why this place terrifies people. "
        ) * 3
        + (
            "You see the number 47 percent in the report from 1968. "
            "Why did they hide it? What happens if you go looking... "
        ) * (55 if i % 2 == 0 else 12),
    }
    base.update(kw)
    return base


def _dossier(tmp_path: Path, videos: list[dict], niche="the deep sea") -> Path:
    p = tmp_path / "dossier.json"
    p.write_text(json.dumps({"niche": niche, "videos": videos}), encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# dossier loading — fail-closed
# ---------------------------------------------------------------------------


def test_load_rejects_missing(tmp_path):
    with pytest.raises(ValueError):
        load_dossier(tmp_path / "nope.json")


def test_load_rejects_too_few(tmp_path):
    p = _dossier(tmp_path, [_vid(1, 1000), _vid(2, 2000)])
    with pytest.raises(ValueError) as e:
        load_dossier(p)
    assert str(MIN_VIDEOS) in str(e.value)


def test_load_rejects_bad_entries(tmp_path):
    bad = _vid(1, 1000)
    bad["views"] = 0
    p = _dossier(tmp_path, [bad, _vid(2, 1000), _vid(3, 1000)])
    with pytest.raises(ValueError) as e:
        load_dossier(p)
    assert "views" in str(e.value)

    bad2 = _vid(1, 1000)
    bad2["transcript"] = ""
    p2 = _dossier(tmp_path, [bad2, _vid(2, 1000), _vid(3, 1000)])
    with pytest.raises(ValueError) as e:
        load_dossier(p2)
    assert "transcript" in str(e.value)


def test_load_rejects_duplicate_ids(tmp_path):
    vids = [_vid(1, 1000), _vid(2, 2000), _vid(3, 3000)]
    vids[1]["id"] = vids[0]["id"]
    p = _dossier(tmp_path, vids)
    with pytest.raises(ValueError):
        load_dossier(p)


# ---------------------------------------------------------------------------
# title formula classification
# ---------------------------------------------------------------------------


def test_classify_title_formulas():
    assert classify_title("This city disappeared...") == "T1"
    assert classify_title("47% of the ocean is untouched") == "T2"
    assert classify_title("What navy seals never tell you") == "T3"
    assert classify_title("Everything you know about sharks is wrong") == "T4"
    assert classify_title("You have been eating shrimp wrong") == "T5"
    assert classify_title("The hidden bunker insiders won't explain") == "T6"
    assert classify_title("Mega shark vs ancient whale") == "T7"
    assert classify_title("The last photos before it disappeared") == "T8"


# ---------------------------------------------------------------------------
# per-video DNA
# ---------------------------------------------------------------------------


def test_analyze_video_zack_band_and_hook():
    fast = CompetitorVideo.from_dict(_vid(0, 1_000_000))
    slow = CompetitorVideo.from_dict(_vid(1, 900_000))
    fa = analyze_dossier("x", [fast, slow, CompetitorVideo.from_dict(_vid(2, 800_000))])
    a = fa.analyses[0]
    assert a.in_zack_band is True
    assert 65 <= a.words_per_30s <= 95
    assert a.hook_open is True          # "nobody ... actually ..." + ellipsis
    assert a.second_person > 0
    assert a.numbers > 0
    assert a.engagement == pytest.approx(0.04, abs=0.001)


def test_hook_is_a_prefix_of_transcript():
    v = CompetitorVideo.from_dict(_vid(0, 500_000))
    from monarch.pipelines.deep_forensic import analyze_video

    a = analyze_video(v)
    assert v.transcript.startswith(a.hook_text.split("...")[0][:40])


# ---------------------------------------------------------------------------
# dossier analysis — patterns, clusters, ideas
# ---------------------------------------------------------------------------


def test_analyze_dossier_produces_patterns_and_ideas(tmp_path):
    vids = [_vid(i, views=10_000_000 - i * 900_000) for i in range(6)]
    niche, videos = load_dossier(_dossier(tmp_path, vids))
    report = analyze_dossier(niche, videos)
    assert report.video_count == 6
    assert report.channel_count == 3
    assert report.outlier_x > 1
    assert len(report.patterns) >= 3
    assert any("N=" in p for p in report.patterns)          # honesty: sample size
    assert any("hooks" in p for p in report.patterns)
    assert report.clusters and report.clusters[0][1] >= 1
    assert len(report.ideas) == 10
    assert all({"title", "hook", "itch", "evidence"} <= set(d) for d in report.ideas)
    assert report.status == "learned"


# ---------------------------------------------------------------------------
# rendering + files
# ---------------------------------------------------------------------------


def test_report_card_and_files(tmp_path):
    vids = [_vid(i, views=5_000_000 - i * 100_000) for i in range(4)]
    report = run_deep_forensic(_dossier(tmp_path, vids), tmp_path / "out")
    card = report_card(report)
    assert "DEEP FORENSIC — THE DEEP SEA" in card
    assert "PATTERNS" in card
    assert "IDEA DRAFTS" in card
    assert "gate-idea" in card
    for name in ("deep_forensic_report.txt", "deep_forensic.json", "ideas.json"):
        assert (tmp_path / "out" / name).is_file()
    data = json.loads((tmp_path / "out" / "deep_forensic.json").read_text())
    assert data["video_count"] == 4
    ideas = json.loads((tmp_path / "out" / "ideas.json").read_text())
    assert len(ideas) == 10


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def test_cli_deep_forensic(tmp_path, capsys):
    p = _dossier(tmp_path, [_vid(i, 3_000_000 - i * 100_000) for i in range(4)])
    rc = main(["deep-forensic", str(p), "--out", str(tmp_path / "out")])
    assert rc == 0
    out = capsys.readouterr().out
    assert "DEEP FORENSIC" in out
    assert "wrote" in out


def test_cli_deep_forensic_bad_dossier_fails(tmp_path, capsys):
    p = tmp_path / "d.json"
    p.write_text(json.dumps({"niche": "x", "videos": []}), encoding="utf-8")
    rc = main(["deep-forensic", str(p), "--out", str(tmp_path / "o")])
    assert rc == 2
    assert "FAIL" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# skill accuracy
# ---------------------------------------------------------------------------


def test_deep_forensic_skill_documents_the_chain():
    skill = (Path(__file__).resolve().parents[1] / "monarch" / "skills"
             / "deep-forensic" / "SKILL.md").read_text(encoding="utf-8")
    for needle in ("transcript-ingest", "deep-forensic", "gate-idea",
                   "15-20", "dossier.json", "make-short", "memory save"):
        assert needle in skill, f"skill must mention {needle!r}"
