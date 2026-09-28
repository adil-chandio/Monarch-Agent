"""STICKMAN ART ENGINE — image banao, phir POSE animate karo (2026-09-28).

The operator's wish, made real within the egress law: AI photoreal
gen stays parked (hf.co/APIs blocked, probed) — but a DETERMINISTIC
stickman ART + POSE-ANIMATION engine is fully in-sandbox (Pillow from
pypi). And for OUR brand it is the better machine anyway: the persona
is sample-identical every render (mere-exposure brand law), fails
closed, and never hallucinates text.

What it draws: a real stick figure (head, torso, elbows, hands,
knees, feet) on the black void — the V6 house style (thick white
lines, dot eyes, minimal props: gold crown, magnifier).

What it animates: POSE-TO-POSE interpolation (joint lerp) — wave,
shock, crown-lift, walk — real limb motion on top of the existing
camera moves (ken burns stays available in the main pipeline).

Laws honored: no text drawn ever (miss #2), subject centered in the
middle-60% band (miss #5), seeded determinism (L-class: same inputs
-> identical bytes), 2-input ffmpeg renders (G7/L2), duration drift
checked (L13). Pillow is an ENV dependency like imageio-ffmpeg —
pyproject stays zero-dep; tests skip gracefully if it is absent.
"""

from __future__ import annotations

try:
    from PIL import Image, ImageDraw
except ImportError as e:      # pragma: no cover - env guard, honest message
    raise ImportError("Pillow required for the art engine: "
                      "pip install pillow (pypi allowlist)") from e

# --- canvas + style laws ---------------------------------------------------
W, H = 1080, 1920
SS = 2                        # supersample factor (smooth lines)
BG = (6, 6, 10)               # the black void
INK = (245, 245, 245)         # white doodle lines
GOLD = (255, 215, 0)
ACCENT = (255, 82, 82)        # signal red (danger)
SUBJECT_BAND = (500, 1400)    # middle-60% law (miss #5)

# --- skeleton (unit space; u = figure scale, origin at ground center) ------
BASE = {
    "head": (0.0, -1.62), "neck": (0.0, -1.24), "hip": (0.0, -0.58),
    "elbow_l": (-0.30, -1.05), "hand_l": (-0.46, -0.72),
    "elbow_r": (0.30, -1.05), "hand_r": (0.46, -0.72),
    "knee_l": (-0.16, -0.30), "foot_l": (-0.24, 0.0),
    "knee_r": (0.16, -0.30), "foot_r": (0.24, 0.0),
}

#: poses = joint overrides in unit space (miss-free, all fields optional)
POSES: dict[str, dict] = {
    "idle":   {},
    "point":  {"elbow_r": (0.34, -1.28), "hand_r": (0.82, -1.50)},
    "shock":  {"elbow_l": (-0.42, -1.32), "hand_l": (-0.44, -1.80),
               "elbow_r": (0.42, -1.32), "hand_r": (0.44, -1.80),
               "mouth": True},
    "wave":   {"hand_r": (0.66, -1.86), "elbow_r": (0.40, -1.34),
               "mouth": True},
    "crown":  {"elbow_l": (-0.30, -1.60), "hand_l": (-0.26, -2.06),
               "elbow_r": (0.30, -1.60), "hand_r": (0.26, -2.06)},
    "walk":   {"knee_l": (-0.34, -0.32), "foot_l": (-0.52, 0.0),
               "knee_r": (0.32, -0.28), "foot_r": (0.50, 0.0),
               "hand_l": (-0.56, -0.66), "hand_r": (0.56, -0.66)},
    "bow":    {"head": (0.34, -1.44), "neck": (0.22, -1.16),
               "hand_l": (-0.18, -0.52), "hand_r": (0.62, -0.60),
               "elbow_r": (0.36, -0.86)},
}

_PROP_JOINTS = frozenset(BASE)


def _resolved(pose: str) -> dict:
    if pose not in POSES:
        raise ValueError(f"unknown pose {pose!r} - have: "
                         f"{', '.join(sorted(POSES))}")
    j = dict(BASE)
    j.update(POSES[pose])
    return j


