"""Tests for monarch.video — director, engine, audio, compositor, pipeline, CLI."""

from __future__ import annotations

import json
import struct
import wave
from pathlib import Path

import pytest

from monarch.cli import main
from monarch.core.gates import GateFail
from monarch.pipelines.fountain import beats_from_screenplay, build_script, screenplay_from_text
from monarch.video import audio
from monarch.video.compositor import MOTIONS, ken_burns, plan_camera, stitch
from monarch.video.director import (
    COHORTS,
    NEURO_DRIVERS,
    plan_storyboard,
    render_box_card,
)
from monarch.video.engine import (
    COHORT_PALETTES,
    Frame,
    FrameSpec,
    render_frame,
)
from monarch.video.font import GLYPH_H, glyph_rows, text_width, wrap_text

TINY = dict(width=270, height=480)


# ---------------------------------------------------------------------------
# font
# ---------------------------------------------------------------------------


def test_font_glyphs_complete():
    for ch in "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .,!?:-()+/":
        rows = glyph_rows(ch)
        assert len(rows) == GLYPH_H
        assert all(0 <= r < 32 for r in rows), f"glyph {ch!r} out of 5-bit range"


def test_font_unknown_char_falls_back():
    assert glyph_rows("£") == glyph_rows("?")


def test_wrap_text():
    lines = wrap_text("the deep sea keeps one secret", 60, scale=1)
    assert lines
    assert " ".join(lines) == "the deep sea keeps one secret"
    for line in lines:
        assert text_width(line, 1) <= 60


# ---------------------------------------------------------------------------
# director — the gated storyboard
# ---------------------------------------------------------------------------


def test_plan_storyboard_hits_the_maths_line():
    sb = plan_storyboard("the deep sea", length=60)
    assert len(sb.scenes) == sb.maths.scenes
    for scene in sb.scenes:
        assert scene.word_count == sb.maths.words_per_clip
        assert scene.vo_line
        assert scene.visual
        assert scene.t_end > scene.t_start
    # open clip obeys the L3/gate law: never longer than 3s
    assert sb.scenes[0].t_end - sb.scenes[0].t_start <= 3.01


def test_storyboard_roles_follow_the_playbook():
    sb = plan_storyboard("the deep sea", length=45, seed=3)
    roles = [m["role"] for m in sb.drivers]
    assert roles[0] == "hook"
    assert roles[-1] == "payoff+cua"
    assert len(roles) == len(sb.scenes)
    for meta in sb.drivers:
        assert meta["driver"] in NEURO_DRIVERS
        assert meta["law"] == NEURO_DRIVERS[meta["driver"]]["law"]
    # N5: exactly one silence-sting carrying the 0.3s drop
    stings = [m for m in sb.drivers if m["role"] == "silence-sting"]
    assert len(stings) == 1
    assert stings[0]["silence_before_s"] == 0.3
    # N3: the body alternates tease and seeded payoffs
    body_roles = {r for r in roles[1:-1]}
    assert {"tease", "payoff"} & body_roles


def test_storyboard_is_deterministic_per_seed():
    a = plan_storyboard("the deep sea", length=30, seed=7)
    b = plan_storyboard("the deep sea", length=30, seed=7)
    assert a.fountain == b.fountain
    assert a.board() == b.board()


def test_seed_varies_the_variable_ratio_schedule():
    """N3 is seeded: across seeds the tease/payoff schedule must vary."""
    patterns = set()
    for seed in range(6):
        sb = plan_storyboard("the deep sea", length=30, seed=seed)
        patterns.add(tuple(m["role"] for m in sb.drivers))
    assert len(patterns) >= 2, "seed has no effect on the variable-ratio schedule"


def test_fountain_round_trips_through_the_real_m3_gate():
    from monarch.pipelines.fountain import beats_from_screenplay, screenplay_from_text

    sb = plan_storyboard("black holes", length=20)
    sp = screenplay_from_text(sb.fountain)
    assert len(sp.scenes) == sb.maths.scenes
    text = sb.fountain
    assert text.count("[[NEURO_DRIVER:") == sb.maths.scenes
    for driver_id in ("N1 THUMB-STOP", "N5 SILENCE-STING"):
        assert driver_id in text
    # re-gate the emitted screenplay independently
    report = __import__("monarch.pipelines.fountain", fromlist=["build_script"]) \
        .build_script(beats_from_screenplay(sp), 20)
    assert len(report.scenes) == sb.maths.scenes


def test_box_card_is_a_hollywood_card():
    sb = plan_storyboard("the deep sea", length=15)
    card = render_box_card(sb)
    assert sb.title in card
    assert "SCENE 01" in card
    assert "DRIVER" in card
    assert "MATHS" in card
    assert "Neuro Playbook N1-N5" in card
    width = max(len(line) for line in card.splitlines())
    assert width <= 82  # stays a phone-readable card


