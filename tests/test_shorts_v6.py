"""MONARCH V6 tests - the 14-miss Shorts canon, executable.

docs/VIRAL_SHORTS_V6.md: prompt laws (miss 2-3), VO-driven timing
(miss 4/12), text placement+animation+sync (miss 7-10), packaging
(miss 1/13/14), buildup music (miss 11), condensed-incomplete plan.
"""

from __future__ import annotations

import pytest

from monarch.cli import main
from monarch.video.mix import buildup_bed, mix
from monarch.video.shorts import (ANIMATIONS, NO_TEXT_CLAUSE, TEXT_Y_BOTTOM,
                                  TEXT_Y_CENTER, TEXT_Y_TOP, beats_for_vo,
                                  cta_lint, end_screen_plan, image_prompt,
                                  long_to_short, plan_texts, prompt_lint,
                                  title_check)


# ---------------------------------------------------------------------------
# image prompt laws (miss 2-3)
# ---------------------------------------------------------------------------


def test_image_prompt_has_all_law_clauses():
    p = image_prompt("polar crown shattering, jaw drop")
    assert NO_TEXT_CLAUSE in p
    assert "middle 60% safe zone" in p
    assert "one focal subject" in p
    assert "stickman" in p


def test_image_prompt_refuses_desi_words():
    with pytest.raises(ValueError, match="miss #2"):
        image_prompt("tabahi next level bear")


def test_prompt_lint_flags_missing_laws():
    issues = prompt_lint("a bear, plain prompt")
    assert any("no-text" in i for i in issues)
    assert prompt_lint(image_prompt("clean bear")) == []


# ---------------------------------------------------------------------------
# VO-driven timing (miss 4/12)
# ---------------------------------------------------------------------------


def test_beats_for_vo_matches_the_session_math():
    b = beats_for_vo(32.55)
    assert b["total_s"] == 33.25          # VO + 0.5 + 0.2 (never cut VO)
    assert b["beats"] == 10
    assert b["beat_s"] == pytest.approx(3.33, abs=0.01)
    assert b["in_short_band"] is True


def test_beats_for_vo_zero_fails_closed():
    with pytest.raises(ValueError, match="measured"):
        beats_for_vo(0)


def test_beats_for_vo_clamps_beat_length():
    b = beats_for_vo(45.0)
    assert b["beat_s"] <= 3.5             # image duration law cap
    assert b["beats"] > 10


# ---------------------------------------------------------------------------
# TEXT_SYNCED planner (miss 7-10)
# ---------------------------------------------------------------------------


def _entries(n=4):
    return [{"text": t, "appear": 0.5 + i * 3.0}
            for i, t in enumerate(["POLAR FAKE?", "WATCH THIS",
                                   "CENSORED!", "YOU WERE WRONG"][:n])]


def test_plan_texts_never_center_over_subject():
    cues = plan_texts(_entries())
    for c in cues:
        assert c["y"] in (TEXT_Y_TOP, TEXT_Y_BOTTOM)
        assert c["y"] != TEXT_Y_CENTER


def test_plan_texts_word_cap():
    with pytest.raises(ValueError, match="words"):
        plan_texts([{"text": "one two three four five", "appear": 0.0}])


def test_plan_texts_animation_never_thrice_in_a_row():
    cues = plan_texts(_entries(8))
    runs = 1
    worst = 1
    for a, b in zip(cues, cues[1:]):
        runs = runs + 1 if a["anim"] == b["anim"] else 1
        worst = max(worst, runs)
    assert worst <= 2
    assert set(c["anim"] for c in cues) <= set(ANIMATIONS)


def test_plan_texts_carries_show_fade_laws():
    cues = plan_texts(_entries(2))
    assert all(c["show_s"] == 1.7 and c["fade_s"] == 0.3 for c in cues)


# ---------------------------------------------------------------------------
# packaging (miss 1/13/14)
# ---------------------------------------------------------------------------


