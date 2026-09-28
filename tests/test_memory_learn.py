"""Tests for session memory (save/restore) and the learning loop (learn)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from monarch.cli import main
from monarch.core.learn import (
    PERFORMANCE_FILE,
    PerformanceRecord,
    consolidate,
    distill,
    load_performance,
    record_performance,
)
from monarch.core.memory import MEMORY_VERSION, format_state, load_state, save_state
from monarch.core.state_machine import STATES


# ---------------------------------------------------------------------------
# PerformanceRecord — fail-closed numbers
# ---------------------------------------------------------------------------


def test_record_rejects_bad_numbers():
    with pytest.raises(ValueError):
        PerformanceRecord(topic="", views=10, avg_pct=50)
    with pytest.raises(ValueError):
        PerformanceRecord(topic="x", views=-1, avg_pct=50)
    with pytest.raises(ValueError):
        PerformanceRecord(topic="x", views=10, avg_pct=150)
    with pytest.raises(ValueError):
        PerformanceRecord(topic="x", views=10, avg_pct=50, subs=-3)


def test_record_defaults_date_and_validates_roundtrip(tmp_path: Path):
    rec = PerformanceRecord(topic="the deep sea", views=1000, avg_pct=62.5,
                            cohort="genz", length_s=58)
    assert rec.date  # today, UTC
    p = record_performance(rec, tmp_path / "perf.jsonl")
    recs = load_performance(p)
    assert len(recs) == 1
    assert recs[0].topic == "the deep sea"
    assert recs[0].avg_pct == 62.5
    assert recs[0].cohort == "genz"


def test_load_corrupt_line_fails_loudly(tmp_path: Path):
    p = tmp_path / "perf.jsonl"
    p.write_text(
        json.dumps({"topic": "a", "views": 1, "avg_pct": 50}) + "\n" + "{broken\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError) as exc:
        load_performance(p)
    assert "line 2" in str(exc.value)


def test_load_missing_log_is_empty(tmp_path: Path):
    assert load_performance(tmp_path / "nope.jsonl") == []


# ---------------------------------------------------------------------------
# distill — the median split
# ---------------------------------------------------------------------------


def _rec(topic, pct, cohort, length):
    return PerformanceRecord(topic=topic, views=1000, avg_pct=pct,
                             cohort=cohort, length_s=length)


def test_distill_needs_three_videos():
    report = distill([_rec("a", 70, "genz", 60), _rec("b", 40, "kids", 30)])
    assert report.status == "need_more"
    assert report.lessons == []


def test_distill_finds_cohort_signal():
    recs = [
        _rec("winner genz a", 85, "genz", 58),
        _rec("winner genz b", 78, "genz", 62),
        _rec("loser kids a", 30, "kids", 45),
        _rec("loser kids b", 25, "kids", 40),
    ]
    report = distill(recs)
    assert report.status == "learned"
    assert any("genz" in les and "kids" in les for les in report.lessons)
    assert all("provisional" in les for les in report.lessons)  # honest wording


def test_distill_finds_runtime_signal():
    recs = [
        _rec("long a", 80, "genz", 70),
        _rec("long b", 75, "kids", 68),
        _rec("short a", 30, "kids", 25),
        _rec("short b", 28, "genz", 30),
    ]
    report = distill(recs)
    assert report.status == "learned"
    assert any("runtime" in les for les in report.lessons)


def test_distill_no_signal_when_identical():
    recs = [_rec(f"same {i}", 50, "genz", 60) for i in range(4)]
    report = distill(recs)
    assert report.status == "no_signal"
    assert consolidate(report) == 0  # nothing written on no_signal


def test_consolidate_writes_lessons_3x_rule(tmp_path: Path):
    recs = [
        _rec("w a", 85, "genz", 58),
        _rec("w b", 78, "genz", 62),
        _rec("l a", 30, "kids", 45),
        _rec("l b", 25, "kids", 40),
    ]
    report = distill(recs)
    lessons_path = tmp_path / "lessons.md"
    written = consolidate(report, lessons_path)
    assert written == len(report.lessons) > 0
    text = lessons_path.read_text(encoding="utf-8")
    assert "retention_signal" in text
    assert "3x rule" in text


# ---------------------------------------------------------------------------
# memory — save / load / format
# ---------------------------------------------------------------------------


def test_memory_roundtrip(tmp_path: Path):
    lessons = tmp_path / "lessons.md"
    lessons.write_text("# Lessons\n\n- 2026-01-01T00:00:00Z | miss: x | 3x rule: y\n",
                       encoding="utf-8")
    perf = tmp_path / "perf.jsonl"
    perf.write_text(json.dumps(_rec("deep sea", 71, "genz", 58).to_dict()) + "\n",
                    encoding="utf-8")
    mem = tmp_path / "memory.json"
    p, doc = save_state(
        path=mem, m_state="M3_script", pending=["approve board"],
        notes=["use seed 9"], topic="the deep sea",
        lessons_path=lessons, perf_path=perf,
    )
    assert p == mem
    assert doc["version"] == MEMORY_VERSION
    assert doc["m_state"] == "M3_script"
    assert doc["wait_for"] == "perfect | improve"
    assert doc["lessons"]["rules"] == 1
    assert doc["performance"]["videos"] == 1
    assert doc["performance"]["best"]["topic"] == "deep sea"

    loaded = load_state(mem)
    assert loaded["m_state"] == "M3_script"
    assert loaded["pending"] == ["approve board"]
    card = format_state(loaded)
    assert "M3_script" in card and "approve board" in card


def test_memory_embeds_channel(tmp_path: Path):
    ch = tmp_path / "channel.yaml"
    ch.write_text('id: test-ch\nniche: history mysteries\naspect: "9:16"\n'
                  'language: ur\n', encoding="utf-8")
    p, doc = save_state(path=tmp_path / "m.json", channel_path=ch)
    assert doc["channel"]["id"] == "test-ch"
    assert doc["channel"]["niche"] == "history mysteries"
    assert doc["channel"]["aspect"] == "9:16"


def test_memory_fail_closed_missing():
    with pytest.raises(ValueError) as exc:
        load_state("/nonexistent/memory.json")
    assert "This is missing" in str(exc.value)


def test_memory_fail_closed_corrupt(tmp_path: Path):
    p = tmp_path / "memory.json"
    p.write_text("{not json", encoding="utf-8")
    with pytest.raises(ValueError):
        load_state(p)


def test_memory_fail_closed_bad_version(tmp_path: Path):
    p = tmp_path / "memory.json"
    p.write_text(json.dumps({"version": 99, "m_state": "M3_script"}), encoding="utf-8")
    with pytest.raises(ValueError):
        load_state(p)


def test_memory_fail_closed_bad_state(tmp_path: Path):
    p = tmp_path / "memory.json"
    p.write_text(json.dumps({"version": MEMORY_VERSION, "m_state": "M99_bogus"}),
                 encoding="utf-8")
    with pytest.raises(ValueError):
        load_state(p)


def test_memory_save_rejects_unknown_state(tmp_path: Path):
    with pytest.raises(ValueError):
        save_state(path=tmp_path / "m.json", m_state="M99_bogus")


def test_memory_states_match_state_machine(tmp_path: Path):
    """Every snapshot state must be a real M-state."""
    for state in STATES:
        p, doc = save_state(path=tmp_path / "m.json", m_state=state)
        assert doc["m_state"] == state


# ---------------------------------------------------------------------------
# CLI wiring
# ---------------------------------------------------------------------------


def test_cli_memory_save_and_restore(tmp_path, capsys):
    out = tmp_path / "memory.json"
    rc = main(["memory", "save", "--state", "M3_script", "--topic", "deep sea",
               "--pending", "approve board", "--out", str(out)])
    assert rc == 0
    assert "MONARCH MEMORY" in capsys.readouterr().out
    rc = main(["memory", "restore", str(out)])
    assert rc == 0
    assert "approve board" in capsys.readouterr().out


def test_cli_memory_restore_missing_fails(tmp_path, capsys):
    rc = main(["memory", "restore", str(tmp_path / "nope.json")])
    assert rc == 2
    assert "FAIL" in capsys.readouterr().out


def test_cli_learn_record_log_distill(tmp_path, capsys):
    perf = tmp_path / "perf.jsonl"
    lessons = tmp_path / "lessons.md"
    rows = [
        ("win a", 85, "genz", 58), ("win b", 78, "genz", 62),
        ("lose a", 30, "kids", 45),
    ]
    for topic, pct, cohort, length in rows:
        rc = main(["learn", "record", "--topic", topic, "--views", "1000",
                   "--avg-pct", str(pct), "--cohort", cohort,
                   "--length", str(length), "--file", str(perf)])
        assert rc == 0
    capsys.readouterr()
    rc = main(["learn", "log", "--file", str(perf)])
    assert rc == 0
    assert "win a" in capsys.readouterr().out
    rc = main(["learn", "distill", "--apply", "--file", str(perf),
               "--lessons", str(lessons)])
    out = capsys.readouterr().out
    assert rc == 0
    assert "LEARNED" in out
    assert "genz" in lessons.read_text(encoding="utf-8")


def test_cli_learn_record_rejects_bad_pct(tmp_path, capsys):
    rc = main(["learn", "record", "--topic", "x", "--views", "10",
               "--avg-pct", "250", "--file", str(tmp_path / "p.jsonl")])
    assert rc == 2
    assert "FAIL" in capsys.readouterr().out


def test_cli_learn_distill_need_more(tmp_path, capsys):
    perf = tmp_path / "perf.jsonl"
    perf.write_text(json.dumps(_rec("a", 50, "genz", 60).to_dict()) + "\n",
                    encoding="utf-8")
    rc = main(["learn", "distill", "--file", str(perf)])
    assert rc == 0
    assert "NEED MORE" in capsys.readouterr().out


def test_performance_default_path_is_project_local():
    assert str(PERFORMANCE_FILE).startswith(".monarch")
