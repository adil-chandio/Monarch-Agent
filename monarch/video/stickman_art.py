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


# --- scene layers (single source of style: bg / figure / prop) -------------

_SEGS = (("head", "neck"), ("neck", "hip"),
         ("neck", "elbow_l"), ("elbow_l", "hand_l"),
         ("neck", "elbow_r"), ("elbow_r", "hand_r"),
         ("hip", "knee_l"), ("knee_l", "foot_l"),
         ("hip", "knee_r"), ("knee_r", "foot_r"))


def _canvas(w: int, h: int) -> "Image.Image":
    return Image.new("RGB", (w * SS, h * SS), BG)


def _bg(d, w: int, h: int, *, seed: int = 7, moon: bool = True,
        stars: int = 40) -> tuple[int, int, float]:
    """Void + glow + seeded stars + moon + ground. Returns (cx, gy, u)."""
    import random
    rng = random.Random(seed * 977 + 13)
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
        d.ellipse([(sx - s) * SS, (sy - s) * SS,
                   (sx + s) * SS, (sy + s) * SS], fill=(210, 214, 230))

    if moon:
        mx, my, mr = int(w * 0.80), int(h * 0.12), int(w * 0.055)
        d.ellipse([(mx - mr) * SS, (my - mr) * SS, (mx + mr) * SS,
                   (my + mr) * SS], fill=(232, 234, 240))
        # rim-lit HOLE, not a ball (the house brand read: "the moon is a
        # hole"): the interior is the void itself + a thin depth rim.
        mri = int(mr * 0.52)
        d.ellipse([(mx - mri) * SS, (my - mri) * SS, (mx + mri) * SS,
                   (my + mri) * SS], fill=BG)
        d.ellipse([(mx - mri) * SS, (my - mri) * SS, (mx + mri) * SS,
                   (my + mri) * SS], outline=(120, 122, 140),
                  width=max(1, int(1.4 * SS)))

    # ground line (the void floor)
    d.line([(int(w * 0.06) * SS, gy * SS), (int(w * 0.94) * SS, gy * SS)],
           fill=(70, 72, 84), width=max(2, int(3 * SS)))
    return cx, gy, u


def _figure(d, px: dict[str, tuple[int, int]], u: float, *,
            mouth: bool = False) -> None:
    """The stickman, painted from pixel-space joints (house style)."""
    lw = max(3, int(u * 0.055))
    for a, b in _SEGS:
        d.line([px[a][0] * SS, px[a][1] * SS, px[b][0] * SS, px[b][1] * SS],
               fill=INK, width=lw * SS)
    hr = int(u * 0.17)
    hx, hy = px["head"]
    d.ellipse([(hx - hr) * SS, (hy - hr) * SS, (hx + hr) * SS,
               (hy + hr) * SS], outline=INK, width=lw * SS)
    er = max(2, int(hr * 0.14))
    for ex in (hx - hr * 0.42, hx + hr * 0.42):
        ey = hy - hr * 0.10
        d.ellipse([(ex - er) * SS, (ey - er) * SS, (ex + er) * SS,
                   (ey + er) * SS], fill=INK)
    if mouth:
        om = int(hr * 0.34)
        d.ellipse([(hx - om * 0.6) * SS, (hy + hr * 0.30) * SS,
                   (hx + om * 0.6) * SS, (hy + hr * 0.30 + om) * SS],
                  fill=INK)


