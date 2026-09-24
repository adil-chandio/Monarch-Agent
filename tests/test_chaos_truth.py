"""W2 CHAOS tests — freshness half-life scoring + link-rot guard."""

from __future__ import annotations

import json
from datetime import datetime, timezone

import pytest

from monarch.cli import main
from monarch.pipelines.deep_forensic import (
    HALF_LIFE_DAYS,
    LINKROT_AT,
    analyze_dossier,
    analyze_video,
    load_dossier,
    recency_factor,
)

TODAY = datetime(2026, 9, 24, tzinfo=timezone.utc)


def test_recency_factor_half_life_math():
    fresh = recency_factor("2026-09-24", today=TODAY)          # age 0
    half = recency_factor("2026-06-11", today=TODAY)           # ~105d = 1 HL
    quarter = recency_factor("2026-02-26", today=TODAY)        # ~210d = 2 HL
    assert fresh == pytest.approx(1.0)
    assert half == pytest.approx(0.5, abs=0.02)
    assert quarter == pytest.approx(0.25, abs=0.02)
    # shorter half-life decays harder
    fast = recency_factor("2026-06-11", today=TODAY, half_life=30.0)
    assert fast < half


def test_recency_none_when_no_date():
    assert recency_factor("") is None
    assert recency_factor("not-a-date") is None


def test_analyze_video_sets_freshness_fields():
    base = dict(id="v1", title="t", channel="c", views=1000.0,
                duration_s=60.0, transcript="The file sat unopened. "
                "Nobody signed the last page at all.", likes=10.0)
    a = analyze_video(type("V", (), {**base, "date": "2026-09-24",
                                     "thumb_note": ""})(), today=TODAY)
    assert a.age_days == 0.0 and a.recency == 1.0
    b = analyze_video(type("V", (), {**base, "date": "",
                                     "thumb_note": ""})(), today=TODAY)
    assert b.age_days == -1.0 and b.recency == 1.0    # honest neutral


def _dossier(tmp_path, dates):
    vids = []
    for i, d in enumerate(dates, 1):
        vids.append({
            "id": f"vid{i:011d}"[:12] + str(i), "title": f"Secret file {i} nobody shows...",
            "channel": "ch", "views": 1000.0 * i, "likes": 50.0,
            "duration_s": 300.0, "transcript":
                ("you the file sat unopened for years and nobody signed it "
                 f"number {i} proof inside this room of records " * 8),
            "date": d,
        })
    p = tmp_path / "d.json"
    p.write_text(json.dumps({"niche": "files", "videos": vids}), encoding="utf-8")
    return p


def test_dossier_freshness_pattern_and_linkrot(tmp_path):
    p = _dossier(tmp_path, ["2026-09-01", "2026-09-10", "2020-01-01"])
    niche, videos = load_dossier(p)
    rep = analyze_dossier(niche, videos, today=TODAY)
    assert rep.freshness["dated"] == "3/3"
    assert rep.freshness["median_age_days"] is not None
    line = next(x for x in rep.patterns if x.startswith("freshness:"))
    assert "LINK-ROT RISK 1" in line            # 2020 row > 2x105d
    assert rep.freshness["linkrot_risk_ids"]
    assert all("evidence freshness" in i["evidence"] for i in rep.ideas)


def test_dossier_no_date_is_honest_not_claimed(tmp_path):
    p = _dossier(tmp_path, ["", "", ""])
    niche, videos = load_dossier(p)
    rep = analyze_dossier(niche, videos, today=TODAY)
    assert rep.freshness["dated"] == "0/3"
    assert rep.freshness["median_age_days"] is None
    assert "NO DATE" in rep.freshness["note"]
    assert not any(x.startswith("freshness:") for x in rep.patterns)


def test_fresh_rank_alpha_dominance(tmp_path):
    p = _dossier(tmp_path, ["2026-09-20", "2021-01-01", "2026-09-22"])
    niche, videos = load_dossier(p)
    rep = analyze_dossier(niche, videos, today=TODAY)
    by_views = {a.id: a for a in rep.analyses}
    ranks = sorted(rep.analyses, key=lambda a: -a.fresh_rank)
    # newest + most-viewed must outrank the stale one despite lower views
    assert ranks[-1].age_days > LINKROT_AT * HALF_LIFE_DAYS


def test_cli_deep_forensic_half_life_flag(tmp_path, capsys):
    p = _dossier(tmp_path, ["2026-09-01", "2026-09-10", "2020-01-01"])
    out = tmp_path / "rep"
    rc = main(["deep-forensic", str(p), "--out", str(out), "--half-life", "30"])
    assert rc == 0
    data = json.loads((out / "deep_forensic.json").read_text(encoding="utf-8"))
    assert data["freshness"]["half_life_days"] == 30.0
