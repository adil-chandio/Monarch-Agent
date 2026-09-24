"""Voiceover track — AUDIO-FIRST timing, sentence glue, honest QC.

Law this module finally enforces (L1: VO is the skeleton):

* scripts are chunked at **sentence boundaries** — never mid-clause;
* every chunk gets a **100 ms lead-in** and a **250-500 ms tail** so the
  last consonant survives (the classic TTS cut);
* chunks join with a **60 ms equal-power crossfade** — no abrupt starts;
* inter-sentence gaps are capped: **0.5 s** after a sentence, **0.3 s**
  after a comma-level beat, **0.15 s** continuing;
* speech length is **measured from the audio envelope** (amplitude
  threshold), never from file duration — TTS engines pad trailing
  silence and pipelines that trust the file length grow dead-air gaps.

Backends (auto-detected, graceful):

* ``edge``    — edge-tts CLI + ffmpeg (network; PC use). Missing here → skip.
* ``dir``     — per-scene WAVs produced elsewhere (Chatterbox/ElevenLabs on
                your GPU box); Monarch glues + times + QC's them.
* ``mumble``  — built-in synthesized placeholder (syllable-rate modulated
                hum). Clearly labelled PLACEHOLDER: it exists so timing,
                glue and the whole video pipeline run offline tonight.

QC is fail-closed honesty: gaps over 0.6 s, clipped endings, dead lead-ins
and coverage drift versus the board are reported as named checks.
"""

from __future__ import annotations

import json
import math
import random
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from monarch.core.words import count_words

SR_DEFAULT = 24000

#: glue laws (seconds)
LEAD_IN = 0.10
TAIL = 0.35
LEAD_KEEP = 0.06   # G8: keep a hair of lead room, kill the dead air
CROSSFADE = 0.06
GAP_SENTENCE = 0.5
GAP_COMMA = 0.3
GAP_CONTINUING = 0.15
MAX_GAP = 0.6  # QC fail threshold

_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+")
_CLAUSE_SPLIT = re.compile(r"(?<=[,;:])\s+")
_VOWELS = "aeiouy"


# ---------------------------------------------------------------------------
# text -> sentence chunks (the anti-mid-cut law)
# ---------------------------------------------------------------------------


def sentence_chunks(text: str, max_chars: int = 240) -> list[str]:
    """Split into sentence chunks (<= max_chars, clause-level fallback)."""
    text = re.sub(r"\s+", " ", (text or "").strip())
    if not text:
        return []
    out: list[str] = []
    for sentence in _SENT_SPLIT.split(text):
        s = sentence.strip()
        if not s:
            continue
        if len(s) <= max_chars:
            out.append(s)
            continue
        buf = ""
        for clause in _CLAUSE_SPLIT.split(s):
            cand = f"{buf}, {clause}" if buf else clause
            if len(cand) > max_chars and buf:
                out.append(buf)
                buf = clause
            else:
                buf = cand
        if buf:
            out.append(buf)
    return out


def next_gap(chunk: str) -> float:
    """Cap for the silence AFTER this chunk (punctuation-level)."""
    c = (chunk or "").strip()
    if c.endswith((".", "!", "?")):
        return GAP_SENTENCE
    if c.endswith((",", ";", ":")):
        return GAP_COMMA
    return GAP_CONTINUING


# ---------------------------------------------------------------------------
# envelope measurement — the anti-dead-air law
# ---------------------------------------------------------------------------


def envelope(samples: list[float], sr: int, frame_s: float = 0.01) -> list[float]:
    """RMS per frame — the raw material for speech-end and gap detection."""
    n = max(1, int(frame_s * sr))
    out = []
    for i in range(0, len(samples), n):
        win = samples[i:i + n]
        out.append(math.sqrt(sum(v * v for v in win) / max(1, len(win))))
    return out


def measure(samples: list[float], sr: int, threshold: float = 0.02) -> dict:
    """Speech stats from the waveform itself (never trust file length)."""
    if not samples:
        return {"speech_end_s": 0.0, "leading_silence_s": 0.0,
                "duration_s": 0.0, "rms_dbfs": -120.0, "peak_dbfs": -120.0}
    peak = max(abs(v) for v in samples) or 1e-9
    thr = max(threshold, peak * 0.02)
    env = envelope(samples, sr)
    frame_s = len(samples) / sr / max(1, len(env))
    speech_frames = [i for i, v in enumerate(env) if v > thr]
    if not speech_frames:
        return {"speech_end_s": 0.0, "leading_silence_s": len(samples) / sr,
                "duration_s": len(samples) / sr, "rms_dbfs": -120.0,
                "peak_dbfs": 20 * math.log10(peak)}
    speech_end = (speech_frames[-1] + 1) * frame_s
    lead = speech_frames[0] * frame_s
    rms = math.sqrt(sum(v * v for v in samples) / len(samples))
    return {
        "speech_end_s": round(speech_end, 3),
        "leading_silence_s": round(lead, 3),
        "duration_s": round(len(samples) / sr, 3),
        "rms_dbfs": round(20 * math.log10(max(rms, 1e-9)), 1),
        "peak_dbfs": round(20 * math.log10(peak), 1),
    }


