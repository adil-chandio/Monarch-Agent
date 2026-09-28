"""RENDER MEMORY tests - the Einstein-session laws, wired and measured.

docs/RENDER_MEMORY.md: stranded-word guards (law 1), VAD + boundary +
gap checks (law 2), warm BGM (law 3), broadcast polish (law 1.6),
measured peaks / frame-1 audible (law 3.5/3.4), complete-sentence
composer (law 1.1), edit-verify discipline (law 8).
"""

from __future__ import annotations

import json
import math
import random
from pathlib import Path

import pytest

from monarch.cli import main
from monarch.core.words import count_words
from monarch.video.audit import audit_dir
from monarch.video.director import _compose_line, plan_storyboard
from monarch.video.mix import mix, warm_bed
from monarch.video.pipeline import make_video
from monarch.video.voiceover import (build_voiceover, polish_chain,
                                     vad_segments, vo_lint)


def _tone(freq: float, seconds: float, sr: int, amp: float = 0.3):
    return [amp * math.sin(2 * math.pi * freq * (i / sr))
            for i in range(int(seconds * sr))]


# ---------------------------------------------------------------------------
# law 1: stranded-word plague
# ---------------------------------------------------------------------------


def test_vo_lint_catches_all_four_misses():
    rows = [
        {"vo_line": "aap kitne bhi successful —"},            # strand mark
        {"vo_line": "aur phir ho"},                            # dup 'ho'? no
        {"vo_line": "the file sat unopened and the"},          # mid-sentence
        {"vo_line": "nau guna 90 ban gaya."},                  # digits
    ]
    issues = vo_lint(rows)
    kinds = {i["kind"] for i in issues}
    assert "strand_mark" in kinds
    assert "mid_sentence_end" in kinds
    assert "digits" in kinds


def test_vo_lint_dup_seam_word():
    rows = [{"vo_line": "he kept the file."}, {"vo_line": "file burned down."}]
    issues = vo_lint(rows)
    assert any(i["kind"] == "dup_seam_word" for i in issues)


def test_vo_lint_clean_rows_pass():
    rows = [{"vo_line": "the first file burned today."},
            {"vo_line": "one page survived the fire."}]
    hard = [i for i in vo_lint(rows) if i["kind"] != "digits"]
    assert hard == []


def test_composer_complete_sentences_all_roles():
    for role in ("hook", "tease", "payoff", "value-debt", "silence-sting",
                 "payoff+cua"):
        for n in (6, 7, 8, 9):
            line = _compose_line(role, "tape", n, random.Random(5))
            assert count_words(line) == n
            assert line[-1] in ".!?"


def test_board_lines_end_with_terminal():
    sb = plan_storyboard("the vault nobody could open", length=10.5, seed=5)
    for row in sb.board():
        assert row["vo_line"][-1] in ".!?"
        assert count_words(row["vo_line"]) == 7


# ---------------------------------------------------------------------------
# law 2: VAD + boundary + gap budget
# ---------------------------------------------------------------------------


def test_vad_segments_find_speech_islands():
    sr = 24000
    audio = ([0.0] * int(0.5 * sr) + _tone(220, 0.8, sr)
             + [0.0] * int(0.4 * sr) + _tone(220, 0.6, sr)
             + [0.0] * int(0.3 * sr))
    segs = vad_segments(audio, sr)
    assert len(segs) == 2
    assert segs[0]["start"] == pytest.approx(0.5, abs=0.06)
    assert segs[-1]["end"] == pytest.approx(2.3, abs=0.08)


def test_vad_merge_short_gaps():
    sr = 24000
    audio = (_tone(220, 0.5, sr) + [0.0] * int(0.06 * sr)
             + _tone(220, 0.5, sr))
    segs = vad_segments(audio, sr)
    assert len(segs) == 1                    # 0.06s gap merged (< 0.12s)


def test_boundary_silence_check_flags_stranded():
    sr = 24000
    # clip ends with 0.9s of trailing silence -> boundary silence > 0.65s
    track = _tone(220, 1.0, sr) + [0.0] * int(0.9 * sr) + _tone(220, 1.0, sr)
    from monarch.video.voiceover import boundary_silences
    worst = max(boundary_silences(track, sr, [2.0]))
    assert worst > 0.65


