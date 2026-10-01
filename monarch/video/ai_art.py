"""AI-art fusion stage: keyframe images -> animated vertical Short.

Operator flow (wish 2026-09-28): "pehle images banaye, phir un images ko
animate karne ke liye prompt banake unko animate karen" - in stickman
style. Three steps, all sandbox-safe:

  1. prompt_plan(board)  -> deterministic per-keyframe prompt plan,
                            written to ai_prompts.json for the agent
  2. the agent generates the stickman-style keyframes OUT of band
     (the image tool is an agent capability, never a sandbox dependency
     - egress law holds)
  3. require_keyframes() -> fail-closed until every key<N>.png exists
  4. render_ai_short()   -> Ken Burns per keyframe, concat, subtitle
                            burn, loudnorm mix, drift-checked

Laws honored: images carry NO text (RENDER_MEMORY miss-#2); prompts are
English-only with a no-text clause and never carry desi words (V6 M4);
single focal subject per frame (M3); zoom cap 1.08 (M10); end-screen
right 40% stays clear on the closing pose (M13); video length = audio
truth (L13 drift <= 0.5s); loudnorm I=-14 TP=-1.5 (W-B2); HAAN gates
the upload.
"""

from __future__ import annotations

import json
import math
import re
import subprocess
import wave
from pathlib import Path

from .render import ffmpeg_exe, measure_lufs

ZOOM_CAP = 0.08          # M10: never beyond 1.08 total zoom
DEFAULT_ZOOM = 0.05      # ideal 1.0 -> 1.05 drift per keyframe
NO_TEXT_CLAUSE = "no text, no letters, no numbers, no watermark"

# xfade morph transitions (forensic-probed live 2026-09-28: filter
# exists in the sandbox ffmpeg build; minterpolate silently emits 0
# frames on yuv444p - never used). Blend-morphs between keyframes.
XFADE_SET = {
    "none", "fade", "dissolve", "wipeleft", "wiperight", "wipeup",
    "wipedown", "slideleft", "slideright", "slideup", "slidedown",
    "circleopen", "circleclose", "radial", "smoothleft", "smoothright",
    "zoomin",
}
DEFAULT_XFADE = "fade"   # classic pencil-dissolve feel

# Roman-Urdu tokens that must never leak into an image prompt (M4).
_DESI_TOKENS = {
    "bilkul", "jhakaas", "zabardast", "karo", "karna", "banaye", "banayo",
    "banao", "nahi", "nahin", "acha", "achha", "maza", "dekh", "dekho",
    "sun", "suno", "yeh", "ye", "woh", "kya", "hai", "hain",
}

# Per-role three-pose animation arc: base -> animate -> settle.
ROLE_ARCS: dict[str, tuple[str, str, str]] = {
    "hook": (
        "establish the subject in one strong dominant pose",
        "lean in pointing straight at the viewer as the secret is exposed, "
        "motion smear lines behind the arm",
        "pull back with a triumphant did-you-catch-it reaction",
    ),
    "silence-sting": (
        "reach toward the glowing object in frozen silence",
        "recoil in a huge silent scream while the stars stretch into "
        "motion streaks",
        "clutch the mouth with both hands, eyes huge, everything frozen",
    ),
    "payoff+cua": (
        "pick up the prize and dust it off with a sly grin",
        "raise the prize overhead in a proud ta-da pose",
        "wave at the viewer with the right side of the frame kept empty",
    ),
}
DEFAULT_ARC = (
    "establish the subject in one strong pose",
    "push the emotion bigger, lean toward the viewer",
    "settle into the closing pose",
)


def _lint_english(text: str) -> str:
    """Fail-closed M4: prompts are ASCII English without desi tokens."""
    if not text or not text.strip():
        raise ValueError("empty visual text in board scene")
    bad = sorted(t for t in _DESI_TOKENS
                 if re.search(rf"\b{re.escape(t)}\b", text.lower()))
    if bad:
        raise ValueError(f"desi word(s) {bad} in image prompt text (M4): "
                         f"{text[:80]!r} - rewrite the board visual in English")
    return text.strip()


