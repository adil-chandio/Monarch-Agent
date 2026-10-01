"""FK MOTION ENGINE tests - bone-rotation animation (recovered 2026-10-01).

The lost local commit's core, rebuilt on the merged art engine: bones
rotate (spine / head / upper-arm / forearm / thigh / shin), joints fall
out of forward kinematics. Laws under test: the motion registry fails
closed, loops are seamless BY CONSTRUCTION (t=1 == t=0), the one-shot
jump lands EXACTLY on the idle base (no float), airborne means airborne
(hip above the ground line, head inside the middle-60% band),
bone lengths are invariants of the FK chain, the walk alternates stance,
frame counts honor the L13 law (frames / fps == spec seconds), and the
CLI contract holds. Pillow/ffmpeg are env dependencies - skip honestly.

Regression note: the pre-recovery `_render_joints` painted over an idle
background figure (double-figure bug) and skipped supersampling + props;
these tests pin the fixed single-source layer path.
"""

from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("PIL")

from monarch.cli import main                                    # noqa: E402
from monarch.video.stickman_art import (BASE, BASE_ANGLES, BONE,  # noqa: E402
                                        MOTIONS, SUBJECT_BAND, W, H,
                                        _joints_px, draw_scene,
                                        render_motion_mp4, motion_frames,
                                        motion_pose)


# ---------------------------------------------------------------------------
# registry + fail-closed
# ---------------------------------------------------------------------------


def test_motion_registry_and_fail_closed():
    assert set(MOTIONS) >= {"walk", "wave", "jump"}
    for spec in MOTIONS.values():
        assert spec["seconds"] > 0 and spec["fps"] >= 2 and spec["note"]
    with pytest.raises(ValueError, match="unknown motion"):
        motion_pose("backflip", 0.5)
    with pytest.raises(ValueError, match="unknown motion"):
        motion_frames("backflip")
    with pytest.raises(ValueError, match="unknown motion"):
        render_motion_mp4("backflip", "/tmp/nope")


# ---------------------------------------------------------------------------
# loop seam + one-shot landing
# ---------------------------------------------------------------------------


def test_loop_seam_is_exact():
    """Loops wrap seamlessly: t=1.0 == t=0.0 (sin/cos by construction)."""
    for name in ("walk", "wave"):
        assert MOTIONS[name]["loop"] is True
        a, b = motion_pose(name, 0.0), motion_pose(name, 1.0)
        for k in BASE:
            assert a[k] == pytest.approx(b[k], abs=1e-12), (name, k)


def test_one_shot_lands_exactly_on_idle_base():
    """The landing frame is EXACTLY the base pose - no float, no drift."""
    assert MOTIONS["jump"]["loop"] is False
    land = motion_pose("jump", 1.0)
    for k, v in BASE.items():
        assert land[k] == pytest.approx(v, abs=1e-9), k
    # clamped beyond 1.0 as well
    over = motion_pose("jump", 2.5)
    assert over["hip"] == pytest.approx(BASE["hip"], abs=1e-9)