def test_qc_track_carries_memory_checks():
    scenes = [{"id": 1, "vo_line": "the file sat unopened today.",
               "t_start": 0.0, "t_end": 3.0, "sfx": ""}]
    vo = build_voiceover(scenes, backend="mumble", sr=24000, seed=1)
    checks = {c["check"] for c in vo["qc"]}
    assert "gap_budget" in checks
    assert "boundary_silence" in checks
    assert "vo_lint_digits" in checks
    assert all(c["pass"] for c in vo["qc"])


# ---------------------------------------------------------------------------
# law 1.6 + 3.5: broadcast polish + peak band
# ---------------------------------------------------------------------------


def test_polish_chain_cuts_rumble_keeps_voice():
    sr = 24000
    rumble = _tone(45, 1.0, sr, amp=0.5)
    voice = _tone(500, 1.0, sr, amp=0.5)
    p_rumble = polish_chain(rumble, sr)
    p_voice = polish_chain(voice, sr)
    r_before = (sum(v * v for v in rumble) / len(rumble)) ** 0.5
    r_after = (sum(v * v for v in p_rumble) / len(p_rumble)) ** 0.5
    v_before = (sum(v * v for v in voice) / len(voice)) ** 0.5
    v_after = (sum(v * v for v in p_voice) / len(p_voice)) ** 0.5
    assert r_after / r_before < 0.5          # 55 Hz rumble cut works
    assert v_after / v_before > 0.6          # voice body survives


def test_polish_chain_peak_in_law_band():
    sr = 24000
    hot = [0.95 * math.sin(2 * math.pi * 300 * (i / sr))
           for i in range(sr)]
    out = polish_chain(hot, sr)
    assert max(abs(v) for v in out) <= 0.82


# ---------------------------------------------------------------------------
# law 3: warm BGM
# ---------------------------------------------------------------------------


def test_warm_bed_audible_from_frame_1():
    sr = 24000
    bed = warm_bed(6.0, sr, seed=3)
    def rms(seg):
        return (sum(v * v for v in seg) / max(1, len(seg))) ** 0.5
    intro = rms(bed[:int(0.4 * sr)])
    body = rms(bed[int(1.0 * sr):int(3.0 * sr)])
    assert intro > 0.3 * body                # attack <= 0.4s (miss #7)
    assert intro > 0.0


def test_warm_bed_one_gentle_build():
    sr = 24000
    bed = warm_bed(12.0, sr, seed=2)
    def rms(a, b):
        seg = bed[int(a * sr):int(b * sr)]
        return (sum(v * v for v in seg) / max(1, len(seg))) ** 0.5
    assert rms(10.0, 12.0) > rms(1.0, 3.0)   # build into the CTA window


def test_warm_mix_peak_in_law_band():
    sr = 24000
    master, rep = mix(duration_s=2.0, vo=[0.2] * int(1.5 * sr), sr=sr,
                      seed=4, music_mood="warm")
    assert max(abs(v) for v in master) <= 0.82
    assert rep.mood == "warm"
    assert "warm" in rep.summary()


def test_make_video_mood_maps_by_genre(tmp_path):
    d1 = tmp_path / "a"
    m1 = make_video("the lost tape", d1, length=10.5, fps=1, seed=3,
                    voice_backend="mumble", do_mix=True, genre="mystery")
    assert "MOOD tension" in m1["mix"]["report"]
    d2 = tmp_path / "b"
    m2 = make_video("study in ten minutes", d2, length=10.5, fps=1, seed=3,
                    voice_backend="mumble", do_mix=True, genre="tutorial")
    assert "MOOD warm" in m2["mix"]["report"]


# ---------------------------------------------------------------------------
# law 3.5/3.4: measured audit on real files
# ---------------------------------------------------------------------------


def test_audit_measures_mix_audio(tmp_path):
    d = tmp_path / "m"
    make_video("the lost tape", d, length=10.5, fps=1, seed=6,
               voice_backend="mumble", do_mix=True, genre="tutorial")
    rep = audit_dir(d)
    assert "mix_peak" in rep.scores
    assert rep.scores["mix_peak"] <= 0.85
    assert rep.scores["intro_rms"] > 0.03    # frame-1 law holds end-to-end


def test_audit_flags_hot_master(tmp_path):
    import wave as w
    d = tmp_path / "hot"
    d.mkdir()
    (d / "manifest.json").write_text(json.dumps({"scenes": []}),
                                     encoding="utf-8")
    with w.open(str(d / "master_mix.wav"), "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(8000)
        f.writeframes(b"\x7f\x7f" * 16000)   # ~1.0 amplitude square-ish
    rep = audit_dir(d)
    assert any("peak over the render-memory band" in f.title
               for f in rep.findings)
