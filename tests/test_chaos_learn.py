"""W1 CHAOS tests — Studio CSV ingest + Learn 2.0 lesson hygiene."""

from __future__ import annotations

import json
from datetime import datetime, timezone

import pytest

from monarch.cli import main
from monarch.core.lesson_hygiene import hygiene, parse_lessons
from monarch.core.learn import PerformanceRecord, load_performance
from monarch.core import lesson_hygiene as lh
from monarch.pipelines.performance import csv_records, ingest_csv

CSV_COMMA = (
    "Video title,Video views,Average percentage viewed,Subscribers gained,"
    "Video published At,Video duration\n"
    '"the buried file, part 1","1,234",45.6%,12,2026-09-01,3:25\n'
    '"the buried file, part 2",5678,"38.2%",0,2026-09-10,0:58\n'
)
CSV_TAB = (
    "Content\tViews\tAvg percentage viewed\tDate\n"
    "\u0644\u0648\u06af \u06a9\u06cc\u0627 \u06a9\u06c1\u06cc\u06ba\u06af\u06d2\t9200\t52.3%\t2026-09-20\n"
)
CSV_BAD = "foo,bar\n1,2\n"


def _n_records():
    return csv_records(CSV_COMMA)


def test_csv_parses_commas_percent_and_duration():
    recs = _n_records()
    assert len(recs) == 2
    r1, r2 = recs
    assert r1.views == 1234.0
    assert r1.avg_pct == pytest.approx(45.6)
    assert r1.subs == 12
    assert r1.length_s == pytest.approx(205.0)   # 3:25
    assert r2.length_s == pytest.approx(58.0)
    assert r1.topic == "the buried file, part 1"  # comma survived quoting


def test_csv_tab_delimited_and_cohort():
    recs = csv_records(CSV_TAB, cohort="genz")
    assert len(recs) == 1
    assert recs[0].views == 9200.0
    assert recs[0].cohort == "genz"
    assert recs[0].avg_pct == pytest.approx(52.3)


def test_csv_fail_closed_unknown_header():
    with pytest.raises(ValueError) as e:
        csv_records(CSV_BAD)
    assert "unrecognized export" in str(e.value)


def test_csv_fail_closed_bad_row_keeps_line_info():
    bad = ("Video title,Views,Average percentage viewed\n"
           "ok video,100,50%\n"
           "broken row,not-a-number,40%\n")
    with pytest.raises(ValueError) as e:
        csv_records(bad)
    assert "row 3" in str(e.value)


def test_csv_skips_totals_and_empty_but_not_all():
    mixed = ("Video title,Views,Average percentage viewed\n"
             "real one,500,60%\n"
             "Totals,9999,55%\n")
    recs = csv_records(mixed)
    assert [r.topic for r in recs] == ["real one"]


def test_ingest_csv_reads_file(tmp_path):
    p = tmp_path / "studio.csv"
    p.write_text(CSV_COMMA, encoding="utf-8")
    recs = ingest_csv(p)
    assert len(recs) == 2


# ---------------------------------------------------------------------------
# lesson hygiene
# ---------------------------------------------------------------------------


def _entry(stamp, miss, rule):
    return lh.LessonEntry(stamp=stamp, miss=miss, rule=rule)


def test_parse_lessons_counts_skipped():
    text = (
        "# Lessons\n\n"
        "- 2026-09-01T10:00:00Z | miss: hook | 3x rule: open with a number\n"
        "some stray line\n"
        "- 2026-09-02T10:00:00Z | miss: pacing | 3x rule: 65-95 words per 30s\n"
    )
    entries, skipped = lh.parse_lessons(text)
    assert len(entries) == 2
    assert skipped == 1


def test_hygiene_confirmed_provisional_stale():
    today = datetime(2026, 9, 24, tzinfo=timezone.utc)
    entries = [
        _entry("2026-09-20T00:00:00Z", "hook", "number openers win")     # 1
        for _ in range(3)
    ] + [
        _entry("2026-09-22T00:00:00Z", "pacing", "faster is better"),    # 1, fresh
        _entry("2026-01-01T00:00:00Z", "length", "60s sweetspot"),       # 1, old
    ]
    rep = lh.hygiene(entries, today=today)
    assert rep.confirmed == 1
    assert rep.provisional == 1
    assert rep.stale == 1
    assert rep.conflicts == []
    by = {r["rule"]: r["status"] for r in rep.rows}
    assert by["number openers win"] == "confirmed"
    assert by["faster is better"] == "provisional"
    assert by["60s sweetspot"] == "stale"


def test_hygiene_flags_confirmed_conflicts():
    today = datetime(2026, 9, 24, tzinfo=timezone.utc)
    entries = (
        [_entry("2026-09-2%dT00:00:00Z" % d, "hook", "short hooks win") for d in (1, 2, 3)]
        + [_entry("2026-09-2%dT00:00:00Z" % d, "hook", "long hooks win") for d in (4, 5, 6)]
    )
    rep = lh.hygiene(entries, today=today)
    assert rep.confirmed == 2
    assert len(rep.conflicts) == 1
    assert "arbitrate" in rep.conflicts[0]


