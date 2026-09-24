"""Render stage - previz frames + mix -> MP4, IN the sandbox (operator order 2026-09-24).

The operator ordered render in-repo (no PC; the Arena agent renders).
Laws honored (PRODUCTION_LAW_V2):
- L13/G14: output duration checked against the MIX (the truth) +-0.5s,
  via ffprobe when present, else the same ffmpeg's own Duration report.
- G7/L2: exactly 2 inputs (frame concat stream + audio) - the giant-graph
  failure cannot recur by construction.
- G16: output name versioned (<slug>_v1_render.mp4) unless --out given.
- G11: captions burned via subtitles filter when a usable font exists;
  on any burn failure we re-render clean and say so (never fake it).
  captions.srt ships regardless (platform-native captions stay king).
- Fail-closed: missing dir/timeline/audio = ValueError, exit 2.
"""

from __future__ import annotations

import json
import re
import subprocess
import wave
from pathlib import Path


def ffmpeg_exe() -> str:
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception as e:  # pragma: no cover - env without the wheel
        raise ValueError(
            "ffmpeg unavailable: pip install imageio-ffmpeg "
            f"(render is fail-closed, never silent) [{e}]") from e


def _slug(title: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", str(title).lower()).strip("-")
    return s[:40] or "monarch-render"


def audio_duration_s(wav_path: str | Path) -> float:
    with wave.open(str(wav_path), "rb") as w:
        return w.getnframes() / float(w.getframerate())


def _pick_font() -> str | None:
    for cand in sorted(Path("/usr/share/fonts").rglob("*Bold*")) + \
            sorted(Path("/usr/share/fonts").rglob("*bold*")):
        if cand.suffix.lower() in (".ttf", ".otf"):
            return str(cand)
    return None


def _probe_duration(ff: str, path: Path) -> float:
    """Same binary's own report - a real check, not a vibe (L15)."""
    proc = subprocess.run([ff, "-hide_banner", "-i", str(path)],
                          capture_output=True, text=True)
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", proc.stderr)
    if not m:
        raise ValueError(f"cannot parse duration of {path}")
    h, mi, s = int(m.group(1)), int(m.group(2)), float(m.group(3))
    return h * 3600 + mi * 60 + s


def render_mp4(subject: str | Path, *, out: str | Path | None = None,
               crf: int = 20, burn_captions: bool = True) -> dict:
    d = Path(subject)
    if not d.is_dir():
        raise ValueError(f"subject dir not found: {d}")
    tl_p = d / "timeline.json"
    if not tl_p.is_file():
        raise ValueError("timeline.json missing - run make-video first")
    tl = json.loads(tl_p.read_text(encoding="utf-8"))
    rows = [r for r in (tl.get("frames") or [])
            if (d / str(r.get("file", ""))).is_file()]
    if not rows:
        raise ValueError("timeline.json frame files missing on disk")

    audio = d / "master_mix.wav"
    audio_used = "master_mix.wav"
    if not audio.is_file():
        audio = d / "vo" / "vo_track.wav"
        audio_used = "vo/vo_track.wav"
    if not audio.is_file():
        raise ValueError("no master_mix.wav / vo_track.wav - make-video with "
                         "--voice-backend (silent render is a lie)")

    ff = ffmpeg_exe()
    width, height = (tl.get("size") or [1080, 1920])[:2]

    want = audio_duration_s(audio)
    vid_end = max(float(r.get("t_end", 0.0)) for r in rows)
    pad = max(0.0, want - vid_end) + 0.2     # cover the full VO (L1 skeleton)

    lst = d / "render_concat.txt"
    lines = ["ffconcat version 1.0"]
    for r in rows[:-1]:
        lines.append(f"file '{(d / str(r['file'])).resolve()}'")
        lines.append(f"duration {max(0.04, float(r['t_end']) - float(r['t_start'])):.3f}")
    last_dur = max(0.04, float(rows[-1]["t_end"]) - float(rows[-1]["t_start"]))
    lines.append(f"file '{(d / str(rows[-1]['file'])).resolve()}'")
    # concat demuxer honors the LAST entry's duration only if the file
    # repeats after it (documented quirk) - this hold covers the VO tail
    lines.append(f"duration {last_dur + pad:.3f}")
    lines.append(f"file '{(d / str(rows[-1]['file'])).resolve()}'")
    lst.write_text("\n".join(lines) + "\n", encoding="utf-8")

    slug = _slug(tl.get("title") or d.name)
    out_p = Path(out) if out else d / f"{slug}_v1_render.mp4"

    def run(extra: list[str]) -> subprocess.CompletedProcess:
        cmd = [ff, "-y", "-hide_banner", "-loglevel", "error",
               "-f", "concat", "-safe", "0", "-i", str(lst),
               "-i", str(audio),
               "-c:v", "libx264", "-preset", "veryfast", "-crf", str(crf),
               "-pix_fmt", "yuv420p", "-vf", f"scale={width}:{height}",
               "-c:a", "aac", "-b:a", "160k",
               "-movflags", "+faststart"] + extra + [str(out_p)]
        return subprocess.run(cmd, capture_output=True, text=True)

    burn_note = "captions.srt ships alongside (burn skipped: --no-burn)"
    if burn_captions and (d / "captions.srt").is_file():
        font = _pick_font()
        if font:
            srt_esc = (str((d / "captions.srt").resolve())
                       .replace("\\", "\\\\")
                       .replace(":", "\\:").replace("'", "\\'"))
            style = ("FontSize=14,Bold=1,PrimaryColour=&H00FFFFFF,"
                     "OutlineColour=&H00000000,Outline=3,Shadow=1,"
                     "MarginV=40")
            vf = f"scale={width}:{height},subtitles={srt_esc}:force_style='{style}'"
            proc = subprocess.run(
                [ff, "-y", "-hide_banner", "-loglevel", "error",
                 "-f", "concat", "-safe", "0", "-i", str(lst),
                 "-i", str(audio), "-shortest",
                 "-c:v", "libx264", "-preset", "veryfast", "-crf", str(crf),
                 "-pix_fmt", "yuv420p", "-vf", vf,
                 "-c:a", "aac", "-b:a", "160k",
                 "-movflags", "+faststart", str(out_p)],
                capture_output=True, text=True)
            if proc.returncode == 0:
                burn_note = "captions burned (scene-level; karaoke needs word timing)"
            else:
                burn_note = (f"burn FAILED, re-rendered clean: "
                             f"{proc.stderr.strip()[:160]}")
                proc = run([])
        else:
            proc = run([])
            burn_note = "no usable font found - rendered clean, srt ships"
    else:
        proc = run([])

    if proc.returncode != 0 or not out_p.is_file() or out_p.stat().st_size == 0:
        raise ValueError(f"render failed: {proc.stderr.strip()[:400]}")

    got = _probe_duration(ff, out_p)
    drift = round(abs(got - want), 3)
    return {
        "output": str(out_p),
        "bytes": out_p.stat().st_size,
        "audio_source": audio_used,
        "audio_s": round(want, 3),
        "video_s": round(got, 3),
        "drift_s": drift,
        "duration_ok": drift <= 0.5,
        "resolution": f"{width}x{height}",
        "captions": burn_note,
        "srt": str(d / "captions.srt") if (d / "captions.srt").is_file() else None,
        "law_note": "2 inputs total (G7/L2); duration +-0.5s checked (L13)",
    }