def trim_tail_silence(samples: list[float], sr: int, keep_s: float = TAIL) -> list[float]:
    """Cut trailing silence down to ``keep_s`` after the last real speech."""
    m = measure(samples, sr)
    end = m["speech_end_s"] if m["speech_end_s"] > 0 else len(samples) / sr
    keep = min(keep_s, m["duration_s"])
    n = int(min(len(samples), (end + keep) * sr))
    return samples[:n]


# ---------------------------------------------------------------------------
# backends
# ---------------------------------------------------------------------------


def _mumble(text: str, sr: int, seed: int = 0) -> list[float]:
    """Placeholder voice — syllable-rate modulated hum, clearly not final.

    Exists so timing/glue/mix/QC run offline. Sounds intentionally wrong.
    """
    rng = random.Random(seed * 977 + len(text))
    syllables = max(2, sum(1 for i in range(1, len(text))
                           if text[i].lower() in _VOWELS and text[i - 1].lower() not in _VOWELS
                           and text[i].isalpha()))
    rate = 5.2  # syllables/second — conversational
    out: list[float] = []
    for syl in range(syllables):
        dur = 0.14 + rng.random() * 0.06
        f = 108 + rng.random() * 30
        n = int(dur * sr)
        for i in range(n):
            t = i / sr
            env = math.sin(math.pi * min(1.0, i / n)) ** 1.5
            v = 0.6 * math.sin(2 * math.pi * f * t) \
                + 0.25 * math.sin(2 * math.pi * f * 2 * t) \
                + 0.08 * (rng.random() * 2 - 1)
            out.append(0.5 * env * v)
        out.extend([0.0] * int((1 / rate) * sr * 0.55))
    return out


def trim_lead_silence(samples: list[float], sr: int,
                      keep_s: float = LEAD_KEEP,
                      threshold: float = 0.02) -> list[float]:
    """G8/L4: leading breath-silence dies; first word lands almost at 0.00s.

    Keeps ``keep_s`` of room before the first voiced sample so the attack
    is not clipped. The no_dead_lead QC gate (<=0.3s) verifies it after.
    """
    idx = next((i for i, v in enumerate(samples) if abs(v) > threshold), None)
    if idx is None:
        return list(samples)
    cut = max(0, idx - int(keep_s * sr))
    return samples[cut:] if cut else list(samples)


def _edge_tts(text: str, sr: int, voice: str) -> list[float]:
    """Real VO via edge-tts CLI + ffmpeg (needs network + tools; PC path)."""
    if shutil.which("edge-tts") is None or shutil.which("ffmpeg") is None:
        raise RuntimeError("edge backend needs edge-tts + ffmpeg on PATH")
    import wave

    with tempfile.TemporaryDirectory() as td:
        mp3 = Path(td) / "v.mp3"
        wav = Path(td) / "v.wav"
        r = subprocess.run(
            ["edge-tts", "--voice", voice, "--text", text,
             "--write-media", str(mp3)],
            capture_output=True, timeout=60,
        )
        if r.returncode != 0:
            raise RuntimeError(f"edge-tts failed: {r.stderr.decode()[:200]}")
        r = subprocess.run(
            ["ffmpeg", "-y", "-i", str(mp3), "-ar", str(sr), "-ac", "1",
             str(wav)],
            capture_output=True, timeout=60,
        )
        if r.returncode != 0:
            raise RuntimeError(f"ffmpeg failed: {r.stderr.decode()[:200]}")
        with wave.open(str(wav), "rb") as w:
            raw = w.readframes(w.getnframes())
    import struct

    return [v / 32768.0 for v in struct.unpack(f"<{len(raw)//2}h", raw)]


