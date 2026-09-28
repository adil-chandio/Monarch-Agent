"""Script-forensics upgrades: genre engine, length classes, logline, AV script.

Sources folded in: vidiQ 4-part/125-150wpm, Alwrity 8-genre configs +
duration splits, Celtx/Boords logline + two-column AV format,
rahulanand1103 time-boxed sections. All deterministic, fail-closed.
"""

from __future__ import annotations

import json

import pytest

from monarch.cli import main
from monarch.video.director import plan_storyboard
from monarch.video.genres import (GENRES, LENGTH_CLASSES, av_script,
                                  beat_plan, logline, plan_budget)
from monarch.video.pipeline import make_video


def test_genres_complete_and_structures_valid():
    assert len(GENRES) == 8
    for name, g in GENRES.items():
        assert g["structure"][0] == "hook"           # vidIQ part 1 pinned
        assert g["structure"][-1].endswith("cua")    # vidIQ part 3 (CTA)
        assert g["hook_strategy"] and g["cta_focus"]


def test_length_classes_cover_targets():
    for name, lc in LENGTH_CLASSES.items():
        beats = beat_plan(list(GENRES)[0], name)
        total = sum(b["s"] for b in beats)
        assert abs(total - lc["target_s"]) <= lc["clip_s"]
        assert all(b["words"] == lc["words_per_clip"] for b in beats)


def test_short60_matches_shipped_maths():
    b = beat_plan("mystery", "short60")
    assert b[0]["s"] == 2.5                       # first clip 2.5s EXACT
    assert all(x["s"] == 3.5 for x in b[1:])      # body clips 3.5s EXACT
    assert all(x["words"] == 7 for x in b)        # 7 words/clip EXACT


def test_unknown_genre_or_class_fails_closed():
    with pytest.raises(ValueError):
        beat_plan("telenovela", "short60")
    with pytest.raises(ValueError):
        beat_plan("mystery", "short90")


def test_budget_wpm_is_honest():
    pb = plan_budget("mystery", "short60")
    assert pb["scenes"] == 18
    assert pb["total_words"] == 126               # 18 x 7 EXACT
    assert 100 <= pb["wpm"] <= 170
    assert pb["in_ideal_band"] == (125 <= pb["wpm"] <= 150)


def test_logline_two_sentences_mentions_topic():
    ll = logline("the doctor who vanished", "mystery")
    assert ll.count(".") >= 2 and "doctor" in ll
    with pytest.raises(ValueError):
        logline("x", "nope")


def test_av_script_two_columns():
    sb = plan_storyboard("the vault nobody could open", length=10.5, seed=5)
    md = av_script(sb.board(), sb.title)
    assert "| # | VISUAL | AUDIO (VO + SFX) |" in md
    assert "**[SFX:" in md
    assert md.strip().endswith("_")


def test_storyboard_carries_genre_and_logline():
    sb = plan_storyboard("the vault nobody could open", length=10.5, seed=5,
                         genre="listicle")
    assert sb.genre == "listicle"
    assert "vault" in sb.logline
    with pytest.raises(ValueError):
        plan_storyboard("x", length=10.5, genre="telenovela")


def test_make_video_emits_av_script_and_logline(tmp_path):
    d = tmp_path / "g"
    m = make_video("the doctor who vanished", d, length=10.5, fps=1,
                   seed=4, voice_backend="mumble", do_mix=True,
                   genre="tutorial")
    assert m["genre"] == "tutorial" and "logline" in m
    av = (d / "av_script.md").read_text(encoding="utf-8")
    assert "VISUAL" in av and "AUDIO" in av


def test_cli_genre_flag(tmp_path):
    d = tmp_path / "c"
    rc = main(["make-video", "--topic", "the lost tape", "--genre",
               "listicle", "--seed", "3", "--length", "10.5", "--fps", "1",
               "--out", str(d)])
    assert rc == 0
    m = json.loads((d / "manifest.json").read_text(encoding="utf-8"))
    assert m["genre"] == "listicle"
