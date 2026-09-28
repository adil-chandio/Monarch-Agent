"""Concat bridge - Monarch board/truth -> jub0t/Concat agent commands (G-law clean).

The operator ordered CapCut-class editing power (auto-captions, keyframes,
effects, 4K export) on our pipeline. Concat (jub0t/Concat, AGPL-3.0 beta)
takes JSONL commands via ``concat-cli api`` - so Monarch EMITS that recipe
from its own artifacts (board.json, timeline.json, captions.srt,
vo/vo_track.wav, sfx/*.wav). Our board stays the truth; Concat is only the
camera-operator that flies it into an MP4 - on the OPERATOR'S PC.

Hard laws honored here (PRODUCTION_LAW_V2):
- zero-dependency: this module emits text; it never imports/links Concat
  (AGPL separate tool, standing order #2)
- every method/op we emit is checked against the REAL Concat API surface
  (docs/api/methods.md, docs/api/edits.md @ v0.2.4) - unknown = ValueError
- G16: export name is versioned (<slug>_v1_final.mp4)
- L13/G7: the summary REMINDS the operator to ffprobe + speech-band check
  the final file; an export is guilty until verified
"""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

# Real API surface @ Concat v0.2.4 (docs/api/methods.md + edits.md).
# If Concat adds methods, extend BOTH sets from THEIR docs - never guess.
METHODS = {
    "project.create", "project.open", "project.get", "project.save",
    "project.list", "project.close", "project.document", "project.setVideo",
    "media.import", "media.probe", "catalogue.list",
    "edit.apply", "edit.undo", "edit.redo",
    "template.list", "template.instantiate", "template.save",
    "preview.frame", "export.run", "export.cancel",
}
OPS = {
    "addClip", "addClipAtFirstFree", "addLayerClip", "addMedia", "addTextClip",
    "addTrack", "addTimeline", "removeTimeline", "renameTimeline",
    "selectTimeline", "moveTimeline", "setTimelineVideo",
    "updateClip", "removeClip", "moveClip", "splitClip", "detachAudio",
    "setClipKey", "clearClipKey", "clearClipKeys",
}

VO_TRACK = "T2"          # starter lanes T1..T4 per docs/api/edits.md
SFX_TRACK = "T3"


