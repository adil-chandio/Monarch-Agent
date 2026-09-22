"""Psychoacoustic SFX synthesizer + DSP filters — stdlib only, WAV out.

SoLoud-inspired design: every sound is generated (sine/noise/envelope), never
sampled from a pack. Playbook wiring (N5 + sfx/map.md):

* ``heartbeat``  — dread under the value-debt beat (N4)
* ``hit``        — the 0.1s thumb-stop accent, one per open (N1)
* ``bass_drop``  — 40Hz sub pressure under reveals (N5)
* ``sonar_ping`` — the searching/tease cue (N3)
* ``glitch``     — the twist cue (never twice in a row, per sfx/map.md)
* ``riser``      — prediction build into a payoff (N3/N5)

Filters: ``bass_boost``, ``tension_echo``, ``cyber_glitch``, ``forensic_tape``,
``limiter``. VO always wins (L2): SFX here are short one-shots and beds duck
in the compositor timeline, never over speech.
"""

from __future__ import annotations

import math
import random
import struct
import wave
from pathlib import Path

#: the law frequency: felt, not heard (N5)
SUB_BASS_HZ = 40.0
#: total silence before the key fact (N5) — kept here so audio and timeline agree
SILENCE_DROP_S = 0.3

Filter = str  # one of FILTERS
FILTERS = ("bass_boost", "tension_echo", "cyber_glitch", "forensic_tape", "limiter")


# --------------------------------------------------------------------------
# core synthesis helpers (all return list[float] in -1..1)
# --------------------------------------------------------------------------


def _silence(seconds: float, sr: int) -> list[float]:
    return [0.0] * int(round(seconds * sr))


def _sine(freq: float, seconds: float, sr: int, amp: float = 1.0,
          decay: float | None = None, attack: float = 0.002) -> list[float]:
    n = int(round(seconds * sr))
    out = []
    for i in range(n):
        t = i / sr
        env = amp
        if attack > 0 and t < attack:
            env *= t / attack
        if decay is not None:
            env *= math.exp(-t / decay)
        out.append(env * math.sin(2 * math.pi * freq * t))
    return out


def _noise(seconds: float, sr: int, amp: float = 1.0, decay: float | None = None,
           seed: int = 0) -> list[float]:
    rng = random.Random(seed)
    n = int(round(seconds * sr))
    out = []
    for i in range(n):
        env = amp * (math.exp(-i / sr / decay) if decay else 1.0)
        out.append(env * (rng.random() * 2 - 1))
    return out


def _sweep(f0: float, f1: float, seconds: float, sr: int, amp: float = 1.0,
           decay: float | None = None, shape: str = "exp") -> list[float]:
    n = int(round(seconds * sr))
    out = []
    phase = 0.0
    for i in range(n):
        p = i / max(1, n - 1)
        if shape == "exp":
            f = f0 * (f1 / f0) ** p
        else:
            f = f0 + (f1 - f0) * p
        phase += 2 * math.pi * f / sr
        env = amp * (math.exp(-p * 3) if decay == "out" else 1.0)
        out.append(env * math.sin(phase))
    return out


def _mix(*parts: list[float]) -> list[float]:
    n = max(len(p) for p in parts)
    out = [0.0] * n
    for p in parts:
        for i, v in enumerate(p):
            out[i] += v
    return out


def _cat(*parts: list[float]) -> list[float]:
    out: list[float] = []
    for p in parts:
        out.extend(p)
    return out


def _env_ramp(samples: list[float], attack: float, sr: int) -> list[float]:
    a = max(1, int(attack * sr))
    out = list(samples)
    for i in range(min(a, len(out))):
        out[i] *= i / a
    return out


# --------------------------------------------------------------------------
# the SFX bank
# --------------------------------------------------------------------------


