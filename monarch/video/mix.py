"""The mix bus — five layers, VO always wins (L2), loudness like pros.

    Layer 1  VO / dialogue   — the skeleton, peaks around -6..-12 dBFS
    Layer 2  music bed       — ducked under VO (sidechain-style envelope)
    Layer 3  SFX             — per-scene role cues (hit/riser/bass_drop/...)
    Layer 4  room tone       — kills "digital silence" between lines
    Layer 5  master          — soft limiter, level report (RMS/peak dBFS)

Pro targets this implements (mined from editor standards):
    VO avg around -16 dBFS; music -18..-25 dB under speech; whoosh on
    cuts; riser under tension; master peak < -1 dB. Pure stdlib — every
    value is measured and reported, nothing is " vibes".
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path

from monarch.video.audio import (
    SFX_KINDS,
    render_sfx,
    sfx_bass_drop,
    sfx_glitch,
    sfx_hit,
    sfx_riser,
    sfx_heartbeat,
    sfx_sonar_ping,
    limiter,
)

#: mix laws (dBFS)
VO_GAIN = 0.85          # ~ -1.4 dB headroom on the voice
MUSIC_DB = -24.0        # music bed under speech
MUSIC_NOVO_DB = -14.0   # music breathes when nobody speaks
ROOM_DB = -46.0         # the noise floor that reads as "real"
DUCK_FLOOR = 0.25       # music never disappears fully under VO

_FALLBACK_SYNTH = {
    "hit": sfx_hit,
    "bass_drop": sfx_bass_drop,
    "glitch": sfx_glitch,
    "riser": sfx_riser,
    "heartbeat": sfx_heartbeat,
    "sonar_ping": sfx_sonar_ping,
}


# ---------------------------------------------------------------------------
# level helpers
# ---------------------------------------------------------------------------


def db_to_gain(db: float) -> float:
    return 10 ** (db / 20)


def rms_dbfs(samples: list[float]) -> float:
    if not samples:
        return -120.0
    r = math.sqrt(sum(v * v for v in samples) / len(samples))
    return round(20 * math.log10(max(r, 1e-9)), 1)


def peak_dbfs(samples: list[float]) -> float:
    if not samples:
        return -120.0
    peak = max(abs(v) for v in samples)
    if peak <= 0.0:
        return -120.0
    return round(20 * math.log10(peak), 1)


# ---------------------------------------------------------------------------
# layers
# ---------------------------------------------------------------------------


def music_bed(duration_s: float, sr: int, *, seed: int = 0) -> list[float]:
    """Dark pulse bed — 55Hz body + slow noise swell, looped to length."""
    import random

    rng = random.Random(seed)
    one = []
    n = int(6.0 * sr)
    for i in range(n):
        t = i / sr
        pulse = 0.5 + 0.5 * math.sin(2 * math.pi * 0.25 * t - math.pi / 2)
        v = (0.5 * math.sin(2 * math.pi * 55 * t)
             + 0.22 * math.sin(2 * math.pi * 110.3 * t)
             + 0.10 * (rng.random() * 2 - 1) * (0.4 + 0.6 * pulse))
        one.append(v * (0.35 + 0.65 * pulse))
    out: list[float] = []
    need = int(math.ceil(duration_s * sr))  # int target — no float-fraction spin
    while len(out) < need:
        out.extend(one[:min(len(one), need - len(out))])
    return out


def room_tone(duration_s: float, sr: int, *, seed: int = 1) -> list[float]:
    import random

    rng = random.Random(seed)
    return [(rng.random() * 2 - 1) * 0.01 for _ in range(int(duration_s * sr))]


def duck_under_voice(music: list[float], vo: list[float], sr: int, *,
                     floor: float = DUCK_FLOOR, attack: int = 2400) -> list[float]:
    """Envelope-sidechain: music dips while (and only while) VO speaks."""
    env = vo_envelope(vo, sr)
    g = [floor + (1 - floor) * (1 - e) for e in env]
    # smooth the gain curve — ~100ms attack/release (5 frames @ 20ms)
    sm: list[float] = []
    acc = g[0] if g else 1.0
    alpha = 1.0 / max(1, min(60, int(attack / max(1, sr // 50))))
    for v in g:
        acc += (v - acc) * alpha
        sm.append(acc)
    # expand frame gains to sample rate (sm is per 20ms frame, audio is not)
    n = max(1, sr // 50)
    out = list(music)
    for i in range(len(out)):
        out[i] *= sm[min(len(sm) - 1, i // n)]
    return out


def vo_envelope(vo: list[float], sr: int, frame_s: float = 0.02) -> list[float]:
    """0..1 speech activity per frame, normalized to the track's own peak."""
    n = max(1, int(frame_s * sr))
    env = []
    peak = max((abs(v) for v in vo), default=1.0) or 1.0
    thr = peak * 0.04
    for i in range(0, len(vo), n):
        win = vo[i:i + n]
        r = math.sqrt(sum(v * v for v in win) / max(1, len(win)))
        env.append(min(1.0, r / thr) if r > thr else 0.0)
    return env