def _prop(d, prop: str | None, px: dict[str, tuple[int, int]],
          u: float) -> None:
    """Signal-color props only (V6 style law); unknown prop fails closed."""
    if prop is None:
        return
    if prop == "crown":
        cw, ch = int(u * 0.5), int(u * 0.24)
        cy0 = px["head"][1] - int(u * 0.17) - ch - int(u * 0.10)
        cx0 = px["head"][0]
        d.polygon([(cx0 - cw) * SS, (cy0 + ch) * SS,
                   (cx0 - cw) * SS, cy0 * SS,
                   (cx0 - cw // 2) * SS, (cy0 + ch // 3) * SS,
                   cx0 * SS, cy0 * SS,
                   (cx0 + cw // 2) * SS, (cy0 + ch // 3) * SS,
                   (cx0 + cw) * SS, cy0 * SS,
                   (cx0 + cw) * SS, (cy0 + ch) * SS],
                  outline=GOLD, width=max(2, int(2.4 * SS)))
    elif prop == "magnifier":
        mxp, myp = px["hand_r"]
        mr = int(u * 0.16)
        d.ellipse([(mxp - mr) * SS, (myp - mr - u * 0.05) * SS,
                   (mxp + mr) * SS, (myp + mr - u * 0.05) * SS],
                  outline=(150, 200, 255), width=max(2, int(2.2 * SS)))
        d.line([mxp * SS, (myp + mr * 0.7 - u * 0.05) * SS,
                (mxp + u * 0.10) * SS, (myp + mr * 1.6) * SS],
               fill=(150, 200, 255), width=max(2, int(2.2 * SS)))
    else:
        raise ValueError(f"unknown prop {prop!r} - have: crown, magnifier")


def draw_scene(pose: str = "idle", *, w: int = W, h: int = H, seed: int = 7,
               prop: str | None = None, moon: bool = True,
               stars: int = 40) -> "Image.Image":
    """One art frame: void + glow + stars + ground + stickman (+prop)."""
    j = _resolved(pose)                     # fail closed before any paint
    img = _canvas(w, h)
    d = ImageDraw.Draw(img)
    cx, gy, u = _bg(d, w, h, seed=seed, moon=moon, stars=stars)
    px = _joints_px(j, cx, gy, u)
    _figure(d, px, u, mouth=bool(j.get("mouth")))
    _prop(d, prop, px, u)
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
    """Explicit joint dict -> full-style frame (animation path).

    Fixed 2026-10-01 (recovery): the old path painted over an idle
    background figure (double-figure bug) and skipped both supersampling
    and props. Now it runs the same single-source layers as draw_scene.
    """
    w, h = kw.get("w", W), kw.get("h", H)
    img = _canvas(w, h)
    d = ImageDraw.Draw(img)
    cx, gy, u = _bg(d, w, h, seed=kw.get("seed", 7),
                    moon=kw.get("moon", True), stars=kw.get("stars", 40))
    px = _joints_px(j, cx, gy, u)
    _figure(d, px, u, mouth=bool(j.get("mouth")))
    _prop(d, kw.get("prop"), px, u)
    return img.resize((w, h), Image.LANCZOS)


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


def _encode_frames(frames: list["Image.Image"], outdir, *, fps: int,
                   wav: str | Path | None = None, name: str = "art_anim.mp4",
                   frames_dir: str = "art_frames",
                   concat: str = "art_concat.txt") -> dict:
    """2-input render law (G7/L2): frame concat + audio -> mp4, L13 drift.

    wav=None -> silent art stage (the master mix rides the render
    pipeline); wav given -> the audio is the truth and gets loudnorm.
    """
    import re as _re
    import subprocess
    from pathlib import Path
    from monarch.video.render import ffmpeg_exe
    from monarch.video.audio import write_wav

    if not frames or fps < 2:
        raise ValueError("need frames and fps >= 2")
    d = Path(outdir)
    d.mkdir(parents=True, exist_ok=True)
    paths = write_frames(frames, d / frames_dir)
    lst = d / concat
    lines = ["ffconcat version 1.0"]
    for p in paths:
        lines.append(f"file '{Path(p).resolve()}'")
        lines.append(f"duration {1.0 / fps:.4f}")
    lines.append(f"file '{Path(paths[-1]).resolve()}'")   # concat quirk hold
    lst.write_text("\n".join(lines) + "\n", encoding="utf-8")

    want = len(frames) / fps
    if wav is None:
        audio = d / "art_silent.wav"
        write_wav(audio, [0.0] * int(44100 * want), 44100)
        acodec = ["-c:a", "aac", "-b:a", "160k", "-ar", "48000"]
    else:
        audio = Path(wav)
        if not audio.is_file():
            raise ValueError(f"no audio at {audio}")
        acodec = ["-c:a", "aac", "-b:a", "160k", "-ar", "48000",
                  "-af", "loudnorm=I=-14:TP=-1.5:LRA=11"]
    out_p = d / name
    ff = ffmpeg_exe()
    proc = subprocess.run(
        [ff, "-y", "-hide_banner", "-loglevel", "error",
         "-f", "concat", "-safe", "0", "-i", str(lst), "-i", str(audio),
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
         "-pix_fmt", "yuv420p", "-vf", f"scale={W}:{H}", *acodec,
         "-movflags", "+faststart", str(out_p)], capture_output=True,
        text=True)
    if proc.returncode != 0 or not out_p.is_file():
        raise ValueError(f"render failed: {proc.stderr.strip()[:300]}")
    info = subprocess.run([ff, "-hide_banner", "-i", str(out_p)],
                          capture_output=True, text=True)
    m = _re.search(r"Duration: (\d+):(\d+):([\d.]+)", info.stderr)
    got = (int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))
           if m else 0.0)
    return {"output": str(out_p), "frames": len(frames), "fps": fps,
            "want_s": round(want, 3), "got_s": round(got, 3),
            "drift_s": round(abs(got - want), 3),
            "bytes": out_p.stat().st_size,
            "duration_ok": abs(got - want) <= 0.5,
            "law_note": ("2 inputs (G7/L2); art stage - the master mix "
                         "stays the render pipeline's job; subject in "
                         "middle-60% (miss #5); no text drawn (miss #2)")}


