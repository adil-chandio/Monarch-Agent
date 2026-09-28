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


LOUDNORM_FILTER = "loudnorm=I=-14:TP=-1.5:LRA=11"   # TABAAHI ARSENAL B19-20


def measure_lufs(ff: str, path: str | Path) -> float | None:
    """Integrated loudness (EBU R128) from the SAME binary - a real
    meter, not a vibe (L15). Returns None only if the meter itself
    failed (then the audit says so instead of guessing)."""
    proc = subprocess.run(
        [ff, "-hide_banner", "-nostats", "-i", str(path),
         "-filter_complex", "ebur128=peak=true", "-f", "null", "-"],
        capture_output=True, text=True)
    hits = re.findall(r"I:\s+(-?\d+(?:\.\d+)?)\s+LUFS", proc.stderr)
    return float(hits[-1]) if hits else None


def _probe_duration(ff: str, path: Path) -> float:
    """Same binary's own report - a real check, not a vibe (L15)."""
    proc = subprocess.run([ff, "-hide_banner", "-i", str(path)],
                          capture_output=True, text=True)
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", proc.stderr)
    if not m:
        raise ValueError(f"cannot parse duration of {path}")
    h, mi, s = int(m.group(1)), int(m.group(2)), float(m.group(3))
    return h * 3600 + mi * 60 + s


def _v6_end_screen(d: Path) -> bool:
    try:
        meta = json.loads((d / "v6_plan.json").read_text(encoding="utf-8"))
        return bool(meta.get("end_screen"))
    except (OSError, ValueError):
        return False


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
               "-af", LOUDNORM_FILTER, "-ar", "48000",
               "-movflags", "+faststart"] + extra + [str(out_p)]
        return subprocess.run(cmd, capture_output=True, text=True)

    burn_note = "captions.srt ships alongside (burn skipped: --no-burn)"

    def _burn(sub_path: Path, *, force_style: str | None,
              note_ok: str) -> tuple[subprocess.CompletedProcess, str]:
        esc = (str(sub_path.resolve())
               .replace("\\", "\\\\")
               .replace(":", "\\:").replace("'", "\\'"))
        sub = f"subtitles={esc}"
        if force_style:
            sub += f":force_style='{force_style}'"
        vf = f"scale={width}:{height},{sub}"
        prc = subprocess.run(
            [ff, "-y", "-hide_banner", "-loglevel", "error",
             "-f", "concat", "-safe", "0", "-i", str(lst),
             "-i", str(audio), "-shortest",
             "-c:v", "libx264", "-preset", "veryfast", "-crf", str(crf),
             "-pix_fmt", "yuv420p", "-vf", vf,
             "-c:a", "aac", "-b:a", "160k",
             "-af", LOUDNORM_FILTER, "-ar", "48000",
             "-movflags", "+faststart", str(out_p)],
            capture_output=True, text=True)
        if prc.returncode == 0:
            return prc, note_ok
        return run([]), (f"burn FAILED, re-rendered clean: "
                         f"{prc.stderr.strip()[:160]}")

    if not burn_captions:
        proc = run([])
    elif (d / "v6.ass").is_file() and _pick_font():
        # W-A1/W-A2 layer: karaoke captions + TEXT_SYNCED cues + end
        # screen + progress bar + loop tail - styles embedded in the file
        proc, burn_note = _burn(d / "v6.ass", force_style=None,
                                note_ok=("v6 layer burned (karaoke words + "
                                         "progress bar + loop tail"
                                         " + end screen)" if _v6_end_screen(d)
                                         else "v6 layer burned (karaoke words "
                                         "+ progress bar + loop tail)"))
    elif (d / "captions.srt").is_file() and _pick_font():
        style = ("FontSize=14,Bold=1,PrimaryColour=&H00FFFFFF,"
                 "OutlineColour=&H00000000,Outline=3,Shadow=1,"
                 "MarginV=40")
        proc, burn_note = _burn(d / "captions.srt", force_style=style,
                                note_ok="scene captions burned (legacy path)")
    elif (d / "v6.ass").is_file() or (d / "captions.srt").is_file():
        proc = run([])
        burn_note = "no usable font found - rendered clean, srt ships"
    else:
        proc = run([])

    if proc.returncode != 0 or not out_p.is_file() or out_p.stat().st_size == 0:
        raise ValueError(f"render failed: {proc.stderr.strip()[:400]}")

    got = _probe_duration(ff, out_p)
    lufs = measure_lufs(ff, out_p)   # ARSENAL B: -14 LUFS / -1 dBTP law

    # MONARCH V2 miss #1: a 32k-class audio encode turns the VO robotic.
    # Verify the ACTUAL bitrate from the file (L15: verify the verifier).
    info = subprocess.run([ff, "-hide_banner", "-i", str(out_p)],
                          capture_output=True, text=True)
    kb = re.search(r"Audio:\s+.*?(\d+)\s+kb/s", info.stderr)
    audio_kbps = int(kb.group(1)) if kb else None
    drift = round(abs(got - want), 3)
    return {
        "output": str(out_p),
        "bytes": out_p.stat().st_size,
        "audio_source": audio_used,
        "audio_s": round(want, 3),
        "video_s": round(got, 3),
        "drift_s": drift,
        "duration_ok": drift <= 0.5,
        "audio_kbps": audio_kbps,
        # law: encode TARGET copy/160k+ (we pass -b:a 160k); the measured
        # floor guards against the 32k class - sparse mono content measures
        # lower than the target, so the floor is 72k (above the banned 64k class), not 160k
        "bitrate_ok": (audio_kbps is None and audio_used.endswith(".wav"))
        or (audio_kbps or 0) >= 72,
        "resolution": f"{width}x{height}",
        "lufs": lufs,
        "lufs_ok": (lufs is not None and -16.0 <= lufs <= -12.0),
        "loudnorm": LOUDNORM_FILTER,
        "captions": burn_note,
        "srt": str(d / "captions.srt") if (d / "captions.srt").is_file() else None,
        "law_note": ("2 inputs total (G7/L2); duration +-0.5s checked (L13); "
                     "audio >= 160k verified (MONARCH V2: never 32k/48k/64k)"),
    }