def test_jump_gets_airborne_and_stays_in_band():
    """Airborne = hip above its base height; the head never leaves the
    middle-60% subject band (miss-#5 law)."""
    up = motion_pose("jump", 0.5)
    assert up["hip"][1] < BASE["hip"][1] - 0.3          # real air
    ground = _joints_px(up, W // 2, int(H * 0.76), H / 6.4)
    assert SUBJECT_BAND[0] <= ground["head"][1] <= SUBJECT_BAND[1]
    assert ground["foot_r"][1] < int(H * 0.76)          # feet off the floor
    # crouch = hip lower than base
    crouch = motion_pose("jump", 0.18)
    assert crouch["hip"][1] > BASE["hip"][1]


# ---------------------------------------------------------------------------
# FK invariants
# ---------------------------------------------------------------------------


def test_fk_bone_lengths_are_invariants():
    """Every joint is BONE[..] away from its parent, at every t, in all
    motions - the FK chain never stretches."""
    from math import hypot
    for name in MOTIONS:
        for t in (0.0, 0.13, 0.37, 0.5, 0.71, 0.99):
            j = motion_pose(name, t)

            def d(a, b):
                return hypot(j[a][0] - j[b][0], j[a][1] - j[b][1])

            assert d("hip", "neck") == pytest.approx(BONE["spine"], abs=1e-9)
            assert d("neck", "head") == pytest.approx(BONE["head"], abs=1e-9)
            assert d("neck", "elbow_r") == pytest.approx(
                BONE["upper_arm"], abs=1e-9)
            assert d("elbow_r", "hand_r") == pytest.approx(
                BONE["forearm"], abs=1e-9)
            assert d("hip", "knee_l") == pytest.approx(
                BONE["thigh"], abs=1e-9)
            assert d("knee_l", "foot_l") == pytest.approx(
                BONE["shin"], abs=1e-9)


def test_walk_alternates_stance_and_wave_raises_the_arm():
    # walk: the two thighs must swing OPPOSITE ways (a real stride)
    a = motion_pose("walk", 0.25)
    b = motion_pose("walk", 0.75)
    assert (a["knee_l"][0] > BASE["knee_l"][0]) != \
        (b["knee_l"][0] > BASE["knee_l"][0])
    assert (a["knee_r"][0] > BASE["knee_r"][0]) != \
        (b["knee_r"][0] > BASE["knee_r"][0])
    # wave: the right hand ends up ABOVE the head, and the left arm rests
    for t in (0.0, 0.25, 0.5, 0.75):
        w = motion_pose("wave", t)
        assert w["hand_r"][1] < w["head"][1]           # hand above head
        assert w["hand_r"][1] < w["hand_l"][1]         # and above the rest


def test_motion_frames_count_and_anim_purity(tmp_path):
    """frames == round(seconds * fps); the animation frame carries ONE
    figure (the double-figure regression stays dead) and no text props."""
    frames = motion_frames("jump", fps=30, seconds=1.6)
    assert len(frames) == 48                            # 1.6s * 30fps exact
    assert frames[0].size == (W, H)
    # idle-vs-jump-landing: the last jump frame equals the idle drawing
    idle = draw_scene("idle", seed=7)
    assert frames[-1].tobytes() == idle.tobytes()    # exact landing law


# ---------------------------------------------------------------------------
# render + CLI
# ---------------------------------------------------------------------------


def test_render_motion_mp4_silent_law(tmp_path):
    res = render_motion_mp4("walk", tmp_path / "mot", fps=12, seconds=0.5)
    out = Path(res["output"])
    assert out.is_file() and out.name == "motion_walk.mp4"
    assert res["frames"] == 6 and res["loop"] is True
    assert res["duration_ok"] and res["drift_s"] <= 0.5
    assert (tmp_path / "mot" / "motion_frames").is_dir()


def test_render_motion_mp4_with_wav_is_audio_truth(tmp_path):
    from monarch.video.audio import write_wav
    wav = tmp_path / "vo.wav"
    write_wav(wav, [0.22] * int(44100 * 1.1), 44100)    # 1.1s truth
    res = render_motion_mp4("wave", tmp_path / "mot2", fps=24, wav=wav)
    assert abs(res["want_s"] - 1.1) <= 1 / 24           # frames snapped
    assert res["duration_ok"]


def test_cli_art_motion(tmp_path, capsys):
    rc = main(["art-motion", "--motion", "jump", "--fps", "12",
               "--seconds", "0.5", "--out", str(tmp_path / "cli")])
    out = capsys.readouterr().out
    assert rc == 0 and "MOTION jump" in out and "one-shot" in out
    assert (tmp_path / "cli" / "motion_jump.mp4").is_file()
    # argparse rejects an unknown motion (fail-closed at the door)
    with pytest.raises(SystemExit) as ex:
        main(["art-motion", "--motion", "backflip",
              "--out", str(tmp_path / "cli2")])
    assert ex.value.code == 2
    # and a missing --wav fails closed with the honest FAIL text
    rc3 = main(["art-motion", "--motion", "wave",
                "--wav", str(tmp_path / "ghost.wav"),
                "--out", str(tmp_path / "cli3")])
    assert rc3 == 2 and "FAIL" in capsys.readouterr().out