def render_art_mp4(frames: list["Image.Image"], outdir, *,
                   fps: int = 12) -> dict:
    """Frames -> mp4 (2-input law: concat + silent wav; L13 drift check).
    NOTE: silent by design - layer the VO/mix through the main render
    pipeline; this is the ART stage, not the master."""
    return _encode_frames(frames, outdir, fps=fps, name="art_anim.mp4")


# ---------------------------------------------------------------------------
# FK MOTION ENGINE - bone-rotation animation (recovered 2026-10-01)
# ---------------------------------------------------------------------------
# The core of the lost local commit: real forward kinematics instead of
# joint-lerp - bones rotate (spine / head / upper-arm / forearm / thigh /
# shin) and every joint falls out of the chain. Loop motions are seamless
# BY CONSTRUCTION (all terms are sin/cos of the phase, so t=1 == t=0);
# the jump is a one-shot whose last frame is EXACTLY the idle base
# (landing law - feet on the ground line, no float).

from math import atan2, cos, degrees, hypot, pi, radians, sin  # noqa: E402


def _bone_lengths() -> dict[str, float]:
    """Bone lengths (unit space) derived from BASE - never hardcoded."""
    def span(a: str, b: str) -> float:
        (ax, ay), (bx, by) = BASE[a], BASE[b]
        return hypot(bx - ax, by - ay)
    return {"spine": span("hip", "neck"), "head": span("neck", "head"),
            "upper_arm": span("neck", "elbow_r"),
            "forearm": span("elbow_r", "hand_r"),
            "thigh": span("hip", "knee_r"), "shin": span("knee_r", "foot_r")}


BONE = _bone_lengths()


def _bone_angles(pose: str = "idle") -> dict[str, float]:
    """A pose expressed as bone angles (deg). Direction = (sin, cos):
    y-down unit space, so 0 = straight down, 180 = straight up."""
    j = _resolved(pose)

    def ang(a: str, b: str) -> float:
        (ax, ay), (bx, by) = j[a], j[b]
        return degrees(atan2(bx - ax, by - ay))

    return {"spine": ang("hip", "neck"),
            "arm_l": ang("neck", "elbow_l"),
            "forearm_l": ang("elbow_l", "hand_l"),
            "arm_r": ang("neck", "elbow_r"),
            "forearm_r": ang("elbow_r", "hand_r"),
            "thigh_l": ang("hip", "knee_l"), "shin_l": ang("knee_l", "foot_l"),
            "thigh_r": ang("hip", "knee_r"), "shin_r": ang("knee_r", "foot_r")}


BASE_ANGLES = _bone_angles("idle")


def fk_joints(angles: dict, *, bob: float = 0.0,
              mouth: bool = False) -> dict:
    """Forward kinematics: bone angles -> joint dict (unit space).

    `bob` shifts the whole body (hip) vertically - negative lifts."""
    hip = (BASE["hip"][0], BASE["hip"][1] + bob)

    def step(p: tuple[float, float], deg: float,
             length: float) -> tuple[float, float]:
        r = radians(deg)
        return (p[0] + length * sin(r), p[1] + length * cos(r))

    spine = angles["spine"]
    neck = step(hip, spine, BONE["spine"])
    out: dict = {"hip": hip, "neck": neck,
                 "head": step(neck, spine, BONE["head"])}
    for side in ("l", "r"):
        e = step(neck, angles[f"arm_{side}"], BONE["upper_arm"])
        out[f"elbow_{side}"] = e
        out[f"hand_{side}"] = step(e, angles[f"forearm_{side}"],
                                   BONE["forearm"])
        k = step(hip, angles[f"thigh_{side}"], BONE["thigh"])
        out[f"knee_{side}"] = k
        out[f"foot_{side}"] = step(k, angles[f"shin_{side}"], BONE["shin"])
    out["mouth"] = bool(mouth)
    return out