def prompt_plan(board: dict) -> list[dict]:
    """One prompt per keyframe: 3 poses per scene, deterministic."""
    scenes = board.get("scenes") if isinstance(board, dict) else None
    if not scenes:
        raise ValueError("board has no scenes - run make-video first")
    plan: list[dict] = []
    for i, s in enumerate(scenes, 1):
        role = str(s.get("retention_role", "hook"))
        arc = ROLE_ARCS.get(role, DEFAULT_ARC)
        visual = _lint_english(str(s.get("visual", board.get("title", ""))))
        for j, pose in enumerate(arc, 1):
            prompt = (
                "hand-drawn minimalist stickman cartoon frame, expressive "
                f"white ink stick figure, {pose}, scene: {visual}, "
                "near-black void background with tiny stars and a thin "
                "crescent moon, bold confident ink strokes, high contrast, "
                "single focal subject, vertical 9:16 composition, "
                + NO_TEXT_CLAUSE
            )
            plan.append({
                "key": (i - 1) * 3 + j,
                "scene": i,
                "role": role,
                "pose_step": j,
                "prompt": prompt,
                "t_start": s.get("t_start"),
                "t_end": s.get("t_end"),
            })
    return plan


def write_prompt_plan(plan: list[dict], path: str | Path) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    return p


def frame_plan(board: dict, audio_s: float, fps: int = 10) -> list[int]:
    """Frames per keyframe; leftover audio (end-screen tail) holds the
    final keyframe. Sum == round(audio_s * fps)."""
    scenes = board.get("scenes") or []
    n = len(scenes) * 3
    if n == 0:
        raise ValueError("board has no scenes")
    total = int(round(audio_s * fps))
    counts = [0] * n
    for i, s in enumerate(scenes):
        span = max(0.0, float(s.get("t_end", 0)) - float(s.get("t_start", 0)))
        f = int(round(span * fps))
        base, rem = divmod(max(f, 6), 3)          # >=2 frames per pose
        for j in range(3):
            counts[(i - 1) * 3 + j] = base + (1 if j == 1 else 0)
        if rem:
            counts[(i - 1) * 3 + 1] += rem        # middle pose breathes most
    tail = total - sum(counts)
    if tail > 0:
        counts[-1] += tail                        # hold last pose (end-screen)
    elif tail < 0:
        for k in range(n - 1, -1, -1):            # trim from the tail back
            take = min(counts[k] - 2, -tail)
            counts[k] -= take
            tail += take
            if tail >= 0:
                break
    if sum(counts) != total:
        raise ValueError("audio too short for the keyframe plan "
                         f"({sum(counts)} min frames vs {total} audio "
                         "frames)")
    return counts


def require_keyframes(d: str | Path, count: int = 9) -> list[Path]:
    """Fail-closed: every key<N>.png must exist (agent-generated)."""
    base = Path(d)
    missing = [f"key{i}.png" for i in range(1, count + 1)
               if not (base / f"key{i}.png").is_file()]
    if missing:
        raise ValueError(
            f"missing AI keyframes in {base}: {', '.join(missing)} - "
            "generate them from ai_prompts.json (agent image tool, "
            "stickman style), then re-run")
    return [base / f"key{i}.png" for i in range(1, count + 1)]


def _audio_s(path: Path) -> float:
    with wave.open(str(path), "rb") as w:
        return w.getnframes() / w.getframerate()