def sfx_heartbeat(sr: int = 44100, seed: int = 0) -> list[float]:
    """Lub-dub thump pair — felt chest pressure for dread (N4)."""
    def thump(amp: float) -> list[float]:
        body = _sine(55, 0.18, sr, amp=amp, decay=0.05)
        sub = _sine(SUB_BASS_HZ, 0.18, sr, amp=amp * 0.6, decay=0.06)
        click = _noise(0.01, sr, amp=amp * 0.15, seed=seed)
        return _mix(body, sub, click)

    return _cat(thump(0.95), _silence(0.12, sr), thump(0.6), _silence(0.45, sr))


def sfx_hit(sr: int = 44100, seed: int = 0) -> list[float]:
    """Impact accent — the 0.1s attention snap (N1)."""
    crack = _noise(0.12, sr, amp=0.9, decay=0.02, seed=seed)
    body = _sweep(180, 45, 0.45, sr, amp=0.95, decay="out")
    sub = _sine(SUB_BASS_HZ, 0.4, sr, amp=0.5, decay=0.12)
    return _mix(crack, body, sub)


def sfx_bass_drop(sr: int = 44100, seed: int = 0) -> list[float]:
    """Pitch drop into sustained 40Hz — N5 sub pressure under a reveal."""
    drop = _sweep(190, SUB_BASS_HZ, 0.7, sr, amp=0.9)
    sub = _sine(SUB_BASS_HZ, 0.9, sr, amp=0.8, decay=0.5)
    punch = _sweep(120, 40, 0.25, sr, amp=0.6, decay="out")
    return _mix(drop, _cat(_silence(0.7, sr), sub), punch)


def sfx_sonar_ping(sr: int = 44100, seed: int = 0) -> list[float]:
    """Searching ping + echo tail — the variable-ratio tease cue (N3)."""
    ping = _sine(880, 0.5, sr, amp=0.55, decay=0.09)
    ping = _env_ramp(ping, 0.004, sr)
    echo = _sine(880, 0.6, sr, amp=0.18, decay=0.16)
    return _mix(ping, _cat(_silence(0.18, sr), echo))


def sfx_glitch(sr: int = 44100, seed: int = 0) -> list[float]:
    """Bit-crushed stutters — the twist cue (sfx/map.md: never twice in a row)."""
    rng = random.Random(seed)
    out: list[float] = []
    for _ in range(7):
        f = rng.choice((220, 330, 440, 660, 880))
        blip = _sine(f, 0.045, sr, amp=rng.uniform(0.4, 0.8), decay=None)
        # quantize to a 4-bit-ish staircase = cheap bit crush
        blip = [round(v * 7) / 7 for v in blip]
        out.extend(blip)
        out.extend(_silence(rng.uniform(0.01, 0.05), sr))
    return out if out else _silence(0.3, sr)


def sfx_riser(sr: int = 44100, seed: int = 0) -> list[float]:
    """Noise + tone sweep rising into a cut — prediction build (N3/N5)."""
    tone = _sweep(110, 880, 1.6, sr, amp=0.5, shape="exp")
    hiss = _noise(1.6, sr, amp=0.35, seed=seed)
    n = len(tone)
    for i in range(n):  # linear volume ramp into the payoff
        g = (i + 1) / n
        tone[i] *= g
        hiss[i] *= g * g
    return _mix(tone, hiss)


#: kind -> (builder, natural seconds)
SFX_KINDS: dict[str, tuple] = {
    "heartbeat": (sfx_heartbeat, 1.15),
    "hit": (sfx_hit, 0.45),
    "bass_drop": (sfx_bass_drop, 1.6),
    "sonar_ping": (sfx_sonar_ping, 0.78),
    "glitch": (sfx_glitch, 0.4),
    "riser": (sfx_riser, 1.6),
}


# --------------------------------------------------------------------------
# DSP filters
# --------------------------------------------------------------------------


def bass_boost(samples: list[float], sr: int, gain: float = 1.4) -> list[float]:
    """One-pole low shelf: low end up, voice band untouched."""
    rc = 1.0 / (2 * math.pi * 150)  # 150Hz shelf
    dt = 1.0 / sr
    a = dt / (rc + dt)
    lp = 0.0
    out = []
    for v in samples:
        lp += a * (v - lp)
        out.append(v + lp * (gain - 1))
    return out