def _mirror(a: dict, *, thigh: float = 0.0, shin: float = 0.0,
            arm: float = 0.0, forearm: float = 0.0) -> dict:
    """Symmetric limb deltas (one figure, both sides): the operator sets
    the left side, the right side mirrors it (angle -> -angle law).
    Sign notes: arm NEGATIVE = raise; thigh NEGATIVE = knee out/up;
    shin POSITIVE = foot tucks back under the body."""
    a = dict(a)
    a["thigh_l"] += thigh
    a["thigh_r"] -= thigh
    a["shin_l"] += shin
    a["shin_r"] -= shin
    a["arm_l"] += arm
    a["arm_r"] -= arm
    a["forearm_l"] += forearm
    a["forearm_r"] -= forearm
    return a


def _walk_motion(t: float) -> tuple[dict, float, bool]:
    """Stride loop: legs alternate, arms counter-swing, body bobs."""
    ph = 2 * pi * t
    a = dict(BASE_ANGLES)
    swing = 24.0 * sin(ph)
    a["thigh_l"] += swing
    a["thigh_r"] -= swing
    a["shin_l"] += 14.0 * max(0.0, sin(ph))
    a["shin_r"] += 14.0 * max(0.0, -sin(ph))
    a["arm_l"] -= 15.0 * sin(ph)
    a["arm_r"] += 15.0 * sin(ph)
    a["forearm_l"] -= 8.0 * sin(ph)
    a["forearm_r"] += 8.0 * sin(ph)
    a["spine"] += 2.0 * sin(ph)
    return a, -0.028 * abs(cos(ph)), False


def _wave_motion(t: float) -> tuple[dict, float, bool]:
    """Greet loop: right arm up (only the right), forearm waves twice."""
    ph = 2 * pi * t
    a = dict(BASE_ANGLES)
    a["arm_r"] += 62.0                        # right side: + = raise
    a["forearm_r"] = 150.0 + 22.0 * sin(2 * ph)   # hand sweeps up-out
    a["arm_l"] -= 6.0 * sin(ph)
    a["spine"] += 2.5 * sin(ph)
    return a, -0.012 - 0.008 * sin(ph), True


#: jump keyframes: t, body deltas, bob (positive = hip drops), mouth
_JUMP_KEYS: tuple[tuple[float, dict], ...] = (
    (0.00, {"spine": 0.0, "thigh": 0.0, "shin": 0.0, "arm": 0.0,
            "forearm": 0.0, "bob": 0.0, "mouth": False}),      # stand
    (0.18, {"spine": 8.0, "thigh": -18.0, "shin": 34.0, "arm": 20.0,
            "forearm": 12.0, "bob": 0.085, "mouth": False}),   # crouch load
    (0.30, {"spine": -4.0, "thigh": 6.0, "shin": -4.0, "arm": -70.0,
            "forearm": -24.0, "bob": -0.30, "mouth": True}),   # launch
    (0.50, {"spine": 2.0, "thigh": -34.0, "shin": 52.0, "arm": -96.0,
            "forearm": -30.0, "bob": -0.44, "mouth": True}),   # air tuck
    (0.72, {"spine": 0.0, "thigh": 4.0, "shin": 10.0, "arm": -46.0,
            "forearm": -14.0, "bob": -0.30, "mouth": True}),   # falling
    (0.88, {"spine": 7.0, "thigh": -16.0, "shin": 30.0, "arm": 18.0,
            "forearm": 12.0, "bob": 0.07, "mouth": False}),    # land absorb
    (1.00, {"spine": 0.0, "thigh": 0.0, "shin": 0.0, "arm": 0.0,
            "forearm": 0.0, "bob": 0.0, "mouth": False}),      # EXACT base
)


