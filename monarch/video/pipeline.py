"""End-to-end ``make_video``: topic -> previz animatic, fully deterministic.

Pipeline (every step gated, fail-closed):

1. :func:`monarch.video.director.plan_storyboard` — Neuro Playbook roles,
   Fountain screenplay, the real M3 gate.
2. SFX bank — one rendered cue per scene from :mod:`monarch.video.audio`
   (N5: riser -> 0.3s silence -> payoff drop is encoded by the director and
   honored here).
3. :func:`monarch.video.compositor.stitch` — Ken Burns frames + timeline.
4. ``manifest.json`` — everything an operator (or the agent) needs at the stop.

This is the PREVIZ layer: no footage generation, no upload. The HAAN gate
still owns the final render (constitution 05/08), unchanged.
"""

from __future__ import annotations

import json
from pathlib import Path

from monarch.video import audio
from monarch.video.compositor import stitch
from monarch.video.director import plan_storyboard, write_storyboard_files

DEFAULT_SR = 22050


def make_video(
    topic: str,
    out_dir: str | Path,
    *,
    length: float = 60.0,
    clip_s: float = 3.5,
    speaking_wps: float = 2.2,
    first_clip_s: float = 2.5,
    cohort: str = "genz",
    seed: int = 0,
    width: int = 1080,
    height: int = 1920,
    fps: int = 2,
    sr: int = DEFAULT_SR,
    accent: tuple[int, int, int] | None = None,
) -> dict:
    """Topic in, previz animatic out. Returns the manifest dict."""
    if width <= 0 or height <= 0:
        raise ValueError("width/height must be > 0")
    if sr <= 0:
        raise ValueError("sample rate must be > 0")

    sb = plan_storyboard(
        topic,
        length=length,
        clip_s=clip_s,
        speaking_wps=speaking_wps,
        first_clip_s=first_clip_s,
        cohort=cohort,
        seed=seed,
    )
    d = Path(out_dir)
    doc_paths = write_storyboard_files(sb, d)

    # SFX cues — one wav per scene, limiter on everything (N5 mix law)
    sfx_dir = d / "sfx"
    sfx_files: dict[int, str] = {}
    for scene, meta in zip(sb.scenes, sb.drivers):
        samples = audio.render_sfx(
            meta["sfx"], sr=sr, seed=sb.seed * 100 + scene.id,
            seconds=max(0.2, (scene.t_end - scene.t_start)),
            filters=["limiter"],
        )
        rel = f"sfx/scene_{scene.id:02d}_{meta['sfx']}.wav"
        audio.write_wav(d / rel, samples, sr)
        sfx_files[scene.id] = rel

    timeline = stitch(sb, d, fps=fps, width=width, height=height, accent=accent,
                      seed=sb.seed)

    manifest = {
        "agent": "monarch.video",
        "kind": "previz animatic (no footage, no upload — HAAN still gates render)",
        "topic": sb.topic,
        "title": sb.title,
        "cohort": sb.cohort,
        "seed": sb.seed,
        "maths": sb.math_line,
        "scene_count": len(sb.scenes),
        "total_s": timeline["total_s"],
        "fps": fps,
        "frame_count": timeline["frame_count"],
        "frame_size": [width, height],
        "sample_rate": sr,
        "files": {
            "screenplay": str(doc_paths["fountain"]),
            "board": str(doc_paths["board"]),
            "storyboard_card": str(doc_paths["card"]),
            "timeline": "timeline.json",
            "sfx": sfx_files,
        },
        "scenes": sb.board(),
    }
    (d / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest
