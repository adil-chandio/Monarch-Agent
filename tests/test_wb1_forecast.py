"""W-B1 tests - the 9-link chain check + curve forecaster.

DONE criterion (TABAHI_PROTOCOL): a deliberately bad plan FAILS WITH
THE LINK NAMED. Plus: But/Therefore lint, the four curve verdicts
(healthy / hockey_stick / gradual_bleed / camel_humps / peak_too_early),
and the CLI gate (rc 2 names the broken link).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from monarch.cli import main
from monarch.video.forecast import (but_therefore_lint, chain_check,
                                    curve_forecast, verdict)
from monarch.video.pipeline import make_video


def _row(role="body", vo="It moved quietly.", t0=0.0, t1=3.0, driver=""):
    return {"retention_role": role, "vo_line": vo, "t_start": t0,
            "t_end": t1, "neuro_driver": driver}


GOOD_BOARD = [
    _row("hook", "Stop scrolling. This doctor vanished.", 0.0, 2.5,
         "N1 THUMB-STOP"),
    _row("body", "But nobody saw him leave. Why?", 2.5, 6.0, "N4 VALUE-DEBT"),
    _row("payoff+cua", "The answer is stranger than you think.", 6.0, 9.0,
         "N3 ESCALATE"),
]

GOOD_TITLE = "The Doctor Who Vanished Mid-Surgery"   # 35 chars


def test_good_plan_chain_9_of_9():
    r = chain_check(GOOD_BOARD, title=GOOD_TITLE, duration_s=9.0,
                    loop_planned=True, has_disclosure=True)
    assert r["weak"] == []
    assert r["curve"]["sickness"] == "healthy"
    assert r["ok"] is True
    assert "9/9" in verdict(r)


def test_deliberately_bad_plan_fails_with_links_named():
    bad = [
        _row("body", "They walked to the store.", 0.0, 3.0),
        _row("body", "Then they sat down.", 3.0, 6.0),
        _row("body", "Then they went home. Thanks for watching.", 6.0, 9.0),
    ]
    r = chain_check(bad, title="no", has_disclosure=False)
    for link in ("first_3s_gate", "one_peak", "engineered_end",
                 "open_loops", "satisfaction", "click"):
        assert link in r["weak"], (link, r["weak"])
    assert r["curve"]["sickness"] == "hockey_stick"
    v = verdict(r)
    assert "CHAIN BROKEN" in v and "first_3s_gate" in v


def test_click_band_shorts_vs_long():
    short_title = "Polar is FAKE King?!"     # 20 chars
    ok_long = chain_check(GOOD_BOARD, title="The Doctor Who Vanished",
                          loop_planned=True, has_disclosure=True)
    assert ok_long["links"]["click"]["ok"]
    bad_short = chain_check(GOOD_BOARD, title=short_title, shorts=True,
                            loop_planned=True, has_disclosure=True)
    assert not bad_short["links"]["click"]["ok"]      # 20 < 22 shorts band
    assert "outside band" in bad_short["links"]["click"]["note"]


def test_diluted_peak_named():
    two_peaks = GOOD_BOARD + [_row("payoff", "Another payoff!", 9.0, 12.0)]
    r = chain_check(two_peaks, title=GOOD_TITLE, loop_planned=True,
                    has_disclosure=True)
    assert not r["links"]["one_peak"]["ok"]
    assert "diluted peak" in r["links"]["one_peak"]["note"]


def test_lufs_out_of_band_breaks_satisfaction():
    r = chain_check(GOOD_BOARD, title=GOOD_TITLE, loop_planned=True,
                    has_disclosure=True, lufs=-8.0)
    assert not r["links"]["satisfaction"]["ok"]
    assert "-8.0 LUFS" in r["links"]["satisfaction"]["note"]


def test_but_therefore_explicit_connectors():
    chained = [
        _row("hook", "The crown was fake.", 0.0, 3.0),
        dict(_row("body", "The bear walked away.", 3.0, 6.0),
             connector="but"),
        dict(_row("payoff", "The king panicked.", 6.0, 9.0),
             connector="therefore"),
    ]
    assert but_therefore_lint(chained) == []
    dead = [dict(_row("body", f"Beat {i} happened.", i * 3.0, (i + 1) * 3.0),
                 connector="and then") for i in range(3)]
    findings = but_therefore_lint(dead)
    assert findings and "AND-THEN" in findings[0]


# ---------------------------------------------------------------------------
# curve verdicts
# ---------------------------------------------------------------------------


def test_curve_gradual_bleed():
    bleed = [_row("hook", vo="Hook.", t0=0, t1=2),
             _row("silence-sting", vo="...", t0=2, t1=5),
             _row("silence-sting", vo="...", t0=5, t1=8)]
    c = curve_forecast(bleed)
    assert c["sickness"] == "gradual_bleed"


def test_curve_camel_humps():
    camel = [_row("hook", t0=0, t1=2), _row("silence-sting", t0=2, t1=4),
             _row("payoff", t0=4, t1=6), _row("silence-sting", t0=6, t1=8),
             _row("payoff", t0=8, t1=10)]
    c = curve_forecast(camel)
    assert c["sickness"] == "camel_humps"
    assert "dips" in c["why"]


def test_curve_peak_too_early():
    early = [_row("hook", t0=0, t1=2), _row("payoff", t0=2, t1=5),
             _row("body", t0=5, t1=8)]
    assert curve_forecast(early)["sickness"] == "peak_too_early"


def test_curve_refuses_garbage():
    with pytest.raises(ValueError, match="refuses"):
        curve_forecast([])


# ---------------------------------------------------------------------------
# CLI gate
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def fdir(tmp_path_factory):
    d = tmp_path_factory.mktemp("wb1") / "out"
    make_video("polar is fake king", d, length=8.0, fps=1, seed=41,
               voice_backend="mumble")
    return d


def test_cli_forecast_pass_and_fail(fdir, capsys):
    rc = main(["forecast", str(fdir), "--title", GOOD_TITLE,
               "--disclosure", "--loop"])
    out = capsys.readouterr().out
    assert rc == 0 and "9/9" in out and "healthy" in out
    rc2 = main(["forecast", str(fdir), "--title", "x", "--shorts"])
    out2 = capsys.readouterr().out
    assert rc2 == 2 and "CHAIN BROKEN" in out2 and "click" in out2


def test_cli_forecast_missing_dir(tmp_path, capsys):
    rc = main(["forecast", str(tmp_path / "ghost")])
    assert rc == 2 and "FAIL" in capsys.readouterr().out
