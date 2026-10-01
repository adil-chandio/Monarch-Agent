#!/usr/bin/env python3
"""DEMO11 - full-system demo build recipe (recovery session 2026-10-01).

Tracked copy of the build script (the runnable one lives in
output/demo11/ while the sandbox holds it; output/ is gitignored, this
copy survives resets). Run: python3 monarch/scripts/demo11_full_system.py

Composition recipe (briefing):
  hook keys (12f each, xfade 0.25) + FK jump motion segment + payoff keys
  -> concat -> tpad/trim to audio truth -> v6.ass burn
  -> loudnorm I=-14:TP=-1.5:LRA=11 -> aac 160k

In-sandbox reality this session: VO TTS is network-blocked
(speech.platform.bing.com unreachable), so the bed is OUR warm music bed
+ SFX hits (proven monarch/video/mix.py + audio.py), captions burned via
the V6 karaoke layer. Every number below is measured, never assumed.

Outputs (output/demo11/):
  DEMO11_FULL.mp4   1080x1920 master
  DEMO11_PHONE.mp4  baseline-profile 720p max-compat (the upload file)
  DEMO11_PREVIEW.gif, demo11_*_sheet.png, index.html, demo11_report.json
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]          # repo root
sys.path.insert(0, str(ROOT))

from monarch.core.upload import sha256_of                              # noqa: E402
from monarch.video.ai_art import XFADE_SET, DEFAULT_XFADE              # noqa: E402
from monarch.video.audio import render_sfx, write_wav                  # noqa: E402
from monarch.video.mix import add_at, limiter, warm_bed                # noqa: E402
from monarch.video.overlays import v6_ass                              # noqa: E402
from monarch.video.render import ffmpeg_exe, measure_lufs              # noqa: E402
from monarch.video.stickman_art import (H, W, _encode_frames,          # noqa: E402
                                        motion_frames, scene_png)

OUT = Path(__file__).resolve().parent
SEGD = OUT / "segments"
FPS = 20
KEY_S = 1.10            # 22 frames @20fps
XFADE_S = 0.25
SR = 44100

#: (pose, prop, caption) - hook keys -> motion -> payoff keys
KEYS = [
    ("shock", None, "THE MOON"),
    ("point", None, "IS A HOLE"),
    ("shock", None, "SOMETHING LIVES IN IT"),
    ("crown", "crown", "A KING FELL IN"),
    ("bow", None, "NOBODY CAME BACK"),
    ("idle", None, "LOOK CLOSER"),
]
MOTION_CAPTION = "HE KEEPS JUMPING"
PAYOFF = [
    ("point", "magnifier", "THE CROWN IS NEW"),
    ("shock", None, "STILL NOT FOUND"),
    ("wave", None, "MONARCH FULL-SYSTEM DEMO"),
]


def run(cmd: list[str], what: str) -> None:
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise SystemExit(f"{what} FAILED:\n{(p.stderr or p.stdout)[:900]}")


def probe_dur(path: Path) -> float:
    p = subprocess.run([ffmpeg_exe(), "-hide_banner", "-i", str(path)],
                       capture_output=True, text=True)
    for line in p.stderr.splitlines():
        if "Duration:" in line:
            h, m, s = line.split("Duration:")[1].split(",")[0].strip().split(":")
            return int(h) * 3600 + int(m) * 60 + float(s)
    return 0.0


def key_segment(i: int, png: Path, frames: int, zoom: float = 0.05) -> Path:
    rate = zoom / (frames - 1)
    vf = (f"scale={W}:{H}:force_original_aspect_ratio=increase,"
          f"crop={W}:{H},"
          f"zoompan=z='1+{rate:.6f}*on':d=1:x='iw/2-(iw/zoom/2)':"
          f"y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={FPS}")
    seg = SEGD / f"seg_{i:02d}_key.mp4"
    run([ffmpeg_exe(), "-y", "-hide_banner", "-loglevel", "error",
         "-loop", "1", "-framerate", str(FPS), "-t", f"{frames / FPS:.4f}",
         "-i", str(png), "-vf", vf, "-frames:v", str(frames),
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
         "-pix_fmt", "yuv420p", str(seg)], f"key segment {i}")
    return seg


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    SEGD.mkdir(parents=True, exist_ok=True)
    ff = ffmpeg_exe()

    # ---------------- segments ----------------
    key_frames = round(KEY_S * FPS)                       # 22
    durs: list[float] = []
    segs: list[Path] = []
    n = 0
    for idx, (pose, prop, _cap) in enumerate(KEYS, 1):
        png = Path(scene_png(OUT / "keys" / f"key{idx}.png", pose=pose,
                             prop=prop, seed=42))
        segs.append(key_segment(idx, png, key_frames))
        durs.append(key_frames / FPS)
        n += 1

    # FK motion: jump is a 1.6s one-shot -> TWO cycles back-to-back (3.2s)
    jump = motion_frames("jump", fps=FPS)                 # 32 frames, 1.6s
    mframes = jump + jump                                 # 64 frames, 3.2s
    mseg = SEGD / "seg_motion.mp4"
    mres = _encode_frames(mframes, SEGD, fps=FPS, wav=None,
                          name="seg_motion.mp4",
                          frames_dir="motion_frames",
                          concat="motion_concat.txt")
    assert Path(mres["output"]) == mseg
    segs.append(mseg)
    durs.append(len(mframes) / FPS)

    for j, (pose, prop, _cap) in enumerate(PAYOFF, 1):
        png = Path(scene_png(OUT / "keys" / f"pay{j}.png", pose=pose,
                             prop=prop, seed=42))
        segs.append(key_segment(90 + j, png, key_frames))
        durs.append(key_frames / FPS)
        n += 1

    # ---------------- xfade morph chain (proven ai_art pattern) ----------
    d_eff = min(XFADE_S, min(durs) * 0.5)
    pad_s = (len(segs) - 1) * d_eff
    parts: list[str] = []
    # every input normalized first: same fps/size/SAR/TB - xfade refuses a
    # timebase mismatch (1/10240 vs 1/12800) instead of guessing
    for k in range(len(segs)):
        parts.append(f"[{k}:v]fps={FPS},scale={W}:{H},setsar=1,"
                     f"settb=AVTB,format=yuv420p[n{k}]")
    prev = "[n0]"
    off = 0.0
    for k in range(1, len(segs)):
        off += durs[k - 1] - d_eff
        parts.append(f"{prev}[n{k}]xfade=transition={DEFAULT_XFADE}:"
                     f"duration={d_eff:.3f}:offset={off:.3f}[x{k}]")
        prev = f"[x{k}]"
    parts.append(f"{prev}tpad=stop_mode=clone:stop_duration={pad_s:.3f},"
                 "format=yuv420p[vout]")
    silent = SEGD / "chain_silent.mp4"
    cmd = [ff, "-y", "-hide_banner", "-loglevel", "error"]
    for s in segs:
        cmd += ["-i", str(s)]
    cmd += ["-filter_complex", ";".join(parts), "-map", "[vout]",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
            "-pix_fmt", "yuv420p", "-r", str(FPS), str(silent)]
    run(cmd, "xfade chain")
    total = sum(durs)                                   # audio truth
    got = probe_dur(silent)
    print(f"chain: {len(segs)} segments, total {total:.2f}s, got {got:.3f}s")

    # ---------------- audio bed (VO TTS blocked -> music + SFX) ----------
    starts = []
    acc = 0.0
    for k, d in enumerate(durs):
        starts.append(acc)
        acc += d - d_eff
    bed = warm_bed(total, SR, seed=42)
    hits = [
        (0.0, "crescendo", 0.55),                       # intro build
        (starts[1], "sonar_ping", 0.30),                # the moon beats
        (starts[3], "sonar_ping", 0.26),
        (starts[6] - 1.6, "riser", 0.5),                # into the jump
        (starts[6] + 1.6, "hit", 0.5),                  # landing 1
        (starts[6] + 3.2, "hit", 0.5),                  # landing 2
        (starts[7], "bass_drop", 0.42),                 # payoff
        (total - 0.55, "crescendo", 0.5),               # end resolve
    ]
    for at, kind, gain in hits:
        add_at(bed, render_sfx(kind, SR, seed=42), at, gain, SR)
    bed = limiter(bed, 0.95)
    peak = max(abs(v) for v in bed) or 1.0
    if peak > 0.9:
        bed = [v * (0.9 / peak) for v in bed]
    # HARD length law: the bed can never outrun the video (the last SFX
    # tail was adding 0.65s of black-tail - L13 drift 1.3s, fixed here)
    n_samples = int(total * SR)
    bed = (bed + [0.0] * n_samples)[:n_samples]
    wav = OUT / "demo11_bed.wav"
    write_wav(wav, bed, SR)

    # ---------------- v6 captions + final mix ----------------
    scenes: list[tuple[float, float, str]] = []
    for k, (st, d) in enumerate(zip(starts, durs)):
        cap = (KEYS + [("", "", MOTION_CAPTION)] + PAYOFF)[k][2]
        scenes.append((round(st, 2), round(min(st + d - 0.05, total - 0.2), 2),
                       cap))
    ass = OUT / "v6.ass"
    ass.write_text(v6_ass(scenes, dur_s=total, karaoke=True,
                          progress=True), encoding="utf-8")

    full = OUT / "DEMO11_FULL.mp4"
    esc = str(ass.resolve()).replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")
    vf = f"scale={W}:{H},subtitles={esc}"
    run([ff, "-y", "-hide_banner", "-loglevel", "error",
         "-i", str(silent), "-i", str(wav),
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
         "-pix_fmt", "yuv420p", "-vf", vf, "-r", str(FPS),
         "-c:a", "aac", "-b:a", "160k", "-ar", "48000",
         "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-shortest",
         "-movflags", "+faststart", str(full)], "final burn+mix")

    # ---------------- phone version (baseline 720p max-compat) -----------
    phone = OUT / "DEMO11_PHONE.mp4"
    run([ff, "-y", "-hide_banner", "-loglevel", "error", "-i", str(full),
         "-vf", "scale=720:1280:flags=lanczos,fps=20",
         "-c:v", "libx264", "-profile:v", "baseline", "-level", "3.1",
         "-preset", "veryfast", "-crf", "23", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "128k", "-ac", "2", "-ar", "44100",
         "-movflags", "+faststart", str(phone)], "phone transcode")

    # ---------------- gif + sheets ----------------
    gif = OUT / "DEMO11_PREVIEW.gif"
    palette = SEGD / "pal.png"
    run([ff, "-y", "-hide_banner", "-loglevel", "error", "-i", str(phone),
         "-vf", "fps=10,scale=420:-1:flags=lanczos,palettegen=stats_mode=diff",
         str(palette)], "gif palette")
    run([ff, "-y", "-hide_banner", "-loglevel", "error", "-i", str(phone),
         "-i", str(palette), "-lavfi",
         "fps=10,scale=420:-1:flags=lanczos[x];[x][1:v]paletteuse=dither=bayer",
         "-loop", "0", str(gif)], "gif")

    from PIL import Image
    frames_png = sorted((SEGD / "motion_frames").glob("art_*.png"))
    def sheet(times: list[float], name: str, cols: int = 6) -> Path:
        ims = []
        for t in times:
            f = SEGD / f"grab_{int(t * 100):04d}.png"
            run([ff, "-y", "-hide_banner", "-loglevel", "error",
                 "-ss", f"{t:.2f}", "-i", str(full), "-frames:v", "1",
                 str(f)], f"grab {t}")
            ims.append(Image.open(f).resize((240, 427), Image.LANCZOS))
        rows = (len(ims) + cols - 1) // cols
        sh = Image.new("RGB", (240 * cols + 8 * (cols - 1),
                               427 * rows + 8 * (rows - 1)), (28, 28, 34))
        for i, im in enumerate(ims):
            sh.paste(im, ((i % cols) * 248, (i // cols) * 435))
        p = OUT / name
        sh.save(p)
        return p

    sheet_a = sheet([0.4, 1.25, 2.1, 2.95, 3.8, 4.65], "demo11_partA_sheet.png")
    sheet_b = sheet([5.6, 6.4, 7.2, 8.3, 9.4, 10.5], "demo11_partB_sheet.png")
    sheet_m = None
    if frames_png:
        picks = frames_png[::max(1, len(frames_png) // 6)][:6]
        ims = [Image.open(p).resize((240, 427), Image.LANCZOS) for p in picks]
        sh = Image.new("RGB", (240 * len(ims) + 8 * (len(ims) - 1), 427),
                       (28, 28, 34))
        for i, im in enumerate(ims):
            sh.paste(im, (i * 248, 0))
        sheet_m = OUT / "demo11_motion_sheet.png"
        sh.save(sheet_m)

    # ---------------- report ----------------
    lufs = measure_lufs(ff, str(full))
    report = {
        "topic": "THE MOON IS A HOLE (system demo, seed 42)",
        "segments": len(segs),
        "key_s": KEY_S, "xfade_s": d_eff, "fps": FPS,
        "motion": "jump x2 (FK one-shot, 1.6s each)",
        "want_s": round(total, 3), "full_s": round(probe_dur(full), 3),
        "phone_s": round(probe_dur(phone), 3),
        "drift_s": round(abs(probe_dur(full) - total), 3),
        "lufs": lufs,
        "vo": "TTS blocked this session (speech.platform.bing.com "
              "unreachable) - music bed + SFX, honest report",
        "files": {p.name: {"bytes": p.stat().st_size,
                           "sha256": sha256_of(p)}
                  for p in (full, phone, gif, sheet_a, sheet_b)
                  if p and p.is_file()},
    }
    if sheet_m:
        report["files"][sheet_m.name] = {"bytes": sheet_m.stat().st_size,
                                         "sha256": sha256_of(sheet_m)}
    (OUT / "demo11_report.json").write_text(json.dumps(report, indent=2),
                                            encoding="utf-8")
    (OUT / "index.html").write_text(
        "<!doctype html><meta name=viewport content='width=device-width,"
        "initial-scale=1'><title>DEMO11</title>"
        "<body style='margin:0;background:#0b0b10;color:#eee;font-family:"
        "system-ui'>"
        "<h3 style='padding:12px 16px'>DEMO11 - THE MOON IS A HOLE "
        "(full-system demo)</h3>"
        "<video src='DEMO11_PHONE.mp4' controls playsinline "
        "style='width:100%;max-height:78vh;display:block'></video>"
        "<p style='padding:8px 16px;font-size:14px;opacity:.8'>"
        "1080x1920 master: DEMO11_FULL.mp4 &middot; phone file: "
        "DEMO11_PHONE.mp4 &middot; sheet A/B + motion sheet below</p>"
        "<img src='demo11_partA_sheet.png' style='width:100%'>"
        "<img src='demo11_partB_sheet.png' style='width:100%'>"
        "<img src='demo11_motion_sheet.png' style='width:100%'>"
        "</body>", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