def add_at(base: list[float], piece: list[float], at_s: float, gain: float,
           sr: int) -> list[float]:
    start = int(at_s * sr)
    if start < 0:
        piece = piece[-int(start):]
        start = 0
    need = start + len(piece)
    if need > len(base):
        base.extend([0.0] * (need - len(base)))
    for i, v in enumerate(piece):
        base[start + i] += v * gain
    return base


# ---------------------------------------------------------------------------
# the mix
# ---------------------------------------------------------------------------


@dataclass
class MixReport:
    duration_s: float
    vo_rms: float
    vo_peak: float
    master_rms: float
    master_peak: float
    music_db: float
    duck_events: int
    sfx_events: int
    warnings: list[str] = field(default_factory=list)
    vo_gate: str = "NO VO"   # G7: VO must survive into the master
    mood: str = "tension"    # RENDER MEMORY 3: warm | tension

    def summary(self) -> str:
        return (f"MIX {self.duration_s:.1f}s | VO {self.vo_rms}/{self.vo_peak} dBFS | "
                f"master {self.master_rms}/{self.master_peak} dBFS | "
                f"music {self.music_db} dB ducked | "
                f"duck events {self.duck_events} | sfx {self.sfx_events}"
                + f" | VO GATE {self.vo_gate} | MOOD {self.mood}"
                + ("" if not self.warnings else
                   " | WARN: " + "; ".join(self.warnings)))


# ---------------------------------------------------------------------------
# RENDER MEMORY 3 - warm supportive bed (motivational storytelling)
# Banned-by-default here: heartbeat, drones, sub-drops, riser stacks,
# silence carves (law 3.2). Pads breathe; sparkle cannot clash (C-pent).
# ---------------------------------------------------------------------------

WARM_PROG = [
    ("A2", ["A2", "C3", "E3"]),          # Am
    ("F2", ["F2", "A2", "C3"]),          # F
    ("C3", ["C3", "E3", "G3"]),          # C
    ("G2", ["G2", "B2", "D3"]),          # G
]
_WARM_END = ("C3", ["C3", "D3", "E3", "G3"])   # Cadd9 resolve
_NOTE_A4 = 440.0
_SEMITONES = {"C": -9, "D": -7, "E": -5, "F": -4, "G": -2, "A": 0, "B": 2}


def _hz(note: str) -> float:
    import math as _m
    name = note[0]
    octv = int(note[-1]) if note[-1].isdigit() else 4
    semi = _SEMITONES[name] + (octv - 4) * 12
    return _NOTE_A4 * (2.0 ** (semi / 12.0))


