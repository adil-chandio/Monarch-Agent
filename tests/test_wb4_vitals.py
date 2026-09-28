"""W-B4 tests - engaged-class vitals + the repurpose queue.

The scoreboard discipline (ABYSS A): engaged views are the only ones
that pay; the sheet never fakes numbers (missing = [fill]); band
verdicts come straight from the 2026 research. The queue skeleton
honors the 5-15 law, the 22-45 s band, and the condensed-incomplete
payoff-tease (cut BEFORE the reveal).
"""

from __future__ import annotations

import json

import pytest

from monarch.cli import main
from monarch.video.pipeline import make_video
from monarch.video.vitals import (evaluate_vitals, queue_md, repurpose_queue,
                                  sheet_md)


@pytest.fixture(scope="module")
def render_dir(tmp_path_factory):
    d = tmp_path_factory.mktemp("wb4") / "out"
    make_video("polar is fake king", d, length=10.5, fps=1, seed=61,
               voice_backend="mumble", do_mix=True)
    return d


# ---------------------------------------------------------------------------
# vitals evaluation
# ---------------------------------------------------------------------------


def test_dead_channel_earns_p1s():
    v = evaluate_vitals(impressions=10000, clicks=120,          # CTR 1.2%
                        public_views=50000, engaged_views=22000,  # 2.27x
                        viewed=2600, swiped=7400,               # 26.0%
                        avp_pct=42.0, returning_pct=6.0)
    assert v["ok"] is False and v["score"] <= 40
    pris = [f["priority"] for f in v["findings"]]
    assert pris.count("P1") == 2                    # CTR critical + swipe dead
    assert any("critical" in f["finding"] for f in v["findings"])
    assert any("dead" in f["finding"] for f in v["findings"])
    assert any("bounce-heavy" in f["finding"] for f in v["findings"])
    assert v["ratios"]["ctr"] == 1.2
    assert v["ratios"]["swipe_through"] == 26.0


def test_strong_channel_scores_full():
    v = evaluate_vitals(impressions=10000, clicks=1100,         # 11%
                        public_views=30000, engaged_views=19000,  # 1.58x
                        viewed=7200, swiped=2800,               # 72%
                        avp_pct=74.0, returning_pct=28.0)
    assert v["ok"] is True and v["score"] == 100
    assert all(f["priority"] == "OK" for f in v["findings"])
    assert any("velocity gate" in f["finding"] for f in v["findings"])


def test_empty_input_is_advisory_never_fake():
    v = evaluate_vitals()
    assert v["advisory_only"] is True and v["ok"] is None
    assert "fill from Studio" in v["note"]
    assert v["findings"] == []


def test_sheet_md_honest_placeholders_and_laws():
    v = evaluate_vitals(viewed=7200, swiped=2800)
    md = sheet_md(v, title="The Bear")
    assert "[fill from Studio]" in md
    assert "ENGAGED" in md and "2026-08-24" in md          # the split law
    assert "Sponsor decks quote ENGAGED" in md
    assert "72.0%" in md                                    # the real verdict


# ---------------------------------------------------------------------------
# repurpose queue
# ---------------------------------------------------------------------------


BOARD = [
    {"id": 1, "retention_role": "hook",
     "vo_line": "Stop scrolling. This bear ranked HIMSELF.",
     "neuro_driver": "N1 THUMB-STOP", "t_start": 0, "t_end": 2.5},
    {"id": 2, "retention_role": "body",
     "vo_line": "But the pride never approved it.",
     "neuro_driver": "N4 VALUE-DEBT", "t_start": 2.5, "t_end": 5},
    {"id": 3, "retention_role": "payoff+cua",
     "vo_line": "The crown was fake all along.",
     "neuro_driver": "N3 ESCALATE", "t_start": 5, "t_end": 8},
]


def test_queue_concepts_and_order():
    q = repurpose_queue(BOARD, title="The Bear Who Ranked HIMSELF?!",
                        n=6, topics=["Panda", "Sun", "Sloth", "Polar",
                                     "Grizzly"])
    concepts = [i["concept"] for i in q]
    assert concepts[0] == "hook-remix"
    assert "payoff-tease" in concepts
    assert "wtf-detail" in concepts
    assert "loop-cut" in concepts
    assert "ranking-teaser" in concepts
    assert len(q) <= 6
    assert all(i["band"].startswith("22-45s") for i in q)
    assert all("DIFFERENT topic" in i["anti_slop"] or
               "new ranking" in i["anti_slop"] or
               "same grammar" in i["anti_slop"] for i in q)


def test_payoff_tease_cuts_before_the_reveal():
    q = repurpose_queue(BOARD, title="The Bear", n=6)
    tease = next(i for i in q if i["concept"] == "payoff-tease")
    assert "BEFORE the reveal" in tease["why"]
    assert "never on the answer" in tease["cut_note"]


def test_queue_laws_fail_closed():
    with pytest.raises(ValueError, match="refuses"):
        repurpose_queue([])
    with pytest.raises(ValueError, match="5-15"):
        repurpose_queue(BOARD, n=0)
    with pytest.raises(ValueError, match="5-15"):
        repurpose_queue(BOARD, n=16)


def test_queue_md_carries_the_laws():
    md = queue_md(repurpose_queue(BOARD, n=4), title="The Bear")
    assert "22-45 s" in md
    assert "HAAN" in md                                    # upload gate
    assert "GRAMMAR" in md                                 # anti-slop law


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def test_cli_vitals_verdicts_and_save(render_dir, capsys):
    rc = main(["vitals", str(render_dir), "--viewed", "7200",
               "--swiped", "2800", "--save"])
    out = capsys.readouterr().out
    assert rc == 0 and "velocity gate" in out
    assert (render_dir / "kit" / "vitals_sheet.md").is_file()
    rc2 = main(["vitals", str(render_dir), "--viewed", "100",
                "--swiped", "900"])
    assert rc2 == 2 and "dead" in capsys.readouterr().out


def test_cli_repurpose_writes_queue(render_dir, capsys):
    rc = main(["repurpose", str(render_dir), "--n", "5",
               "--topics", "Panda,Sun,Sloth,Polar,Grizzly",
               "--title", "The Bear Who Ranked HIMSELF?!"])
    out = capsys.readouterr().out
    assert rc == 0 and "hook-remix" in out and "saved:" in out
    md = (render_dir / "kit" / "repurpose_queue.md").read_text(
        encoding="utf-8")
    assert "ranking-teaser" in md and "censor" in md
    rc2 = main(["repurpose", str(render_dir), "--n", "99"])
    assert rc2 == 2 and "5-15" in capsys.readouterr().out


def test_cli_repurpose_missing_dir(tmp_path, capsys):
    rc = main(["repurpose", str(tmp_path / "ghost")])
    assert rc == 2 and "FAIL" in capsys.readouterr().out