def render_ai_short(frames_dir: str | Path, wav: str | Path,
                    out: str | Path, board: dict, *,
                    ass: str | Path | None = None, fps: int = 10,
                    zoom: float = DEFAULT_ZOOM, crf: int = 20,
                    transition: str = DEFAULT_XFADE,
                    xfade_s: float = 0.25) -> dict:
    """Animate the keyframes (Ken Burns <= 1+ZOOM_CAP) and mix.

    transition: xfade morph between consecutive keyframes (fade,
    dissolve, zoomin, ... see XFADE_SET) or 'none' for hard cuts.
    Transition overlap seconds are re-added as tail hold so the video
    still lands on the audio truth (L13).
    """
    if transition not in XFADE_SET:
        raise ValueError(f"transition {transition!r} not in XFADE_SET")
    if transition != "none" and xfade_s <= 0:
        raise ValueError("xfade_s must be > 0 when transition is on")
    if zoom > ZOOM_CAP:
        raise ValueError(f"zoom {zoom} exceeds the M10 cap {ZOOM_CAP} "
                         "(total zoom would pass 1.08)")
    keys = require_keyframes(frames_dir, len(board.get("scenes", [])) * 3)
    want = _audio_s(Path(wav)) if Path(wav).is_file() else None
    if want is None:
        raise ValueError(f"no master mix at {wav}")
    counts = frame_plan(board, want, fps=fps)
    d = Path(out).parent
    d.mkdir(parents=True, exist_ok=True)
    ff = ffmpeg_exe()
    segs: list[Path] = []
    for i, (key, n) in enumerate(zip(keys, counts), 1):
        rate = zoom / (n - 1) if n > 1 else 0.0
        vf = (
            "scale=1080:1920:force_original_aspect_ratio=increase,"
            "crop=1080:1920,"
            f"zoompan=z='1+{rate:.6f}*on':d=1:x='iw/2-(iw/zoom/2)':"
            f"y='ih/2-(ih/zoom/2)':s=1080x1920:fps={fps}"
        )
        seg = d / f"ai_seg_{i:02d}.mp4"
        r = subprocess.run(
            [ff, "-y", "-hide_banner", "-loglevel", "error", "-loop", "1",
             "-framerate", str(fps), "-t", f"{n / fps:.3f}", "-i", str(key),
             "-vf", vf, "-frames:v", str(n), "-c:v", "libx264",
             "-preset", "veryfast", "-crf", str(crf),
             "-pix_fmt", "yuv420p", str(seg)],
            capture_output=True, text=True)
        if r.returncode != 0:
            raise ValueError(f"keyframe {i} segment failed: "
                             f"{(r.stderr or r.stdout).strip()[:200]}")
        segs.append(seg)
    lst = d / "ai_concat.txt"
    lst.write_text("\n".join(f"file '{s.resolve()}'" for s in segs) + "\n",
                   encoding="utf-8")
    silent = d / "ai_silent.mp4"
    if transition == "none" or len(segs) == 1:
        r = subprocess.run(
            [ff, "-y", "-hide_banner", "-loglevel", "error", "-f", "concat",
             "-safe", "0", "-i", str(lst), "-c", "copy", str(silent)],
            capture_output=True, text=True)
        if r.returncode != 0:
            raise ValueError(f"concat failed: "
                             f"{(r.stderr or r.stdout).strip()[:200]}")
    else:
        # xfade morph chain. offset_k = sum(durs[:k]) - k*d_eff; the
        # overlap seconds are cloned back at the tail (tpad) so the
        # total lands on the audio truth (L13).
        durs = [c / fps for c in counts]
        d_eff = min(xfade_s, min(durs) * 0.5)
        pad_s = (len(segs) - 1) * d_eff
        parts: list[str] = []
        prev = "[0:v]"
        off = 0.0
        for k in range(1, len(segs)):
            off += durs[k - 1] - d_eff
            parts.append(f"{prev}[{k}:v]xfade=transition={transition}:"
                         f"duration={d_eff:.3f}:offset={off:.3f}[x{k}]")
            prev = f"[x{k}]"
        parts.append(f"{prev}tpad=stop_mode=clone:"
                     f"stop_duration={pad_s:.3f},format=yuv420p[vout]")
        cmd = [ff, "-y", "-hide_banner", "-loglevel", "error"]
        for s in segs:
            cmd += ["-i", str(s)]
        cmd += ["-filter_complex", ";".join(parts), "-map", "[vout]",
                "-c:v", "libx264", "-preset", "veryfast", "-crf", str(crf),
                "-pix_fmt", "yuv420p", str(silent)]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            raise ValueError(f"xfade chain failed: "
                             f"{(r.stderr or r.stdout).strip()[:300]}")
    out_p = Path(out)
    cmd = [ff, "-y", "-hide_banner", "-loglevel", "error",
           "-i", str(silent), "-i", str(wav),
           "-c:v", "libx264", "-preset", "veryfast", "-crf", str(crf),
           "-pix_fmt", "yuv420p"]
    if ass is not None and Path(ass).is_file():
        esc = str(Path(ass).resolve()).replace("\\", "\\\\").replace(":", "\\:")
        cmd += ["-vf", f"subtitles={esc}"]
    cmd += ["-c:a", "aac", "-b:a", "160k",
            "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000",
            "-movflags", "+faststart", str(out_p)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise ValueError(f"final mix failed: {(r.stderr or r.stdout).strip()[:200]}")
    info = subprocess.run([ff, "-hide_banner", "-i", str(out_p)],
                          capture_output=True, text=True)
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", info.stderr)
    got = float(m.group(1)) * 3600 + float(m.group(2)) * 60 + float(m.group(3))
    drift = abs(got - want)
    return {
        "output": str(out_p),
        "frames": sum(counts),
        "counts": counts,
        "fps": fps,
        "want_s": round(want, 3),
        "got_s": round(got, 3),
        "drift_s": round(drift, 3),
        "bytes": out_p.stat().st_size,
        "duration_ok": drift <= 0.5,
        "zoom_max": round(1 + zoom, 3),
        "transition": transition,
        "law_note": ("AI keyframes -> Ken Burns <=1.08 -> xfade morph -> "
                     "burn -> loudnorm mix; images text-free (miss-#2, "
                     "M4); inputs: keyframe segs + master mix"),
    }


def cli_stage(out_dir: str | Path, frames_dir: str | Path | None = None,
              *, render: bool = True,
              transition: str = DEFAULT_XFADE) -> int:
    """Shared CLI path: write ai_prompts.json, fail-closed on frames,
    render when all keyframes exist. Returns the process exit code."""
    base = Path(out_dir)
    board_p = base / "board.json"
    if not board_p.is_file():
        print(f"FAIL no board.json in {base} - run make-video first")
        return 2
    board = json.loads(board_p.read_text(encoding="utf-8"))
    plan = prompt_plan(board)
    write_prompt_plan(plan, base / "ai_prompts.json")
    n = len(plan)
    fdir = Path(frames_dir) if frames_dir else base / "ai_frames"
    print(f"AI-ART: {n}-keyframe prompt plan -> {base / 'ai_prompts.json'}")
    try:
        require_keyframes(fdir, n)
    except ValueError as e:
        print(f"PENDING {e}")
        return 2
    if not render:
        return 0
    wav = base / "master_mix.wav"
    if not wav.is_file():
        print(f"FAIL no master_mix.wav in {base} - re-run with --with-mix")
        return 2
    ass = base / "v6.ass"
    try:
        m = render_ai_short(fdir, wav, base / "ai_short.mp4", board,
                            ass=ass if ass.is_file() else None,
                            transition=transition)
    except ValueError as e:
        print(f"FAIL {e}")
        return 2
    print(f"AI-ART RENDER: {Path(m['output']).name} | {m['frames']}f | "
          f"drift {m['drift_s']}s | zoom {m['zoom_max']} | "
          f"{m['bytes'] // 1024}KB | laws: {m['duration_ok']}")
    print("HAAN still gates the upload. You upload.")
    return 0