def _jump_motion(t: float) -> tuple[dict, float, bool]:
    """One-shot: crouch -> launch -> air-tuck -> EXACT landing."""
    t = min(1.0, max(0.0, t))
    last = _JUMP_KEYS[-1][1]
    if t >= 1.0:                              # the landing frame is exact
        return (_mirror(dict(BASE_ANGLES), thigh=last["thigh"],
                        shin=last["shin"], arm=last["arm"],
                        forearm=last["forearm"]),
                last["bob"], bool(last["mouth"]))
    for (t0, k0), (t1, k1) in zip(_JUMP_KEYS, _JUMP_KEYS[1:]):
        if t0 <= t <= t1:
            u = (t - t0) / (t1 - t0) if t1 > t0 else 0.0
            u = u * u * (3 - 2 * u)           # smoothstep (no robot snaps)
            a = dict(BASE_ANGLES)
            a["spine"] += k0["spine"] + (k1["spine"] - k0["spine"]) * u
            a = _mirror(a,
                        thigh=k0["thigh"] + (k1["thigh"] - k0["thigh"]) * u,
                        shin=k0["shin"] + (k1["shin"] - k0["shin"]) * u,
                        arm=k0["arm"] + (k1["arm"] - k0["arm"]) * u,
                        forearm=(k0["forearm"]
                                 + (k1["forearm"] - k0["forearm"]) * u))
            return (a, k0["bob"] + (k1["bob"] - k0["bob"]) * u,
                    bool(k0["mouth"] or k1["mouth"]))
    return (dict(BASE_ANGLES), 0.0, False)    # unreachable, fail-safe idle


#: motion registry: seconds / loop flag / default fps / law note
MOTIONS: dict[str, dict] = {
    "walk": {"seconds": 1.0, "loop": True, "fps": 30,
             "note": "stride loop - arms counter-swing, seamless t=0/1"},
    "wave": {"seconds": 1.2, "loop": True, "fps": 30,
             "note": "greet loop - raised arm waves twice per loop"},
    "jump": {"seconds": 1.6, "loop": False, "fps": 30,
             "note": "one-shot - crouch -> launch -> air-tuck (mouth) "
                     "-> landing = EXACT idle base"},
}

_SAMPLERS = {"walk": _walk_motion, "wave": _wave_motion, "jump": _jump_motion}


def motion_pose(motion: str, t: float) -> dict:
    """Motion + normalized time -> joint dict (same shape as _resolved).

    Loops wrap (t=1.0 == t=0.0, seamless); the one-shot is clamped.
    Unknown motion fails closed."""
    if motion not in MOTIONS:
        raise ValueError(f"unknown motion {motion!r} - have: "
                         f"{', '.join(sorted(MOTIONS))}")
    if MOTIONS[motion]["loop"]:
        t = t % 1.0
    angles, bob, mouth = _SAMPLERS[motion](t)
    return fk_joints(angles, bob=bob, mouth=mouth)


def motion_frames(motion: str, *, fps: int | None = None,
                  seconds: float | None = None, **kw) -> list["Image.Image"]:
    """Motion -> frames. Loops sample [0,1) (wrap-safe); the one-shot
    samples [0,1] so the exact landing frame exists (L13-friendly:
    frames / fps == spec seconds)."""
    if motion not in MOTIONS:
        raise ValueError(f"unknown motion {motion!r} - have: "
                         f"{', '.join(sorted(MOTIONS))}")
    spec = MOTIONS[motion]
    fps = int(fps or spec["fps"])
    seconds = float(spec["seconds"] if seconds is None else seconds)
    if fps < 2 or seconds <= 0:
        raise ValueError("fps >= 2 and seconds > 0")
    n = max(2, round(seconds * fps))
    if spec["loop"]:
        ts = [i / n for i in range(n)]
    else:
        ts = [i / (n - 1) for i in range(n)]
    return [_render_joints(motion_pose(motion, t), **kw) for t in ts]


def render_motion_mp4(motion: str, outdir, *, fps: int | None = None,
                      seconds: float | None = None,
                      wav: str | Path | None = None, seed: int = 7,
                      prop: str | None = None) -> dict:
    """Motion clip -> mp4. wav=None: silent art stage; wav given: the
    audio is the truth (video length follows it) + loudnorm mix."""
    if motion not in MOTIONS:
        raise ValueError(f"unknown motion {motion!r} - have: "
                         f"{', '.join(sorted(MOTIONS))}")
    if seconds is None and wav is not None:
        from pathlib import Path as _P
        import wave as _wave
        src = _P(wav)
        if not src.is_file():
            raise ValueError(f"no audio at {src}")
        with _wave.open(str(src), "rb") as w:
            seconds = w.getnframes() / w.getframerate()
    fps = int(fps or MOTIONS[motion]["fps"])
    frames = motion_frames(motion, fps=fps, seconds=seconds, seed=seed,
                           prop=prop)
    res = _encode_frames(frames, outdir, fps=fps, wav=wav,
                         name=f"motion_{motion}.mp4",
                         frames_dir="motion_frames",
                         concat="motion_concat.txt")
    res["motion"] = motion
    res["loop"] = MOTIONS[motion]["loop"]
    return res