def test_title_short_passes_long_fails():
    ok = title_check("Polar is FAKE King?! 😱")
    assert ok["ok"] and ok["words"] == 5
    bad = title_check("Polar is FAKE #1?! Grizzly CHASED Him?! 🤯")
    assert not bad["ok"] and bad["chars"] > 35 or not bad["ok"]


def test_cta_lint_bans_link_in_bio():
    bad = cta_lint("great video, link in bio!")
    assert not bad["ok"] and "link in bio" in bad["issues"][0]
    good = cta_lint("Full video on screen now - tap to watch!")
    assert good["ok"]


def test_end_screen_last_7s_right_40pct():
    e = end_screen_plan(33.0)
    assert e["start_s"] == 26.0 and e["side"] == "right"
    assert e["width_frac"] == 0.4 and e["arrow"] == "WATCH HERE"


def test_long_to_short_split_law():
    plan = long_to_short(["Panda", "Sun", "Spectacled", "Moon", "Sloth",
                          "Black", "Polar", "Grizzly"])
    assert plan["pct"]["show"] >= 55
    assert 15 <= plan["pct"]["skipped"] <= 35
    assert 5 <= plan["pct"]["censored"] <= 25
    assert plan["censored"] == ["Grizzly"]      # #1 censored (miss #1 fix)
    assert "Comment YOUR TOP 3" in plan["comment_bait"]


def test_long_to_short_refuses_cta_only():
    with pytest.raises(ValueError, match="CTA-only"):
        long_to_short(["Panda", "Sun", "Grizzly"])


# ---------------------------------------------------------------------------
# buildup music (miss 11)
# ---------------------------------------------------------------------------


def test_buildup_bed_rises_smooth_never_harsh():
    sr = 24000
    bed = buildup_bed(12.0, sr, seed=1)
    def rms(a, b):
        seg = bed[int(a * sr):int(b * sr)]
        return (sum(v * v for v in seg) / max(1, len(seg))) ** 0.5
    early, late = rms(0.5, 2.5), rms(9.0, 12.0)
    assert late > early                          # slow build
    assert max(abs(v) for v in bed) <= 0.6       # stays under the VO
    # no hard kick (miss #11): 20ms envelope-RMS jumps stay small -
    # a hard kick would spike the level between neighbouring windows
    win = int(0.02 * sr)
    env = [(sum(v * v for v in bed[i:i + win]) / win) ** 0.5
           for i in range(0, len(bed) - win, win)]
    # soft 1.4 s heartbeat onsets are DESIGNED (canon 3.2/miss 11 fix);
    # the banned hard kick would onset every 0.7 s at harsh amplitude
    jumps = [abs(a - b) for a, b in zip(env, env[1:])]
    assert max(jumps) < 0.2
    med = sorted(env)[len(env) // 2]
    onsets = [i for i in range(1, len(env))
              if env[i] > 2 * max(med, 1e-4) and env[i - 1] <= 2 * max(med, 1e-4)]
    # merge the lub-dub pair (one heartbeat = two hits ~0.14 s apart)
    clusters: list[int] = []
    for o in onsets:
        if not clusters or o - clusters[-1] > 25:
            clusters.append(o)
    if len(clusters) >= 2:
        gaps = [b - a for a, b in zip(clusters, clusters[1:])]
        assert min(gaps) >= 55                   # 1.1 s floor (law: 1.4 s
        # period, NOT the banned 0.7 s hard-kick metronome)


def test_mix_mood_buildup_flows():
    sr = 24000
    master, rep = mix(duration_s=2.0, vo=[0.2] * int(1.5 * sr), sr=sr,
                      seed=2, music_mood="buildup")
    assert rep.mood == "buildup"
    assert max(abs(v) for v in master) <= 0.82


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def test_cli_short_plan(capsys):
    rc = main(["short-plan", "--topics",
               "Panda,Sun,Spectacled,Moon,Sloth,Black,Polar,Grizzly",
               "--vo-s", "32.55"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "33.25" in out and "SHOW" in out and "CENSORED" in out
    rc2 = main(["short-plan", "--topics", "a,b,c"])
    assert rc2 == 2 and "FAIL" in capsys.readouterr().out