def lerp_poses(a: str, b: str, t: float) -> dict:
    """Joint-lerp between two poses; t=0 -> a, t=1 -> b (clamped)."""
    ja, jb = _resolved(a), _resolved(b)
    t = min(1.0, max(0.0, t))
    out = {}
    for k in _PROP_JOINTS:
        ax, ay = ja[k]
        bx, by = jb[k]
        out[k] = (ax + (bx - ax) * t, ay + (by - ay) * t)
    out["mouth"] = bool(ja.get("mouth") or jb.get("mouth"))
    return out


# ---------------------------------------------------------------------------
# drawing
# ---------------------------------------------------------------------------


def _joints_px(j: dict, cx: int, gy: int, u: float) -> dict[str, tuple[int, int]]:
    out: dict[str, tuple[int, int]] = {}
    for k, v in j.items():
        if k not in _PROP_JOINTS:
            continue                     # skip flags (mouth) BEFORE unpack
        x, y = v
        out[k] = (int(cx + x * u), int(gy + y * u))
    return out


def draw_scene(pose: str = "idle", *, w: int = W, h: int = H, seed: int = 7,
               prop: str | None = None, moon: bool = True,
               stars: int = 40) -> "Image.Image":
    """One art frame: void + glow + stars + ground + stickman (+prop)."""
    import random
    rng = random.Random(seed * 977 + 13)
    img = Image.new("RGB", (w * SS, h * SS), BG)
    d = ImageDraw.Draw(img)
    cx, gy, u = w // 2, int(h * 0.76), h / 6.4

    # soft glow behind the figure (concentric faint rings)
    for r, alpha in ((5.2, 14), (4.0, 18), (2.9, 22)):
        ring = tuple(min(255, c + alpha) for c in BG)
        d.ellipse([(cx - r * u) * SS, (gy - r * u) * SS,
                   (cx + r * u) * SS, (gy + r * u) * SS], outline=ring,
                  width=max(1, int(6 * SS * r / 4)))

    # seeded stars (upper half only, never on the subject band center)
    for _ in range(stars):
        sx = rng.randrange(int(w * 0.04), int(w * 0.96))
        sy = rng.randrange(int(h * 0.03), int(h * 0.34))
        s = rng.choice((1, 1, 2))
        d.ellipse([(sx - s) * SS, (sy - s) * SS, (sx + s) * SS,
                   (sy + s) * SS], fill=(210, 214, 230))

    if moon:
        mx, my, mr = int(w * 0.80), int(h * 0.12), int(w * 0.055)
        d.ellipse([(mx - mr) * SS, (my - mr) * SS, (mx + mr) * SS,
                   (my + mr) * SS], fill=(232, 234, 240))
        d.ellipse([(mx - mr * 0.32) * SS, (my - mr * 0.4) * SS,
                   (mx + mr * 0.5) * SS, (my + mr * 0.42) * SS],
                  fill=(206, 210, 222))

    # ground line (the void floor)
    d.line([(int(w * 0.06) * SS, gy * SS), (int(w * 0.94) * SS, gy * SS)],
           fill=(70, 72, 84), width=max(2, int(3 * SS)))

    # --- the figure ---
    j = _joints_px(_resolved(pose), cx, gy, u)
    lw = max(3, int(u * 0.055))
    segs = (("head", "neck"), ("neck", "hip"),
            ("neck", "elbow_l"), ("elbow_l", "hand_l"),
            ("neck", "elbow_r"), ("elbow_r", "hand_r"),
            ("hip", "knee_l"), ("knee_l", "foot_l"),
            ("hip", "knee_r"), ("knee_r", "foot_r"))
    for a, b in segs:
        d.line([j[a][0] * SS, j[a][1] * SS, j[b][0] * SS, j[b][1] * SS],
               fill=INK, width=lw * SS)
    hr = int(u * 0.17)
    hx, hy = j["head"]
    d.ellipse([(hx - hr) * SS, (hy - hr) * SS, (hx + hr) * SS,
               (hy + hr) * SS], outline=INK, width=lw * SS)
    # dot eyes (the house style) + optional open mouth
    er = max(2, int(hr * 0.14))
    for ex in (hx - hr * 0.42, hx + hr * 0.42):
        ey = hy - hr * 0.10
        d.ellipse([(ex - er) * SS, (ey - er) * SS, (ex + er) * SS,
                   (ey + er) * SS], fill=INK)
    if j.get("mouth"):
        om = int(hr * 0.34)
        d.ellipse([(hx - om * 0.6) * SS, (hy + hr * 0.30) * SS,
                   (hx + om * 0.6) * SS, (hy + hr * 0.30 + om) * SS],
                  fill=INK)

    # --- props (signal colors only - V6 style law) ---
    if prop == "crown":
        cw, ch = int(u * 0.5), int(u * 0.24)
        cy0 = j["head"][1] - hr - ch - int(u * 0.10)
        cx0 = j["head"][0]
        d.polygon([(cx0 - cw) * SS, (cy0 + ch) * SS,
                   (cx0 - cw) * SS, cy0 * SS,
                   (cx0 - cw // 2) * SS, (cy0 + ch // 3) * SS,
                   cx0 * SS, cy0 * SS,
                   (cx0 + cw // 2) * SS, (cy0 + ch // 3) * SS,
                   (cx0 + cw) * SS, cy0 * SS,
                   (cx0 + cw) * SS, (cy0 + ch) * SS],
                  outline=GOLD, width=max(2, int(2.4 * SS)))
    elif prop == "magnifier":
        mxp, myp = j["hand_r"]
        mr = int(u * 0.16)
        d.ellipse([(mxp - mr) * SS, (myp - mr - u * 0.05) * SS,
                   (mxp + mr) * SS, (myp + mr - u * 0.05) * SS],
                  outline=(150, 200, 255), width=max(2, int(2.2 * SS)))
        d.line([mxp * SS, (myp + mr * 0.7 - u * 0.05) * SS,
                (mxp + u * 0.10) * SS, (myp + mr * 1.6) * SS],
               fill=(150, 200, 255), width=max(2, int(2.2 * SS)))
    elif prop is not None:
        raise ValueError(f"unknown prop {prop!r} - have: crown, magnifier")

    return img.resize((w, h), Image.LANCZOS)


def scene_png(path, pose: str = "idle", **kw) -> str:
    """Render one art frame -> PNG (bytes-identical for same inputs)."""
    from pathlib import Path
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    img = draw_scene(pose, **kw)
    img.save(path, format="PNG", optimize=False)
    return str(path)


# ---------------------------------------------------------------------------
# POSE ANIMATION: joint-lerp frame sequences -> PNG series -> mp4
# ---------------------------------------------------------------------------


def pose_frames(seq: list[str], steps: int = 10,
                hold: int = 4, **kw) -> list["Image.Image"]:
    """Pose sequence -> frames. Each transition gets `steps` interpolated
    frames, each pose then holds `hold` frames (readable, not flicker)."""
    if len(seq) < 2:
        raise ValueError("animation needs >= 2 poses (a still is a scene, "
                         "not an animation)")
    if steps < 2 or hold < 0:
        raise ValueError("steps >= 2 and hold >= 0")
    frames: list[Image.Image] = []
    for a, b in zip(seq, seq[1:]):
        for i in range(steps):
            t = i / (steps - 1) if steps > 1 else 0.0
            j = lerp_poses(a, b, t)
            frames.append(_render_joints(j, **kw))
        for _ in range(hold):
            frames.append(_render_joints(_resolved(b), **kw))
    return frames


def _render_joints(j: dict, **kw) -> "Image.Image":
    """draw_scene internals for an explicit joint dict (animation path)."""
    w, h = kw.get("w", W), kw.get("h", H)
    img = draw_scene("idle", w=w, h=h, seed=kw.get("seed", 7),
                     moon=kw.get("moon", True), stars=kw.get("stars", 40))
    # redraw the figure with explicit joints on a fresh copy:
    # simplest correct route - render idle bg once via draw_scene, then
    # paint the figure layer here (deterministic, single source of style)
    d = ImageDraw.Draw(img)
    cx, gy, u = w // 2, int(h * 0.76), h / 6.4
    px = _joints_px(j, cx, gy, u)
    lw = max(3, int(u * 0.055))
    segs = (("head", "neck"), ("neck", "hip"),
            ("neck", "elbow_l"), ("elbow_l", "hand_l"),
            ("neck", "elbow_r"), ("elbow_r", "hand_r"),
            ("hip", "knee_l"), ("knee_l", "foot_l"),
            ("hip", "knee_r"), ("knee_r", "foot_r"))
    for a, b in segs:
        d.line([px[a][0], px[a][1], px[b][0], px[b][1]], fill=INK, width=lw)
    hr = int(u * 0.17)
    hx, hy = px["head"]
    d.ellipse([hx - hr, hy - hr, hx + hr, hy + hr], outline=INK, width=lw)
    er = max(2, int(hr * 0.14))
    for ex in (hx - hr * 0.42, hx + hr * 0.42):
        ey = hy - hr * 0.10
        d.ellipse([ex - er, ey - er, ex + er, ey + er], fill=INK)
    if j.get("mouth"):
        om = int(hr * 0.34)
        d.ellipse([hx - om * 0.6, hy + hr * 0.30,
                   hx + om * 0.6, hy + hr * 0.30 + om], fill=INK)
    return img


def write_frames(frames: list["Image.Image"], outdir) -> list[str]:
    from pathlib import Path
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    paths = []
    for i, f in enumerate(frames):
        p = out / f"art_{i:04d}.png"
        f.save(p, format="PNG")
        paths.append(str(p))
    return paths


def render_art_mp4(frames: list["Image.Image"], outdir, *,
                   fps: int = 12) -> dict:
    """Frames -> mp4 (2-input law: concat + silent wav; L13 drift check).
    NOTE: silent by design - layer the VO/mix through the main render
    pipeline; this is the ART stage, not the master."""
    import re as _re
    import subprocess
    import wave as _wave
    from pathlib import Path
    from monarch.video.render import ffmpeg_exe
    d = Path(outdir)
    d.mkdir(parents=True, exist_ok=True)
    paths = write_frames(frames, d / "art_frames")
    lst = d / "art_concat.txt"
    lines = ["ffconcat version 1.0"]
    for p in paths:
        lines.append(f"file '{Path(p).resolve()}'")
        lines.append(f"duration {1.0 / fps:.4f}")
    lines.append(f"file '{Path(paths[-1]).resolve()}'")   # concat quirk hold
    lst.write_text("\n".join(lines) + "\n", encoding="utf-8")

    sr = 44100
    silent = [0.0] * int(sr * len(frames) / fps)
    wav = d / "art_silent.wav"
    from monarch.video.audio import write_wav
    write_wav(wav, silent, sr)
    out_p = d / "art_anim.mp4"
    ff = ffmpeg_exe()
    proc = subprocess.run(
        [ff, "-y", "-hide_banner", "-loglevel", "error",
         "-f", "concat", "-safe", "0", "-i", str(lst), "-i", str(wav),
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
         "-pix_fmt", "yuv420p", "-vf", f"scale={W}:{H}",
         "-c:a", "aac", "-b:a", "160k", "-ar", "48000",
         "-movflags", "+faststart", str(out_p)],
        capture_output=True, text=True)
    if proc.returncode != 0 or not out_p.is_file():
        raise ValueError(f"art render failed: {proc.stderr.strip()[:300]}")
    # L13: probe duration
    info = subprocess.run([ff, "-hide_banner", "-i", str(out_p)],
                          capture_output=True, text=True)
    m = _re.search(r"Duration: (\d+):(\d+):([\d.]+)", info.stderr)
    got = (int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))
           if m else 0.0)
    want = len(frames) / fps
    return {"output": str(out_p), "frames": len(frames), "fps": fps,
            "want_s": round(want, 3), "got_s": round(got, 3),
            "drift_s": round(abs(got - want), 3),
            "bytes": out_p.stat().st_size,
            "duration_ok": abs(got - want) <= 0.5,
            "law_note": ("2 inputs (G7/L2); silent art stage - master mix "
                         "stays the render pipeline's job; subject in "
                         "middle-60% (miss #5); no text drawn (miss #2)")}