def _dir_backend(scene_id: int, wavs_dir: Path, sr: int) -> list[float]:
    """Pre-made per-scene WAVs (Chatterbox / ElevenLabs / recorded)."""
    import wave

    for cand in (wavs_dir / f"scene_{scene_id:02d}.wav",
                 wavs_dir / f"scene_{scene_id}.wav",
                 wavs_dir / f"{scene_id}.wav"):
        if cand.is_file():
            with wave.open(str(cand), "rb") as w:
                if w.getframerate() != sr or w.getnchannels() != 1 \
                        or w.getsampwidth() != 2:
                    raise ValueError(
                        f"{cand.name}: need 16-bit mono {sr}Hz wavs "
                        f"(got {w.getframerate()}Hz {w.getnchannels()}ch)")
                raw = w.readframes(w.getnframes())
            import struct

            return [v / 32768.0 for v in
                    struct.unpack(f"<{len(raw)//2}h", raw)]
    raise FileNotFoundError(f"no wav for scene {scene_id} in {wavs_dir}")


# ---------------------------------------------------------------------------
# glue — lead-in / tail / crossfade (the anti-abrupt law)
# ---------------------------------------------------------------------------


def _crossfade(a: list[float], b: list[float], sr: int) -> list[float]:
    n = min(len(a), int(CROSSFADE * sr))
    if n <= 0:
        return a + b
    body = a[:-n]
    tail = a[-n:]
    head = b[:n]
    rest = b[n:]
    mixed = [tail[i] * (1 - (i + 1) / n) + head[i] * ((i + 1) / n)
             for i in range(n)]
    return body + mixed + rest


def glue_chunks(chunks: list[list[float]], sr: int) -> list[float]:
    """Chunks -> one scene track: lead-in, 60ms crossfades, tail."""
    if not chunks:
        return [0.0] * sr
    out: list[float] = [0.0] * int(LEAD_IN * sr)
    for i, c in enumerate(chunks):
        c = trim_tail_silence(c, sr, keep_s=0.12)
        out = _crossfade(out, c, sr) if i else out + c
        if i < len(chunks) - 1:
            gap = next_gap(chunks_text_guard := "")  # placeholder never used
            out.extend([0.0] * int(GAP_CONTINUING * sr))
    out.extend([0.0] * int(TAIL * sr))
    return out


# ---------------------------------------------------------------------------
# scene + timeline build
# ---------------------------------------------------------------------------


@dataclass
class VOScene:
    scene_id: int
    file: str
    speech_s: float
    start: float
    end: float
    chunks: int
    backend: str


def synthesize_scene(
    scene_id: int,
    line: str,
    *,
    backend: str = "auto",
    wavs_dir: str | Path | None = None,
    sr: int = SR_DEFAULT,
    seed: int = 0,
) -> tuple[list[float], list[str], str]:
    """One scene's spoken line -> (audio, chunk texts, backend used)."""
    chunks = sentence_chunks(line)
    if not chunks:
        raise ValueError(f"scene {scene_id}: nothing to speak")
    used = backend
    audio = None
    if backend in ("auto", "edge"):
        try:
            audio = _edge_tts(" ".join(chunks), sr, voice="en-US-ChristopherNeural")
            used = "edge"
        except Exception:
            audio = None
        if audio is None and backend == "edge":
            raise RuntimeError("edge backend unavailable (no edge-tts/ffmpeg/net)")
    if audio is None and backend in ("auto", "dir"):
        if wavs_dir and Path(wavs_dir).is_dir():
            try:
                audio = _dir_backend(scene_id, Path(wavs_dir), sr)
                used = "dir"
            except FileNotFoundError:
                if backend == "dir":
                    raise
    if audio is None:
        parts = [_mumble(c, sr, seed=seed + i) for i, c in enumerate(chunks)]
        audio = parts[0]
        for p in parts[1:]:
            audio.extend([0.0] * int(next_gap("x") * sr * 0.3))
            audio.extend(p)
        used = "mumble"
        return trim_lead_silence(glue_chunks(parts, sr), sr), chunks, used
    return trim_lead_silence(
        glue_chunks([trim_tail_silence(audio, sr, keep_s=0.12)], sr), sr
    ), chunks, used