def test_plan_rejects_bad_input():
    with pytest.raises(ValueError):
        plan_storyboard("")
    with pytest.raises(ValueError):
        plan_storyboard("x", cohort="boomers")
    with pytest.raises(ValueError):
        plan_storyboard("x", length=0)
    with pytest.raises(GateFail):
        # open clip would run longer than 3s — the scene gate refuses it
        plan_storyboard("x", length=10, first_clip_s=4.0)


def test_board_json_carries_neuro_metadata():
    sb = plan_storyboard("the deep sea", length=15)
    board = sb.board()
    entry = board[0]
    for key in ("retention_role", "neuro_driver", "law", "sfx", "word_count"):
        assert key in entry
    assert entry["neuro_driver"] == "N1 THUMB-STOP"
    assert entry["retention_role"] == "hook"


# ---------------------------------------------------------------------------
# engine — procedural frames
# ---------------------------------------------------------------------------


def test_frame_writes_valid_png(tmp_path: Path):
    f = Frame(16, 12, (1, 2, 3))
    p = f.write_png(tmp_path / "f.png")
    raw = p.read_bytes()
    assert raw[:8] == b"\x89PNG\r\n\x1a\n"
    assert raw.endswith(b"IEND\xaeB`\x82")
    w, h = struct.unpack(">II", raw[16:24])
    assert (w, h) == (16, 12)


def test_render_frame_sizes_and_cohort_palettes():
    for cohort in COHORTS:
        assert cohort in COHORT_PALETTES
    spec = FrameSpec(scene_id=1, headline="THE DEEP SEA", vo_line="one two three",
                     badge="S01/02", driver="N1 THUMB-STOP", role="hook")
    f = render_frame(spec, **TINY)
    assert (f.w, f.h) == (270, 480)
    assert len(f.px) == 270 * 480 * 3
    other = render_frame(
        FrameSpec(scene_id=2, headline="X", vo_line="Y", cohort="kids"), **TINY
    )
    assert other.px != f.px  # different scene + cohort = different frame


def test_custom_accent_overrides_cohort():
    spec = FrameSpec(scene_id=1, headline="A", vo_line="B", accent=(255, 0, 0))
    assert render_frame(spec, **TINY).px != render_frame(
        FrameSpec(scene_id=1, headline="A", vo_line="B"), **TINY
    ).px


# ---------------------------------------------------------------------------
# audio — SFX bank + DSP
# ---------------------------------------------------------------------------


def test_every_sfx_kind_renders():
    for kind in audio.SFX_KINDS:
        s = audio.render_sfx(kind, sr=8000, seed=1)
        assert len(s) > 0
        assert all(-1.0 <= v <= 1.0 for v in s), f"{kind} exceeded the limiter"


def test_sfx_unknown_kind_and_filter_raise():
    with pytest.raises(ValueError):
        audio.render_sfx("laser", sr=8000)
    with pytest.raises(ValueError):
        audio.render_sfx("hit", sr=8000, filters=["reverb"])


def test_sfx_seconds_clamps():
    s = audio.render_sfx("hit", sr=8000, seconds=0.25)
    assert len(s) == 2000
    s2 = audio.render_sfx("hit", sr=8000, seconds=5.0)
    assert len(s2) == 40000
    assert s2[-100] == 0.0  # padded with the law-mandated silence


def test_dsp_filters_shape_the_signal():
    src = audio.render_sfx("hit", sr=8000, seed=2)
    for name in audio.FILTERS:
        out = audio.render_sfx("hit", sr=8000, seed=2, filters=[name])
        assert out != src, f"filter {name} did nothing"
        if name == "cyber_glitch":
            # stutters repeat segments: longer, but bounded
            assert len(src) < len(out) <= len(src) * 2
        else:
            assert len(out) == len(src)
    # limiter truly bounds a runaway signal
    hot = [3.0, -7.5, 40.0]
    assert all(abs(v) <= 0.95 for v in audio.limiter(hot))


def test_bass_boost_favors_lows():
    sr = 8000
    low = audio._sine(50, 1.0, sr)
    high = audio._sine(4000, 1.0, sr, amp=0.5)
    boosted_low = audio.bass_boost(low, sr)
    boosted_high = audio.bass_boost(high, sr)
    gain_low = max(abs(v) for v in boosted_low) / max(abs(v) for v in low)
    gain_high = max(abs(v) for v in boosted_high) / max(abs(v) for v in high)
    assert gain_low > gain_high


def test_write_wav_round_trip(tmp_path: Path):
    s = audio.render_sfx("sonar_ping", sr=8000, seed=4)
    p = audio.write_wav(tmp_path / "ping.wav", s, 8000)
    with wave.open(str(p), "rb") as w:
        assert w.getnchannels() == 1
        assert w.getsampwidth() == 2
        assert w.getframerate() == 8000
        assert w.getnframes() == len(s)


def test_40hz_and_silence_constants_are_lawful():
    assert audio.SUB_BASS_HZ == 40.0
    assert audio.SILENCE_DROP_S == 0.3


# ---------------------------------------------------------------------------
# compositor — Ken Burns + stitcher
# ---------------------------------------------------------------------------