def tension_echo(samples: list[float], sr: int, delay_s: float = 0.22,
                 feedback: float = 0.45) -> list[float]:
    """Feedback delay — the tension build under open loops."""
    d = max(1, int(delay_s * sr))
    out = list(samples)
    buf = [0.0] * d
    for i, v in enumerate(samples):
        echoed = buf[i % d]
        buf[i % d] = v + echoed * feedback
        out[i] = v + echoed * feedback
    return out


def cyber_glitch(samples: list[float], sr: int, crush: int = 5,
                 seed: int = 0) -> list[float]:
    """Sample-hold bit crush + random one-shot repeat stutters (bounded)."""
    rng = random.Random(seed)
    levels = 2 ** max(1, crush) / 2
    hold_len = max(1, sr // 4000)
    crushed: list[float] = []
    hold = 0.0
    for i, v in enumerate(samples):
        if i % hold_len == 0:
            hold = round(v * levels) / levels
        crushed.append(hold)
    # one-shot stutters: occasionally replay the preceding ~20-60ms once
    out: list[float] = []
    for i, v in enumerate(crushed):
        if i > 0 and rng.random() < 0.002:
            L = int((0.02 + rng.random() * 0.04) * sr)
            out.extend(crushed[max(0, i - L):i])
        out.append(v)
    return out


def forensic_tape(samples: list[float], sr: int, seed: int = 0) -> list[float]:
    """Lowpass + wow/flutter + hiss — the 'evidence' voice of the tape."""
    rc = 1.0 / (2 * math.pi * 3200)
    dt = 1.0 / sr
    a = dt / (rc + dt)
    lp = 0.0
    rng = random.Random(seed)
    out = []
    for i, v in enumerate(samples):
        lp += a * (v - lp)
        t = i / sr
        wow = 1.0 + 0.02 * math.sin(2 * math.pi * 0.7 * t) \
            + 0.008 * math.sin(2 * math.pi * 6.1 * t)
        hiss = (rng.random() * 2 - 1) * 0.012
        out.append(lp * 0.9 * wow + hiss)
    return out


def limiter(samples: list[float], ceiling: float = 0.95) -> list[float]:
    """tanh soft clip — everything peaks strictly under ``ceiling``."""
    k = 3.0
    return [ceiling * math.tanh(v * k) for v in samples]


FILTER_FNS = {
    "bass_boost": bass_boost,
    "tension_echo": tension_echo,
    "cyber_glitch": cyber_glitch,
    "forensic_tape": forensic_tape,
    "limiter": limiter,
}


# --------------------------------------------------------------------------
# render + write
# --------------------------------------------------------------------------


def render_sfx(kind: str, sr: int = 44100, seed: int = 0,
               seconds: float | None = None,
               filters: list[Filter] | None = None) -> list[float]:
    """One SFX kind -> float samples, optional filter chain, limited."""
    if kind not in SFX_KINDS:
        raise ValueError(f"unknown sfx kind {kind!r}: use {', '.join(SFX_KINDS)}")
    builder, natural = SFX_KINDS[kind]
    s = builder(sr=sr, seed=seed)
    if seconds is not None:
        n = int(round(seconds * sr))
        s = (s + [0.0] * n)[:n]  # truncate or pad with law-mandated silence
    for name in (filters or []):
        fn = FILTER_FNS.get(name)
        if fn is None:
            raise ValueError(f"unknown filter {name!r}: use {', '.join(FILTER_FNS)}")
        s = fn(s, sr) if name != "limiter" else fn(s)
    return limiter(s)


def write_wav(path: str | Path, samples: list[float], sr: int = 44100) -> Path:
    """Float samples -1..1 -> 16-bit mono WAV."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    frames = b"".join(struct.pack("<h", int(max(-1.0, min(1.0, v)) * 32767))
                      for v in samples)
    with wave.open(str(p), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(frames)
    return p


def duration_s(samples: list[float], sr: int = 44100) -> float:
    return round(len(samples) / sr, 3) if sr else 0.0
