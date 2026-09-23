"""Ken Burns camera motion + timeline stitcher — stdlib only.

Playbook wiring:

* N1 — the open clip is a snap zoom-in: frame one moves.
* N3 — motion variety between scenes resets visual habituation (L3's 2-3s
  cut law stays the maths line's job; this module only moves the camera).
* N5 — a ``silence_before_s`` marker on a scene lands the 0.3s dead gap in
  the timeline right before that scene's first frame.

Output: ``frames/`` PNG sequence + ``timeline.json`` (the stitcher's EDL).
This is the previz/animatic layer — final footage still goes through the
visual pipeline and the HAAN gate, unchanged.
"""

from __future__ import annotations

import json
import math
import random
from dataclasses import dataclass
from pathlib import Path

from monarch.video.audio import SILENCE_DROP_S
from monarch.video.director import Storyboard
from monarch.video.engine import (
    FRAME_H,
    FRAME_W,
    Frame,
    FrameSpec,
    draw_fg,
    render_frame,
    scene_geometry,
)

MOTIONS = ("zoom_in", "zoom_out", "pan_left", "pan_right", "shake",
           "parallax_orbit", "push_in_fg")
ANIMATIONS = ("kenburns", "parallax")


@dataclass
class Motion:
    kind: str
    zoom_from: float = 1.0
    zoom_to: float = 1.12
    focus_from: tuple[float, float] = (0.5, 0.5)   # normalized center
    focus_to: tuple[float, float] = (0.5, 0.5)
    shake_amp: float = 0.0                          # fraction of width


#: N1: the open clip snaps — frame one moves before the reflex can ignore it;
#: N3: variety through the body; last scene holds slow (payoff)
_OPEN = Motion("zoom_in", 1.0, 1.18, (0.5, 0.42), (0.5, 0.5))
_ALTERNATE = (
    Motion("pan_left", 1.08, 1.08, (0.62, 0.5), (0.38, 0.5)),
    Motion("pan_right", 1.08, 1.08, (0.38, 0.5), (0.62, 0.5)),
    Motion("zoom_in", 1.0, 1.14, (0.5, 0.45), (0.5, 0.55)),
    Motion("shake", 1.06, 1.06, (0.5, 0.5), (0.5, 0.5), 0.012),
    Motion("zoom_out", 1.16, 1.0, (0.45, 0.5), (0.5, 0.5)),
)
_HOLD = Motion("zoom_in", 1.0, 1.06, (0.5, 0.45), (0.5, 0.5))


def plan_camera(scene_id: int, role: str, seed: int = 0) -> Motion:
    """Deterministic camera per scene: open snaps, body varies, payoff holds."""
    if scene_id == 1:
        return _OPEN
    if role in ("payoff", "payoff+cua"):
        return _HOLD
    rng = random.Random(seed * 31337 + scene_id)
    m = _ALTERNATE[(scene_id + seed) % len(_ALTERNATE)]
    if m.kind == "shake":  # keep shake subtle + seeded
        return Motion(m.kind, m.zoom_from, m.zoom_to, m.focus_from, m.focus_to,
                      m.shake_amp * (0.5 + rng.random()))
    return m


def ken_burns(src: Frame, motion: Motion, progress: float, seed: int = 0) -> Frame:
    """Crop-resample one camera step. progress 0..1, nearest-neighbor."""
    W, H = src.w, src.h
    p = min(1.0, max(0.0, progress))
    z = motion.zoom_from + (motion.zoom_to - motion.zoom_from) * p
    z = max(1.0, z)
    cw, ch = W / z, H / z
    fx = motion.focus_from[0] + (motion.focus_to[0] - motion.focus_from[0]) * p
    fy = motion.focus_from[1] + (motion.focus_to[1] - motion.focus_from[1]) * p
    cx, cy = fx * W, fy * H
    if motion.kind == "shake":
        amp = motion.shake_amp * W
        t = p * math.pi * 2 * 3  # three wobbles across the clip
        rng = random.Random(seed)
        cx += amp * math.sin(t) + amp * (rng.random() * 2 - 1) * 0.5
        cy += amp * math.cos(t * 1.7) + amp * (rng.random() * 2 - 1) * 0.5

    x0 = min(max(cx - cw / 2, 0.0), max(0.0, W - cw))
    y0 = min(max(cy - ch / 2, 0.0), max(0.0, H - ch))

    # precomputed source columns — reused for every row (fast path)
    xs = [min(W - 1, int(x0 + (ox + 0.5) * cw / W)) for ox in range(W)]
    flat = bytes(src.px)  # immutable, fast slicing
    out = Frame(W, H, (0, 0, 0))
    ostride = W * 3
    for oy in range(H):
        sy = min(H - 1, int(y0 + (oy + 0.5) * ch / H))
        rb = sy * ostride
        out.px[oy * ostride:(oy + 1) * ostride] = b"".join(
            flat[rb + i * 3:rb + i * 3 + 3] for i in xs
        )
    return out


def _frames_for(duration_s: float, fps: int) -> int:
    return max(1, int(round(duration_s * fps)))