def test_plan_camera_variety_and_open_snap():
    open_m = plan_camera(1, "hook")
    assert open_m.kind == "zoom_in"
    kinds = {plan_camera(i, "tease", seed=2).kind for i in range(2, 9)}
    assert kinds <= set(MOTIONS)
    assert len(kinds) > 1  # N3: motion variety resets habituation
    assert plan_camera(9, "payoff").kind == "zoom_in"  # payoff holds slow


def test_ken_burns_moves_and_keeps_size():
    base = render_frame(FrameSpec(scene_id=1, headline="K", vo_line="v"), **TINY)
    m = plan_camera(1, "hook")
    first = ken_burns(base, m, 0.0, seed=1)
    last = ken_burns(base, m, 1.0, seed=1)
    assert (first.w, first.h) == (base.w, base.h)
    assert (last.w, last.h) == (base.w, base.h)
    assert bytes(first.px) != bytes(last.px)
    # progress clamps: beyond 1 equals 1
    assert bytes(ken_burns(base, m, 1.5, seed=1).px) == bytes(last.px)


def test_stitch_writes_timeline_and_frames(tmp_path: Path):
    sb = plan_storyboard("the deep sea", length=9)  # 3 scenes (hook/sting/payoff)
    timeline = stitch(sb, tmp_path, fps=1, **TINY, seed=0)
    tl_path = tmp_path / "timeline.json"
    assert tl_path.is_file()
    assert timeline["frame_count"] > 0
    files = [e["file"] for e in timeline["frames"]]
    assert len(files) == timeline["frame_count"]
    for rel in files:
        assert (tmp_path / rel).is_file(), rel
    # timeline covers the board
    scenes_in_tl = {e["scene"] for e in timeline["frames"]}
    assert scenes_in_tl == {s.id for s in sb.scenes}
    # N5 silence marker lands on the sting scene's first frame
    stings = [e for e in timeline["frames"] if e["silence_before_s"]]
    assert all(e["sfx"] == "riser" for e in stings)
    reloaded = json.loads(tl_path.read_text(encoding="utf-8"))
    assert reloaded["frame_count"] == timeline["frame_count"]


# ---------------------------------------------------------------------------
# pipeline + CLI
# ---------------------------------------------------------------------------


def test_make_video_end_to_end(tmp_path: Path):
    from monarch.video.pipeline import make_video

    out = tmp_path / "previz"
    manifest = make_video(
        "the deep sea", out, length=6, fps=1, sr=8000, **TINY, seed=5
    )
    assert manifest["scene_count"] == 2
    assert manifest["frame_count"] > 0
    for rel in ("manifest.json", "screenplay.fountain", "board.json",
                "storyboard.txt", "timeline.json"):
        assert (out / rel).is_file(), rel
    assert (out / "sfx" / "scene_01_hit.wav").is_file()
    board = json.loads((out / "board.json").read_text(encoding="utf-8"))
    assert board["scenes"][0]["neuro_driver"] == "N1 THUMB-STOP"
    m = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
    assert m["title"] == "THE DEEP SEA"
    assert "HAAN" in m["kind"]


def test_cli_script_outputs_gated_fountain(capsys):
    rc = main(["script", "--topic", "the deep sea", "--length", "6", "--json"])
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert data["scene_count"] == 2
    assert "NEURO_DRIVER" in data["fountain"]


def test_cli_script_writes_fountain_file(tmp_path, capsys):
    out = tmp_path / "s.fountain"
    rc = main(["script", "--topic", "the deep sea", "--length", "6",
               "--out", str(out), "--card"])
    assert rc == 0
    text = out.read_text(encoding="utf-8")
    assert text.startswith("Title: THE DEEP SEA")
    assert "SCENE 01" in capsys.readouterr().out  # --card printed


def test_cli_video_storyboard_prints_card(capsys):
    rc = main(["video-storyboard", "--topic", "the deep sea", "--length", "6"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "NEURAL STORYBOARD" in out
    assert "SILENCE-STING" in out or "THUMB-STOP" in out


def test_cli_sfx_writes_wav(tmp_path, capsys):
    p = tmp_path / "hit.wav"
    rc = main(["sfx", "--kind", "hit", "--out", str(p), "--sr", "8000",
               "--seconds", "0.3", "--filter", "bass_boost"])
    assert rc == 0
    assert p.is_file() and p.stat().st_size > 44
    assert "hit" in capsys.readouterr().out


def test_cli_make_video(tmp_path, capsys):
    out = tmp_path / "mv"
    rc = main([
        "make-video", "--topic", "the deep sea", "--out", str(out),
        "--length", "6", "--fps", "1", "--width", "270", "--height", "480",
        "--sr", "8000", "--seed", "9",
    ])
    assert rc == 0
    text = capsys.readouterr().out
    assert "PREVIZ READY" in text
    assert (out / "manifest.json").is_file()
    assert list((out / "frames").glob("frame_*.png"))


def test_cli_script_fails_closed_on_bad_cohort(capsys):
    rc = main(["script", "--topic", "the deep sea", "--cohort", "boomers"])
    assert rc == 2
    assert "FAIL" in capsys.readouterr().out