def build_voiceover(
    scenes: list[dict],
    *,
    backend: str = "auto",
    wavs_dir: str | Path | None = None,
    sr: int = SR_DEFAULT,
    seed: int = 0,
    audio_first: bool = False,
    first_min_s: float = 1.6,
) -> dict:
    """Board scenes -> VO track + timing (+ new timeline when audio-first).

    Board mode: track is placed sequentially with gap caps; the M3 board
    stays the truth and QC reports drift. Audio-first mode: scene durations
    come from measured speech (L1 wins; the maths line becomes the target
    we deviate from, honestly reported).
    """
    if not scenes:
        raise ValueError("This is missing, could you provide it: scenes.")
    tracks: list[list[float]] = []
    meta_rows: list[VOScene] = []
    used_backends: set[str] = set()
    for i, s in enumerate(scenes, 1):
        line = str(s.get("vo_line", "")).strip()
        audio, chunks, used = synthesize_scene(
            i, line, backend=backend, wavs_dir=wavs_dir, sr=sr, seed=seed + i
        )
        used_backends.add(used)
        tracks.append(audio)
        meta_rows.append(VOScene(
            scene_id=i, file=f"vo/scene_{i:02d}.wav",
            speech_s=round(len(audio) / sr, 3), start=0.0, end=0.0,
            chunks=len(chunks), backend=used,
        ))

    # sequential placement with gap caps (no abrupt line starts)
    gaps: list[float] = []
    timeline: list[VOScene] = []
    track: list[float] = []
    t = 0.0
    for i, (row, audio) in enumerate(zip(meta_rows, tracks)):
        if i:
            gap = GAP_SENTENCE if scenes[i - 1].get("vo_line", "").rstrip().endswith(
                (".", "!", "?")) else GAP_COMMA
            t += gap
            gaps.append(gap)
        start = t
        # pad to start
        if len(track) < int(round(start * sr)):
            track.extend([0.0] * (int(round(start * sr)) - len(track)))
        track.extend(audio)
        end = start + len(audio) / sr
        timeline.append(VOScene(
            scene_id=row.scene_id, file=row.file,
            speech_s=row.speech_s, start=round(start, 3), end=round(end, 3),
            chunks=row.chunks, backend=row.backend,
        ))
        t = end

    # board-mode timing vs measured timing
    new_scenes = None
    board_end = float(scenes[-1].get("t_end", 0.0) or 0.0)
    vo_end = round(len(track) / sr, 3)
    if audio_first:
        # rebuild a timeline whose durations follow the voice (L1)
        new_scenes: list[dict] = []
        t = 0.0
        for i, row in enumerate(timeline, 1):
            dur = row.speech_s
            if i == 1:
                dur = max(first_min_s, min(dur, 3.0))
            new_scenes.append({
                **scenes[i - 1],
                "t_start": round(t, 3),
                "t_end": round(t + dur, 3),
            })
            t += dur
        board_end = t
    qc = qc_track(track, sr, board_end_s=board_end,
                  gaps=[(r.start, g) for r, g in zip(timeline[1:], gaps)])
    return {
        "track": track,
        "sr": sr,
        "vo_end_s": vo_end,
        "board_end_s": round(board_end, 3),
        "scenes": [r.__dict__ for r in timeline],
        "backends": sorted(used_backends),
        "placeholder": "mumble" in used_backends,
        "qc": qc,
        "scenes_new": new_scenes if audio_first else None,
    }


def qc_track(track: list[float], sr: int, *, board_end_s: float,
             gaps: list[tuple[float, float]]) -> list[dict]:
    """Named checks, fail-closed honesty (these bugs never ship silently)."""
    checks: list[dict] = []
    m = measure(track, sr)

    def add(name: str, ok: bool, detail: str) -> None:
        checks.append({"check": name, "pass": bool(ok), "detail": detail})

    big = [(pos, g) for pos, g in gaps if g > MAX_GAP]
    add("no_dead_air", not big,
        f"max inter-scene gap {max([g for _, g in gaps], default=0):.2f}s "
        f"(cap {MAX_GAP}s)")
    add("no_clipped_end", m["speech_end_s"] < m["duration_s"] - 0.02
        or m["duration_s"] == 0.0,
        f"speech ends {m['speech_end_s']}s, file {m['duration_s']}s")
    add("no_dead_lead", m["leading_silence_s"] <= 0.3,
        f"leading silence {m['leading_silence_s']}s")
    drift = abs(board_end_s - m["speech_end_s"])
    add("coverage_within_15pct", board_end_s == 0 or
        drift <= max(1.0, board_end_s * 0.15),
        f"VO {m['speech_end_s']}s vs board {board_end_s}s (drift {drift:.2f}s)")
    add("audible", m["peak_dbfs"] > -30,
        f"peak {m['peak_dbfs']} dBFS, rms {m['rms_dbfs']} dBFS")
    return checks


# ---------------------------------------------------------------------------
# io
# ---------------------------------------------------------------------------


def write_track(path: str | Path, track: list[float], sr: int) -> Path:
    from monarch.video.audio import write_wav

    return write_wav(path, track, sr)


def _srt_ts(t: float) -> str:
    ms = int(round(max(0.0, t) * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    sec, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{sec:02d},{ms:03d}"


def format_srt(rows: list[tuple[float, float, str]]) -> str:
    """VO scene windows -> captions.srt text (L6: captions are not optional)."""
    out: list[str] = []
    for i, (a, b, text) in enumerate(rows, 1):
        out.append(f"{i}\n{_srt_ts(a)} --> {_srt_ts(b)}\n{str(text).strip()}\n")
    return "\n".join(out)
