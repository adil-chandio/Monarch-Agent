"""MONARCH V2 post-mortem tests - Every Bear session laws, wired.

Miss #1 audio bitrate verify · #2 crescendo not tick · #4 chunk planner
(never split a topic) · #5 unique image per beat. Deterministic, stdlib.
"""

from __future__ import annotations

import json
import wave as wmod
from pathlib import Path

import pytest

from monarch.cli import main
from monarch.video.chunks import (BOUNDARY_GAP_S, BOUNDARY_SFX, MAX_BEATS,
                            plan_chunks, verify_no_split)
from monarch.video.audit import audit_dir
from monarch.video.audio import render_sfx, sfx_crescendo
from monarch.video.mix import mix
from monarch.video.pipeline import make_video
from monarch.video.render import render_mp4


# ---------------------------------------------------------------------------
# miss #2 - crescendo, never the intro beep
# ---------------------------------------------------------------------------


def test_crescendo_smooth_1p8s_soft_head():
    sr = 44100
    c = sfx_crescendo(sr)
    assert len(c) / sr == pytest.approx(1.8, abs=0.01)
    head = max(abs(v) for v in c[:int(0.02 * sr)])
    assert head < 0.3                      # no instantaneous click
    assert max(abs(v) for v in c) <= 0.85  # peak-safe


def test_crescendo_registered_in_sfx_kinds():
    piece = render_sfx("crescendo", sr=24000, seed=1)
    assert len(piece) == int(1.8 * 24000)


def test_mix_auto_swaps_tick_at_edges():
    sr = 24000
    board = [
        {"id": 1, "sfx": "tick", "t_start": 0.0, "t_end": 1.0},
        {"id": 2, "sfx": "hit", "t_start": 1.0, "t_end": 2.0},
        {"id": 3, "sfx": "tick", "t_start": 2.0, "t_end": 3.0},
    ]
    master, rep = mix(duration_s=3.2, vo=None, sr=sr, board=board, seed=1)
    assert any("tick at intro/outro auto-swapped" in w for w in rep.warnings)
    assert board[0]["sfx"] == "crescendo" and board[-1]["sfx"] == "crescendo"
    assert board[1]["sfx"] == "hit"        # body ticks stay untouched


def test_audit_flags_tick_edges(tmp_path):
    d = tmp_path / "t"
    d.mkdir()
    (d / "board.json").write_text(json.dumps({"scenes": [
        {"id": 1, "vo_line": "the tape starts here.", "t_start": 0.0,
         "t_end": 3.0, "sfx": "tick"}]}), encoding="utf-8")
    rep = audit_dir(d)
    assert any("harsh tick at intro" in f.title for f in rep.findings)


# ---------------------------------------------------------------------------
# miss #4 - chunk planner: never split a topic
# ---------------------------------------------------------------------------


def _groups():
    return [{"topic": "hook", "beats": list(range(1, 9))},
            {"topic": "panda", "beats": list(range(9, 21))},
            {"topic": "sun", "beats": list(range(21, 40))},
            {"topic": "moon", "beats": list(range(40, 55))},
            {"topic": "verdict", "beats": list(range(55, 60))}]


def test_chunks_start_new_topic_end_complete():
    chunks = plan_chunks(_groups())
    seen: set[str] = set()
    for c in chunks:
        assert c["topics"][0] not in seen  # every chunk starts a NEW topic
        seen.update(c["topics"])
        assert all(t in seen for t in c["topics"])
    assert sum(len(c["beats"]) for c in chunks) == 59
    assert chunks[0]["boundary"] is None


def test_chunks_never_exceed_max_and_carry_cues():
    chunks = plan_chunks(_groups())
    for c in chunks:
        assert len(c["beats"]) <= MAX_BEATS
    for c in chunks[1:]:
        assert c["boundary"]["gap_s"] == BOUNDARY_GAP_S == 0.85
        assert c["boundary"]["sfx"] == list(BOUNDARY_SFX) == ["whoosh", "riser"]


def test_chunks_fail_closed_on_topic_split():
    big = [{"topic": "one-bear", "beats": list(range(1, MAX_BEATS + 2))}]
    with pytest.raises(ValueError, match="repetition bug"):
        plan_chunks(big)


def test_chunks_garbage_fails_closed():
    with pytest.raises(ValueError):
        plan_chunks([{"topic": "", "beats": [1]}])
    with pytest.raises(ValueError):
        plan_chunks([{"topic": "x", "beats": []}])


def test_verify_no_split_catches_duplicates():
    chunks = plan_chunks(_groups())
    verify_no_split(_groups(), chunks)      # clean plan passes
    broken = [dict(c) for c in chunks]
    broken[1]["topics"] = list(broken[1]["topics"]) + ["sun"]
    with pytest.raises(ValueError, match="repetition bug"):
        verify_no_split(_groups(), broken)


# ---------------------------------------------------------------------------
# miss #1 + #5 - bitrate verify + unique frames (audit + render)
# ---------------------------------------------------------------------------


def test_render_reports_audio_bitrate(tmp_path):
    d = tmp_path / "r"
    make_video("the lost tape", d, length=10.5, fps=1, seed=8,
               voice_backend="mumble", do_mix=True)
    res = render_mp4(d)
    assert res["audio_kbps"] is None or res["audio_kbps"] >= 72
    assert res["bitrate_ok"] is True      # 32k class = the robotic bug
    Path(res["output"]).unlink()           # workspace diet


def test_audit_flags_low_bitrate_robotic_class(tmp_path):
    ff = None
    try:
        from monarch.video.render import ffmpeg_exe
        ff = ffmpeg_exe()
    except ValueError:
        pytest.skip("ffmpeg unavailable")
    import subprocess as sp
    d = tmp_path / "lo"
    d.mkdir()
    (d / "manifest.json").write_text(json.dumps({"scenes": []}),
                                     encoding="utf-8")
    # build a real 32k aac mp4 from a tiny wav (the 32k bug, on purpose)
    wav = d / "t.wav"
    with wmod.open(str(wav), "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(24000)
        f.writeframes(b"\x10\x00" * 24000)
    bad = d / "bad.mp4"
    sp.run([ff, "-y", "-hide_banner", "-loglevel", "error", "-i", str(wav),
            "-b:a", "32k", str(bad)], check=True)
    rep = audit_dir(d)
    hit = [f for f in rep.findings
           if "bitrate starvation" in f.title]
    assert hit and hit[0].severity == "P1"


def test_audit_flags_duplicate_frames(tmp_path):
    d = tmp_path / "dup"
    d.mkdir()
    (d / "timeline.json").write_text(json.dumps({"frames": [
        {"file": "frames/a.png", "t_start": 0.0, "t_end": 1.0},
        {"file": "frames/a.png", "t_start": 1.0, "t_end": 2.0},
        {"file": "frames/b.png", "t_start": 2.0, "t_end": 3.0}]}),
        encoding="utf-8")
    (d / "manifest.json").write_text(json.dumps({"scenes": []}),
                                     encoding="utf-8")
    rep = audit_dir(d)
    hit = [f for f in rep.findings if "repeated frame" in f.title]
    assert hit and hit[0].severity == "P2"
    assert rep.scores["frames_unique"] == (2, 3)


def test_clean_video_has_no_duplicate_frames(tmp_path):
    d = tmp_path / "ok"
    make_video("the vault nobody could open", d, length=10.5, fps=1, seed=5)
    rep = audit_dir(d)
    assert not any("repeated frame" in f.title for f in rep.findings)


def test_cli_still_green_after_v2(capsys):
    assert main(["laws"]) == 0
    assert "PART 3" in capsys.readouterr().out