def warm_bed(duration_s: float, sr: int, *, seed: int = 0) -> list[float]:
    """Law 3.1/3.4: warm pads Am-F-C-G (+Cadd9 resolve), attack <= 0.4 s,
    sparse C-pentatonic music-box sparkle, ONE gentle build into the CTA
    window (last ~18%), hopeful resolve at the end. Deterministic."""
    import math as _m
    import random as _r
    n = int(duration_s * sr)
    rng = _r.Random(seed * 31 + 7)
    chord_s = 2.6
    pad = [0.0] * n
    t = 0.0
    ci = 0
    prog = [ch for ch in WARM_PROG] + [_WARM_END]
    while t < duration_s:
        root, notes = prog[ci % len(prog)]
        seg_s = min(chord_s, duration_s - t)
        if seg_s <= 0.05:
            break
        a = int(t * sr)
        seg_n = int(seg_s * sr)
        # per-chord envelope: 0.35s rise, 0.5s fall (breathing)
        rise = min(int(0.35 * sr), seg_n // 2)
        fall = min(int(0.50 * sr), seg_n // 2)
        for i in range(seg_n):
            env = 1.0
            if i < rise:
                env = i / rise
            elif i > seg_n - fall:
                env = max(0.0, (seg_n - i) / fall)
            v = 0.0
            for note in notes:
                f = _hz(note)
                v += _m.sin(2 * _m.pi * f * ((i + a) / sr))
            pad[a + i] += env * v / len(notes) * 0.32
        t += seg_s
        ci += 1
    # music-box sparkle: C-pentatonic plucks, sparse + quiet
    pent = [_hz("C5"), _hz("D5"), _hz("E5"), _hz("G5"), _hz("A5")]
    pos = 0.9
    while pos < duration_s - 0.4:
        f = pent[rng.randrange(len(pent))]
        a = int(pos * sr)
        dur = int(0.5 * sr)
        for i in range(min(dur, n - a)):
            envv = _m.exp(-i / (0.09 * sr))
            pad[a + i] += 0.05 * envv * _m.sin(2 * _m.pi * f * (i / sr))
        pos += rng.uniform(1.4, 2.3)
    # ONE gentle build into the CTA window (+3 dB over the last 18%)
    build_a = int(n * 0.82)
    if build_a < n:
        for i in range(build_a, n):
            g = 1.0 + 1.412 * (i - build_a) / max(1, n - build_a)  # +3 dB
            pad[i] *= g
    # frame-1 law (3.4): 0.4 s global fade-in only - pads audible at once
    lead = min(int(0.4 * sr), n)
    for i in range(lead):
        pad[i] *= i / lead
    return pad


def mix(
    *,
    duration_s: float,
    vo: list[float] | None = None,
    sr: int = 24000,
    board: list[dict] | None = None,
    wavs_dir: str | Path | None = None,
    music: bool = True,
    seed: int = 0,
    music_mood: str = "tension",
) -> tuple[list[float], MixReport]:
    """Five-layer master. VO wins; everything else serves it.

    ``music_mood``: "tension" = the classic 3-act engine (heartbeat,
    riser, sub-drops); "warm" = RENDER MEMORY 3.1 supportive pads
    (Am-F-C-G, sparkle, gentle CTA build) - motivational content law.
    """
    if duration_s <= 0:
        raise ValueError("duration must be > 0")
    board = board or []
    n = int(duration_s * sr)
    vo = vo or []

    # Layer 1 — voice
    voice = list(vo[:n])
    if len(voice) < n:
        voice.extend([0.0] * (n - len(voice)))
    voice = [v * VO_GAIN for v in voice]
    has_voice = any(abs(v) > 1e-4 for v in voice)

    # Layer 2 — music bed, ducked
    warnings: list[str] = []
    music_gain = db_to_gain(MUSIC_DB if has_voice else MUSIC_NOVO_DB)
    if not music:
        bed = [0.0] * n
    elif music_mood == "warm":
        bed = warm_bed(duration_s, sr, seed=seed)
    else:
        bed = music_bed(duration_s, sr, seed=seed)
    if has_voice and music:
        bed = duck_under_voice(bed, voice, sr)
    bed = [b * music_gain for b in bed]

    # Layer 3 — SFX per scene role from the board
    sfx_events = 0
    for s in board:
        kind = str(s.get("sfx", "")).strip()
        if not kind:
            continue
        t0 = float(s.get("t_start", 0.0))
        if kind in _FALLBACK_SYNTH:
            piece = _FALLBACK_SYNTH[kind](sr=sr, seed=seed + int(s.get("id", 0)))
        elif kind in SFX_KINDS:
            piece = render_sfx(kind, sr=sr, seed=seed)
        else:
            warnings.append(f"scene {s.get('id')}: unknown sfx {kind!r} skipped")
            continue
        scene_dur = max(0.2, float(s.get("t_end", t0 + 2)) - t0)
        piece = (piece + [0.0] * int(scene_dur * sr))[:int(scene_dur * sr)]
        bed2 = add_at(bed, piece, t0, db_to_gain(-8.0), sr)
        bed = bed2 if len(bed2) >= len(bed) else bed
        sfx_events += 1
    if not sfx_events:
        warnings.append("no SFX placed — board carried no sfx fields")

    # Layer 4 — room tone (anti digital-silence)
    tone = [t * db_to_gain(ROOM_DB) for t in room_tone(duration_s, sr, seed=seed + 3)]

    # Layer 5 — sum + master limiter
    master = [voice[i] + bed[i] + tone[i] for i in range(n)]
    # RENDER MEMORY 3.5: mix peak law 0.72-0.82 (AAC headroom; the old
    # 0.97 ceiling read as clipping next to the per-channel law)
    master = limiter(master, ceiling=0.82)

    report = MixReport(
        duration_s=round(n / sr, 3),
        vo_rms=rms_dbfs(voice),
        vo_peak=peak_dbfs(voice),
        master_rms=rms_dbfs(master),
        master_peak=peak_dbfs(master),
        music_db=MUSIC_DB if has_voice else MUSIC_NOVO_DB,
        mood=music_mood,
        duck_events=_count_dips(voice, sr) if has_voice else 0,
        sfx_events=sfx_events,
        warnings=warnings,
    )
    if has_voice and report.vo_peak > -1.0:
        warnings.append("VO peaks hot — consider VO_GAIN down")
    # G7 gate: broadband numbers lie (booms mask a lost VO). Compare the
    # VO bus against the MASTER inside real speech windows: if the voice
    # got misbound or lost, the delta explodes. Fail loudly, never silently.
    if has_voice:
        ok, detail = _vo_gate(master, voice, sr, n)
        report.vo_gate = ("PASS: " if ok else "FAIL: ") + detail
        if not ok:
            warnings.append("VO GATE FAIL - voice lost/misbound in master (G7)")
    return master, report


def _count_dips(vo: list[float], sr: int) -> int:
    env = vo_envelope(vo, sr)
    dips = 0
    was_up = False
    for v in env:
        if v > 0.5 and not was_up:
            was_up = True
        elif v <= 0.1 and was_up:
            dips += 1
            was_up = False
    return dips


def _vo_gate(master: list[float], voice: list[float], sr: int, n: int, *,
             max_delta_db: float = 6.0) -> tuple[bool, str]:
    """Multi-window speech-level proof (L3): first + middle + last onset."""
    frame = max(1, int(sr * 0.01))
    win = max(frame, int(sr * 0.4))
    env = vo_envelope(voice, sr)
    voiced = [i for i, v in enumerate(env) if v > 0.02]
    if not voiced:
        return False, "no voiced frames in the VO bus"
    picks = (voiced[0], voiced[len(voiced) // 2], voiced[-1])
    checked, worst = 0, 0.0
    for p in picks:
        a = min(n - 1, p * frame)
        b = min(n, a + win)
        if b - a < frame * 5:
            continue
        vm = rms_dbfs(voice[a:b])
        mm = rms_dbfs(master[a:b])
        if vm <= -60.0:
            continue
        # G7 failure mode = the voice is GONE: master collapses to bed
        # level. Music/sfx sitting ON TOP of the voice is legitimate, so
        # only the DROP direction fails the window.
        drop = vm - mm
        worst = max(worst, drop)
        checked += 1
        if drop > max_delta_db:
            return False, (f"window @{a / sr:.2f}s master {mm} dBFS vs VO "
                           f"{vm} dBFS (voice dropped {drop:.1f} dB > "
                           f"{max_delta_db})")
    if not checked:
        return False, "no measurable VO windows above -60 dBFS"
    return True, f"{checked} windows, worst drop {worst:.1f} dB"