def _slug(title: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", str(title).lower()).strip("-")
    return s[:40] or "monarch-edit"


def _req(i: int, method: str, params: dict) -> dict:
    if method not in METHODS:
        raise ValueError(f"method {method!r} not in Concat API surface")
    return {"jsonrpc": "2.0", "id": i, "method": method, "params": params}


def _cmd(i: int, project_path: str, op: str, command: dict) -> dict:
    if op not in OPS:
        raise ValueError(f"edit op {op!r} not in Concat API surface")
    full = {"op": op, **command}
    return _req(i, "edit.apply",
                {"path": project_path, "command": full})


def emit_concat_plan(subject: str | Path, *, out: str | Path | None = None,
                     codec: str = "h264", crf: int = 20,
                     preset: str = "medium") -> dict:
    """Read a make-video dir -> write concat_recipe.jsonl (+ summary)."""
    d = Path(subject)
    if not d.is_dir():
        raise ValueError(f"subject dir not found: {d}")

    tl_p = d / "timeline.json"
    if not tl_p.is_file():
        raise ValueError("timeline.json missing - run make-video first (G14: "
                         "the timeline is the truth we hand the editor)")
    tl = json.loads(tl_p.read_text(encoding="utf-8"))
    rows = tl.get("frames") or []
    if not rows:
        raise ValueError("timeline.json has no frame rows - nothing to cut")

    width, height = (tl.get("size") or [1080, 1920])[:2]
    fps = int(tl.get("fps", 30))
    slug = _slug(tl.get("title") or d.name)
    location = str(d.resolve())

    lines: list[dict] = []
    n = 0

    def nxt() -> int:
        nonlocal n
        n += 1
        return n

    # deterministic media ids (docs: media are m1, m2, ... in import order)
    media_counter = 0

    def import_media(abs_path: str) -> str:
        nonlocal media_counter
        media_counter += 1
        lines.append(_req(nxt(), "media.import",
                          {"path": location, "file": abs_path}))
        return f"m{media_counter}"

    # 1) project
    lines.append(_req(nxt(), "project.create",
                      {"location": location, "name": f"{slug} edit"}))

    # 2) import every frame once, then lay clips at OUR times (board = truth)
    frame_media: dict[str, str] = {}
    for row in rows:
        f = str(row.get("file", ""))
        if not f or f in frame_media:
            continue
        if (d / f).suffix.lower() not in (".png", ".jpg", ".jpeg"):
            continue
        frame_media[f] = import_media(str((d / f).resolve()))
    n_video = 0
    for row in rows:
        f = str(row.get("file", ""))
        if f not in frame_media:
            continue
        n_video += 1
        lines.append(_cmd(nxt(), location, "addClip", {
            "mediaId": frame_media[f], "trackId": "T1",
            "start": round(float(row.get("t_start", 0.0)), 3),
        }))

    # 3) VO under everything (L8: voice wins) + sfx per clip start (G13);
    #    a wav imports ONCE and is placed many times - real-editor behavior
    vo_wav = d / "vo" / "vo_track.wav"
    if vo_wav.is_file():
        vo_id = import_media(str(vo_wav.resolve()))
        lines.append(_cmd(nxt(), location, "addClip", {
            "mediaId": vo_id, "trackId": VO_TRACK, "start": 0.0}))
    sfx_media: dict[str, str] = {}
    for row in rows:
        scene_no = int(row.get("scene", 0) or 0)
        if not scene_no:
            continue
        cands = sorted(d.glob(f"sfx/scene_{scene_no:02d}_*.wav"))
        if not cands:
            continue
        rel = cands[0].relative_to(d).as_posix()
        if rel not in sfx_media:
            sfx_media[rel] = import_media(str(cands[0].resolve()))
        lines.append(_cmd(nxt(), location, "addClip", {
            "mediaId": sfx_media[rel], "trackId": SFX_TRACK,
            "start": round(float(row.get("t_start", 0.0)), 3),
        }))

    # 4) captions as lower-third text clips (G11 parity in the editor;
    #    word-level karaoke burn stays our render-side standard)
    srt_p = d / "captions.srt"
    if srt_p.is_file():
        board = json.loads((d / "board.json").read_text(encoding="utf-8"))
        scenes = board.get("scenes", []) if isinstance(board, dict) else board
        for s in scenes:
            line_txt = str(s.get("vo_line", "")).strip()
            if not line_txt:
                continue
            lines.append(_cmd(nxt(), location, "addTextClip", {
                "above": True,
                "start": round(float(s.get("t_start", 0.0)), 3),
                "duration": round(max(0.5, float(s.get("t_end", 0.0))
                                      - float(s.get("t_start", 0.0))), 3),
                "offsetY": -0.55,               # lower third (safe zone)
                "style": {"content": line_txt},
            }))

    # 5) save + export (G16 versioned name)
    lines.append(_req(nxt(), "project.save", {"path": location}))
    export_name = f"{slug}_v1_final.mp4"
    lines.append(_req(nxt(), "export.run", {
        "path": location, "output": str((d / export_name).resolve()),
        "width": int(width), "height": int(height),
        "codec": codec, "crf": int(crf), "preset": preset,
    }))

    # final honesty pass: every op we emitted is whitelisted (double gate)
    for r in lines:
        if r["method"] == "edit.apply":
            assert r["params"]["command"]["op"] in OPS

    target = Path(out) if out else d / "concat_recipe.jsonl"
    target.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in lines) + "\n",
        encoding="utf-8")

    ffprobe = shutil.which("ffprobe")
    plan = {
        "recipe": str(target),
        "commands": len(lines),
        "clips": n_video,
        "text_clips": sum(1 for r in lines
                          if r["method"] == "edit.apply"
                          and r["params"]["command"]["op"] == "addTextClip"),
        "export": str(d / export_name),
        "resolution": f"{width}x{height}",
        "fps": fps,
        "next_steps": [
            "1. operator PC: install Concat (github.com/jub0t/Concat releases)",
            "2. concat-cli api < " + str(target),
            "3. L13: ffprobe the export - duration +-0.5s vs timeline.json, "
            "1080x1920, h264/aac, both streams",
            "4. G7/L3: speech-band volumedetect on first/mid/last VO windows "
            "- broadband alone lies",
        ],
    }
    if not ffprobe:
        plan["next_steps"].append(
            "(ffprobe not on PATH here - checks run on the operator PC)")
    return plan
