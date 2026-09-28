"""STICKMAN ART ENGINE tests - image banao, pose animate karo.

Laws under test: seeded determinism (identical bytes), the no-text
style (nothing textual is ever drawn), subject centered in the
middle-60% band (miss #5), pose registry integrity, joint-lerp
monotonicity, animation frame-count law, the 2-input mp4 render with
L13 drift, and the CLI contracts. Pillow is an env dependency - these
tests skip honestly if it is absent (pyproject stays zero-dep).
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

pytest.importorskip("PIL")

from monarch.cli import main                                   # noqa: E402
from monarch.video.stickman_art import (SUBJECT_BAND, W, H,    # noqa: E402
                                        draw_scene, lerp_poses,
                                        pose_frames, render_art_mp4,
                                        scene_png, POSES,
                                        _joints_px, _resolved)


# ---------------------------------------------------------------------------
# determinism + registry
# ---------------------------------------------------------------------------


def test_scene_deterministic_bytes():
    a = draw_scene("shock", prop="crown", seed=11)
    b = draw_scene("shock", prop="crown", seed=11)
    assert hashlib.sha256(a.tobytes()).digest() == \
        hashlib.sha256(b.tobytes()).digest()
    c = draw_scene("shock", seed=12)
    assert a.tobytes() != c.tobytes()            # seed changes the stars


def test_pose_registry_and_fail_closed():
    assert len(POSES) >= 7
    for name in POSES:
        j = _resolved(name)                      # every pose resolves
        assert "head" in j and "hip" in j
    with pytest.raises(ValueError, match="unknown pose"):
        draw_scene("karate")


def test_unknown_prop_fails_closed():
    with pytest.raises(ValueError, match="unknown prop"):
        draw_scene("idle", prop="lightsaber")


# ---------------------------------------------------------------------------
# placement laws
# ---------------------------------------------------------------------------


def test_subject_in_middle_60_band_and_centered():
    j = _joints_px(_resolved("shock"), W // 2, int(H * 0.76), H / 6.4)
    head_y = j["head"][1]
    assert SUBJECT_BAND[0] <= head_y <= SUBJECT_BAND[1]   # miss #5 law
    assert abs(j["head"][0] - W // 2) <= 2                # centered


def test_void_background_and_white_ink():
    img = draw_scene("idle", seed=3)
    px = img.load()
    corner = px[8, 8]
    assert corner[0] < 30 and corner[1] < 30 and corner[2] < 30   # void
    # white ink exists somewhere (the figure itself)
    whites = sum(1 for x in range(0, W, 17) for y in range(0, H, 17)
                 if px[x, y][0] > 200 and px[x, y][1] > 200)
    assert whites > 3


# ---------------------------------------------------------------------------
# pose animation
# ---------------------------------------------------------------------------


def test_lerp_monotonic_and_clamped():
    lo = lerp_poses("idle", "shock", -0.5)       # clamp to t=0
    mid = lerp_poses("idle", "shock", 0.5)
    hi = lerp_poses("idle", "shock", 2.0)        # clamp to t=1
    idle, shock = _resolved("idle"), _resolved("shock")
    assert lo["hand_r"] == idle["hand_r"]
    assert hi["hand_r"] == shock["hand_r"]
    for k in ("hand_r", "elbow_l"):
        ax, ay = idle[k]
        bx, by = shock[k]
        mx, my = mid[k]
        assert min(ax, bx) <= mx <= max(ax, bx)
        assert min(ay, by) <= my <= max(ay, by)


def test_pose_frames_count_law():
    frames = pose_frames(["idle", "shock", "crown"], steps=8, hold=3)
    # 2 transitions x 8 steps + 2 holds x 3
    assert len(frames) == 2 * 8 + 2 * 3
    with pytest.raises(ValueError, match=">= 2"):
        pose_frames(["idle"])
    with pytest.raises(ValueError, match="steps >= 2"):
        pose_frames(["idle", "shock"], steps=1)


def test_art_mp4_render_laws(tmp_path):
    frames = pose_frames(["idle", "wave", "idle"], steps=6, hold=2)
    res = render_art_mp4(frames, tmp_path / "art", fps=12)
    out = Path(res["output"])
    assert out.is_file() and res["bytes"] > 10_000
    assert res["duration_ok"] and res["drift_s"] <= 0.5
    assert res["frames"] == 2 * 6 + 2 * 2
    assert "2 inputs" in res["law_note"]
    assert (tmp_path / "art" / "art_frames").is_dir()
    assert (tmp_path / "art" / "art_concat.txt").is_file()


def test_scene_png_writer(tmp_path):
    p = scene_png(tmp_path / "scene.png", pose="crown", prop="crown",
                  seed=5)
    assert Path(p).is_file() and Path(p).stat().st_size > 5_000


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def test_cli_art_scene_and_anim(tmp_path, capsys):
    out_png = tmp_path / "scene.png"
    rc = main(["art-scene", "--pose", "shock", "--prop", "crown",
               "--out", str(out_png)])
    out = capsys.readouterr().out
    assert rc == 0 and out_png.is_file() and "ART SCENE" in out
    rc2 = main(["art-anim", "--poses", "idle,shock,crown",
                "--out", str(tmp_path / "anim")])
    out2 = capsys.readouterr().out
    assert rc2 == 0 and "ART ANIM" in out2 and "drift" in out2
    assert (tmp_path / "anim" / "art_anim.mp4").is_file()
    rc3 = main(["art-scene", "--pose", "karate", "--out",
                str(tmp_path / "x.png")])
    assert rc3 == 2 and "FAIL" in capsys.readouterr().out