def render_parallax(base_bg: Frame, geo: dict, motion: Motion, progress: float,
                    seed: int = 0) -> Frame:
    """2.5D: background crop-moves one way, foreground drifts the other.

    The image-from-a-still finally BREATHES — focal block and dialogue pill
    float over the plate with independent motion (DepthFlow idea, stdlib).
    """
    frame = ken_burns(base_bg, motion, progress, seed)
    W = base_bg.w
    p = min(1.0, max(0.0, progress))
    amp = max(4, W // 90)
    phase = progress * math.pi * 2
    dx = int(amp * math.sin(phase)) * (-1 if motion.kind != "push_in_fg" else 1)
    dy = int(amp * 0.35 * math.cos(phase * 0.5))
    if motion.kind == "push_in_fg":
        dx = int(-amp * 0.6 * p)
        dy = int(-amp * 0.6 * p)
    draw_fg(frame, geo, dx=dx, dy=dy)
    return frame


def stitch(
    sb: Storyboard,
    out_dir: str | Path,
    *,
    fps: int = 2,
    width: int = FRAME_W,
    height: int = FRAME_H,
    accent: tuple[int, int, int] | None = None,
    seed: int = 0,
    animation: str = "kenburns",
) -> dict:
    """Storyboard -> base frames -> animated sub-frames + timeline.json."""
    if fps <= 0:
        raise ValueError("fps must be > 0")
    d = Path(out_dir)
    frames_dir = d / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)

    scenes = sb.scenes
    metas = sb.drivers
    total_frames = 0
    entries: list[dict] = []
    n = len(scenes)
    for scene, meta in zip(scenes, metas):
        base = render_frame(
            FrameSpec(
                scene_id=scene.id,
                headline=sb.title,
                vo_line=scene.vo_line,
                badge=f"S{scene.id:02d}/{n:02d}",
                driver=meta["driver"],
                role=meta["role"],
                progress=(scene.t_start + scene.t_end) / 2 / max(0.001, scenes[-1].t_end),
                cohort=sb.cohort,
                accent=accent,
            ),
            width=width,
            height=height,
            seed=seed + scene.id,
        )
        motion = plan_camera(scene.id, meta["role"], seed)
        if animation == "parallax" and scene.id % 2 == 0:
            motion = Motion("parallax_orbit", 1.06, 1.06,
                            (0.55, 0.5), (0.45, 0.5))
        geo = scene_geometry(
            FrameSpec(
                scene_id=scene.id, headline=sb.title, vo_line=scene.vo_line,
                badge=f"S{scene.id:02d}/{n:02d}", driver=meta["driver"],
                role=meta["role"],
                progress=(scene.t_start + scene.t_end) / 2 / max(0.001, scenes[-1].t_end),
                cohort=sb.cohort, accent=accent,
            ),
            width=width, height=height, seed=seed + scene.id,
        ) if animation == "parallax" else None
        base_bg = None
        if geo is not None:
            base_bg = render_frame(
                FrameSpec(
                    scene_id=scene.id, headline=sb.title, vo_line=scene.vo_line,
                    badge=f"S{scene.id:02d}/{n:02d}", driver=meta["driver"],
                    role=meta["role"],
                    progress=(scene.t_start + scene.t_end) / 2 / max(0.001, scenes[-1].t_end),
                    cohort=sb.cohort, accent=accent,
                ),
                width=width, height=height, seed=seed + scene.id,
                include_fg=False,
            )
        count = _frames_for(scene.t_end - scene.t_start, fps)
        for k in range(count):
            progress = k / max(1, count - 1) if count > 1 else 0.0
            if geo is not None:
                frame = render_parallax(base_bg, geo, motion, progress,
                                        seed + scene.id * 10 + k)
            else:
                frame = ken_burns(base, motion, progress, seed + scene.id * 10 + k)
            name = f"frame_{total_frames + 1:05d}.png"
            frame.write_png(frames_dir / name)
            entries.append({
                "file": f"frames/{name}",
                "scene": scene.id,
                "t_start": round(scene.t_start + (scene.t_end - scene.t_start) * (k / count), 3),
                "t_end": round(scene.t_start + (scene.t_end - scene.t_start) * ((k + 1) / count), 3),
                "duration": round((scene.t_end - scene.t_start) / count, 3),
                "motion": motion.kind,
                "retention_role": meta["role"],
                "neuro_driver": meta["driver"],
                "sfx": meta["sfx"],
                "silence_before_s": meta.get("silence_before_s", 0.0)
                if k == 0 else 0.0,
            })
            total_frames += 1

    timeline = {
        "title": sb.title,
        "cohort": sb.cohort,
        "seed": sb.seed,
        "fps": fps,
        "animation": animation,
        "size": [width, height],
        "maths": sb.math_line,
        "frame_count": total_frames,
        "total_s": scenes[-1].t_end if scenes else 0.0,
        "silence_drop_s": SILENCE_DROP_S,
        "note": "PREVIZ animatic — final footage still requires the HAAN gate",
        "frames": entries,
    }
    (d / "timeline.json").write_text(
        json.dumps(timeline, indent=2), encoding="utf-8"
    )
    return timeline


def read_timeline(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))