def test_hygiene_fresh_single_is_not_stale():
    today = datetime(2026, 9, 24, tzinfo=timezone.utc)
    rep = lh.hygiene([_entry("2026-09-23T00:00:00Z", "sfx", "riser before payoff")],
                     today=today)
    assert rep.rows[0]["status"] == "provisional"
    assert rep.stale == 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def test_cli_learn_ingest_appends_and_reports(capsys, tmp_path):
    perf = tmp_path / "perf.jsonl"
    studio = tmp_path / "studio.csv"
    studio.write_text(CSV_COMMA, encoding="utf-8")
    rc = main(["learn", "ingest", str(studio), "--cohort", "genz",
               "--file", str(perf)])
    out = capsys.readouterr().out
    assert rc == 0
    assert "INGESTED 2" in out
    lines = perf.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2
    assert json.loads(lines[0])["cohort"] == "genz"


def test_cli_learn_ingest_rejects_garbage(capsys, tmp_path):
    bad = tmp_path / "bad.csv"
    bad.write_text(CSV_BAD, encoding="utf-8")
    rc = main(["learn", "ingest", str(bad), "--file", str(tmp_path / "p.jsonl")])
    out = capsys.readouterr().out
    assert rc == 2
    assert "FAIL" in out and "unrecognized export" in out


def test_cli_learn_hygiene_reports_statuses(capsys, tmp_path):
    lessons = tmp_path / "lessons.md"
    lessons.write_text(
        "# Lessons\n"
        "- 2026-09-20T00:00:00Z | miss: hook | 3x rule: numbers open\n"
        "- 2026-09-21T00:00:00Z | miss: hook | 3x rule: numbers open\n"
        "- 2026-09-22T00:00:00Z | miss: hook | 3x rule: numbers open\n"
        "- 2026-01-01T00:00:00Z | miss: length | 3x rule: 60s only\n",
        encoding="utf-8")
    rc = main(["learn", "hygiene", "--lessons", str(lessons)])
    out = capsys.readouterr().out
    assert rc == 0
    assert "confirmed 1" in out and "stale 1" in out


def test_cli_learn_hygiene_missing_file_fails_closed(capsys, tmp_path):
    rc = main(["learn", "hygiene", "--lessons", str(tmp_path / "nope.md")])
    out = capsys.readouterr().out
    assert rc == 2 and "FAIL" in out


# ---------------------------------------------------------------------------
# W1b hardening (CHAOS MONARCH DoD: >=315 green, fail-closed everywhere)
# ---------------------------------------------------------------------------


def test_ingest_rejects_negative_views(tmp_path):
    p = tmp_path / "bad.csv"
    p.write_text("Video title,Views,Comments,Avg percentage viewed,Subscribers\n"
                 "weird\t-12\t1\t40%\t0\n", encoding="utf-8")
    with pytest.raises(ValueError):
        ingest_csv(p)


def test_hygiene_rows_carry_day_deltas():
    lines = ["- 2025-01-01T10:00:00Z | miss: x1 | 3x rule: y1",
             "- 2025-01-02T10:00:00Z | miss: x1 | 3x rule: y1",
             "- 2025-01-03T10:00:00Z | miss: x1 | 3x rule: y1",
             "- 2026-08-01T10:00:00Z | miss: x1 | 3x rule: y2",
             "- 2026-08-02T10:00:00Z | miss: x1 | 3x rule: y2",
             "- 2026-08-03T10:00:00Z | miss: x1 | 3x rule: y2",
             "- 2026-09-01T10:00:00Z | miss: x2 | 3x rule: y3"]
    entries, skipped = parse_lessons("\n".join(lines))
    assert skipped == 0
    rep = hygiene(entries, today=datetime(2026, 9, 24, tzinfo=timezone.utc))
    by_miss = {r["miss"]: r for r in rep.rows}
    assert by_miss["x2"]["count"] == 1
    assert by_miss["x2"]["status"] == "provisional"
    # same miss + 2 CONFIRMED distinct rules -> operator arbitration (spec)
    x1_rows = [r for r in rep.rows if r["miss"] == "x1"]
    assert len(x1_rows) == 2
    assert len(rep.conflicts) == 1
    assert "x1" in rep.conflicts[0]


def test_performance_record_roundtrip(tmp_path):
    p = tmp_path / "p.jsonl"
    recs = [PerformanceRecord(topic="t1", views=10, avg_pct=40.0, subs=1,
                              cohort="c", length_s=60.0,
                              date="2026-09-01", note="n"),
            PerformanceRecord(topic="t2", views=20, avg_pct=50.0, subs=2,
                              cohort="c", length_s=90.0,
                              date="2026-09-02", note="")]
    p.write_text("\n".join(json.dumps(r.__dict__) for r in recs) + "\n",
                 encoding="utf-8")
    out = load_performance(p)
    assert len(out) == 2 and out[1].views == 20


def test_learn_help_lists_subcommands(capsys):
    with pytest.raises(SystemExit) as e:
        main(["learn", "--help"])
    assert e.value.code == 0
    out = capsys.readouterr().out
    assert "ingest" in out and "hygiene" in out
