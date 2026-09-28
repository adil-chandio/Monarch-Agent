"""TABAAHI wave tests — humanize, voiceover, story, mix, parallax, CLI.

The laws under test (the wave's whole point):
* L1: VO is the skeleton — timing from measured speech, never file length.
* No cut lines: sentence chunks + glue caps (0.5/0.3/0.15, max 0.6).
* No abrupt starts: lead-in + crossfade.
* VO wins the mix: music ducks, master limited, levels measured.
* Scripts read human: AI-tells die, grammar survives the strip.
"""

from __future__ import annotations

import json
import math
import wave
from pathlib import Path

import pytest

from monarch.cli import main
from monarch.video import audio, mix as mix_bus, voiceover
from monarch.video.humanize import humanize, score_text, strip_hits
from monarch.video.story import ear_check, plan_arc, prosody_note


# ---------------------------------------------------------------------------
# humanize
# ---------------------------------------------------------------------------


def test_score_counts_ai_signs():
    signs, hits, notes = score_text(
        "Let's delve into this game-changer and unravel the secrets.")
    assert signs > 0
    assert any("delve" in h[0].lower() for h in hits)


def test_clean_text_scores_zero():
    signs, hits, notes = score_text(
        "The file sat unopened for fifty years. Nobody signed the last page.")
    assert signs == 0.0
    assert hits == []


def test_strip_removes_opener_and_connective():
    out, stripped = strip_hits(
        "In today's world, we dig deep. Moreover, the case grew colder.")
    assert "In today's world" not in out
    assert "Moreover" not in out
    assert any("opener" in s for s in stripped)
    assert any("connective" in s for s in stripped)


def test_word_fixes_keep_grammar():
    out, _ = strip_hits("Historians utilized files to delve into the tapestry.")
    assert "used" in out            # utilized -> used (inflection kept)
    assert "dig into" in out        # delve into -> dig into
    assert "story" in out           # tapestry -> story (replaced, not deleted)
    assert "the tapestry" not in out


def test_no_article_orphans_after_strip():
    out, _ = strip_hits("It was a game-changer, honestly.")
    assert "a ," not in out
    assert " a." not in out


def test_tidy_recapitalizes_sentences():
    out, _ = strip_hits("All things considered, the file stayed shut.")
    assert out.startswith("The file")
    assert out[0].isupper()


def test_humanize_gate_fail_reports():
    raw = ("Let's delve into this. Moreover, it's a game-changer. "
           "In conclusion, brace yourself as we embark on a journey through "
           "the ever-evolving bustling landscape. It's important to note that "
           "cutting-edge seamless tools elevate your potential exponentially. "
           "At the end of the day, the verdict is still unknown. ")
    clean, rep = humanize(raw)
    assert rep.signs_before > rep.signs_after
    assert rep.final_words != rep.original_words
    assert rep.summary()


def test_humanize_empty_is_clean():
    clean, rep = humanize("")
    assert clean == ""
    assert rep.summary().startswith("CLEAN")


def test_not_just_shape_counted_not_deleted():
    signs, hits, _ = score_text("It's not just a file — it's a confession.")
    assert any("not-just" in h[1] for h in hits)


# ---------------------------------------------------------------------------
# story engine
# ---------------------------------------------------------------------------


def test_plan_arc_partial_payoff_carries_rehook():
    plan = plan_arc(["hook", "tease", "payoff", "value-debt",
                     "silence-sting", "payoff+cua"])
    assert plan[0]["beat"].startswith("COLD OPEN")
    assert plan[2]["partial"] is True
    assert plan[2]["rehook"]            # the next question enters early
    assert not plan[3]["partial"]


def test_prosody_direction_on_every_scene():
    plan = plan_arc(["hook", "payoff"])
    assert plan[0]["prosody"].startswith("[")
    assert plan[1]["prosody"].startswith("[")


def test_ear_check_flags_uniform_rhythm():
    text = ("The file sat. The file stayed. The page was signed. "
            "The room was cleared. The case was closed. The tape ran out. "
            "The night got long. The man went west.")
    notes = ear_check(text)
    assert any("uniform" in n or "contractions" in n for n in notes)


def test_ear_check_flags_long_sentences():
    long = ("The investigator walked back to the car in the pouring rain "
            "while the radio kept repeating the same three words over and "
            "over again until the signal finally dissolved into static.")
    assert any("over 24 words" in n for n in ear_check(long))


# ---------------------------------------------------------------------------
# voiceover — the audio-first laws
# ---------------------------------------------------------------------------


def test_chunks_cut_at_sentences_never_mid_clause():
    chunks = voiceover.sentence_chunks(
        "The file sat unopened for fifty years. What was inside? Nobody knew.")
    assert chunks == ["The file sat unopened for fifty years.",
                      "What was inside?", "Nobody knew."]


def test_chunks_respect_max_chars_via_clauses():
    long = ("The investigator walked back to the car, the tape still running, "
            "the rain drowning every word, the case growing colder by the "
            "minute, and the city asleep.")
    chunks = voiceover.sentence_chunks(long, max_chars=80)
    assert all(len(c) <= 80 for c in chunks)
    assert len(chunks) >= 2
    assert chunks[0].rstrip().endswith(",")  # clause boundary, never mid-word


def test_next_gap_caps_by_punctuation():
    assert voiceover.next_gap("The end.") == pytest.approx(0.5)
    assert voiceover.next_gap("Wait,") == pytest.approx(0.3)
    assert voiceover.next_gap("and then") == pytest.approx(0.15)


def test_measure_speech_end_from_envelope_not_file_length():
    sr = 22050
    tone = [0.5 * math.sin(2 * math.pi * 220 * i / sr) for i in range(sr)]
    padded = tone + [0.0] * (3 * sr)          # 1s speech + 3s TTS padding
    m = voiceover.measure(padded, sr)
    assert m["speech_end_s"] < 1.3
    assert m["duration_s"] == pytest.approx(4.0, abs=0.01)
    assert m["leading_silence_s"] < 0.1


def test_trim_tail_keeps_law_tail():
    sr = 22050
    tone = [0.5] * sr
    trimmed = voiceover.trim_tail_silence(tone + [0.0] * (2 * sr), sr)
    assert len(trimmed) <= sr + int(voiceover.TAIL * sr) + sr // 100


def test_glue_has_lead_in_and_tail():
    sr = 8000
    a = [0.4] * sr
    out = voiceover.glue_chunks([a, a], sr)
    assert out[: int(voiceover.LEAD_IN * sr)] == [0.0] * int(voiceover.LEAD_IN * sr)
    assert out[-1] == 0.0                      # tail silence, no clip


def test_build_voiceover_scenes_gaps_and_qc():
    scenes = [{"id": i, "vo_line": ln, "t_start": (i - 1) * 3.0,
               "t_end": i * 3.0, "sfx": "", "role": "", "driver": "",
               "match_cut": ""}
              for i, ln in enumerate(
                  ["The file sat unopened for fifty years",
                   "What was inside changed the whole case",
                   "Nobody signed the last page"], 1)]
    built = voiceover.build_voiceover(scenes, backend="mumble", sr=22050, seed=2)
    assert built["placeholder"] is True
    assert len(built["scenes"]) == 3
    starts = [r["start"] for r in built["scenes"]]
    assert starts[0] == 0.0
    assert starts[1] - built["scenes"][0]["end"] <= voiceover.MAX_GAP + 1e-9
    checks = {c["check"]: c["pass"] for c in built["qc"]}
    assert checks["no_dead_air"] is True
    assert checks["no_clipped_end"] is True
    assert checks["no_dead_lead"] is True
    assert checks["audible"] is True


def test_build_voiceover_empty_line_fails_closed():
    with pytest.raises(ValueError):
        voiceover.build_voiceover(
            [{"id": 1, "vo_line": "", "t_start": 0, "t_end": 1, "sfx": "",
              "role": "", "driver": "", "match_cut": ""}], backend="mumble")


def test_dir_backend_reads_scene_wavs(tmp_path):
    sr = 8000
    tone = [0.3 * math.sin(2 * math.pi * 300 * i / sr) for i in range(sr)]
    audio.write_wav(tmp_path / "scene_01.wav", tone, sr)
    got = voiceover._dir_backend(1, tmp_path, sr)
    assert len(got) == sr
    with pytest.raises(FileNotFoundError):
        voiceover._dir_backend(9, tmp_path, sr)


def test_write_and_read_wav_roundtrip_floats(tmp_path):
    sr = 8000
    samples = [0.5 * math.sin(2 * math.pi * 440 * i / sr) for i in range(sr)]
    p = audio.write_wav(tmp_path / "t.wav", samples, sr)
    back, sr2 = audio.read_wav(p)
    assert sr2 == sr
    assert abs(back[100] - samples[100]) < 1e-3   # floats, not raw ints


# ---------------------------------------------------------------------------
# mix bus
# ---------------------------------------------------------------------------


def test_music_bed_no_infinite_loop_on_fractional_duration():
    # regression: 13.132s * 22050 left a float fraction -> spin forever
    bed = mix_bus.music_bed(13.132, 22050, seed=0)
    assert len(bed) == math.ceil(13.132 * 22050)
    assert bed == mix_bus.music_bed(13.132, 22050, seed=0)   # deterministic


def test_room_tone_length():
    assert len(mix_bus.room_tone(1.5, 22050, seed=1)) == int(1.5 * 22050)


def test_duck_quiets_music_only_while_voice_speaks():
    sr = 8000
    music = [0.8] * (2 * sr)
    voice = [0.0] * sr + [0.6] * sr
    ducked = mix_bus.duck_under_voice(music, voice, sr)
    early = sum(abs(v) for v in ducked[: sr // 2]) / (sr // 2)
    late = sum(abs(v) for v in ducked[-sr // 2:]) / (sr // 2)
    assert early > late * 2          # music dips under speech
    assert late > 0                  # ...but never fully disappears


def test_mix_vo_wins_and_master_limited():
    sr = 8000
    vo = [0.5 * math.sin(2 * math.pi * 220 * i / sr) for i in range(sr)]
    board = [{"id": 1, "t_start": 0.0, "t_end": 1.0, "sfx": "hit"}]
    mixed, rep = mix_bus.mix(duration_s=1.2, vo=vo, sr=sr, board=board, seed=0)
    assert len(mixed) == int(1.2 * sr)
    assert rep.master_peak <= -0.1                      # limiter law
    assert rep.sfx_events == 1
    assert rep.vo_rms > -40


def test_mix_warns_unknown_sfx_and_empty_board():
    sr = 8000
    _, rep = mix_bus.mix(duration_s=0.5, vo=[], sr=sr,
                         board=[{"id": 1, "t_start": 0, "t_end": 0.5,
                                 "sfx": "laser"}], seed=0)
    assert rep.sfx_events == 0
    assert any("unknown sfx" in w for w in rep.warnings)
    _, rep2 = mix_bus.mix(duration_s=0.5, vo=[], sr=sr, board=[], seed=0)
    assert any("no SFX" in w for w in rep2.warnings)


def test_mix_rejects_bad_duration():
    with pytest.raises(ValueError):
        mix_bus.mix(duration_s=0, vo=[], sr=8000, board=[])


# ---------------------------------------------------------------------------
# engine parallax + pipeline wiring
# ---------------------------------------------------------------------------


def test_scene_geometry_and_fg_redraw():
    from monarch.video.engine import FrameSpec, draw_fg, render_frame, scene_geometry

    spec = FrameSpec(scene_id=2, headline="t", vo_line="hello world",
                     badge="02/18", driver="N1", role="tease",
                     progress=0.5, cohort="genz")
    geo = scene_geometry(spec, width=270, height=480)
    assert geo["focal"]["rects"] and geo["pill"]["lines"]
    base = render_frame(spec, width=270, height=480, include_fg=False)
    walled = render_frame(spec, width=270, height=480)
    assert bytes(base.px) != bytes(walled.px)        # fg really adds layers
    f2 = type(base)(270, 480, (0, 0, 0))
    draw_fg(f2, geo, dx=5, dy=-3)                    # offset redraw works
    assert bytes(f2.px) != bytes(base.px)


def test_make_video_with_voice_and_mix(tmp_path):
    from monarch.video.pipeline import make_video

    manifest = make_video("the vault nobody could open", tmp_path / "mv",
                          length=10.5, fps=2, seed=3,
                          animation="parallax", voice_backend="mumble",
                          do_mix=True)
    assert manifest["animation"] == "parallax"
    assert manifest["voice"]["placeholder"] is True
    assert manifest["voice"]["qc"][0]["check"] == "no_dead_air"
    assert manifest["mix"]["wav"] == "master_mix.wav"
    assert (tmp_path / "mv" / "vo" / "vo_track.wav").is_file()
    assert (tmp_path / "mv" / "master_mix.wav").is_file()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _run(capsys, *argv):
    rc = main(list(argv))
    out = capsys.readouterr().out
    return rc, out


def test_cli_humanize_strips_and_reports(capsys):
    rc, out = _run(capsys, "humanize",
                   "In today's world, let's delve into the tapestry of lies.")
    assert rc == 0
    assert "CLEAN" in out or "ROBOTIC" in out
    assert "dig into" in out


def test_cli_humanize_needs_text(capsys):
    rc, _ = _run(capsys, "humanize")
    assert rc == 2


def test_cli_voiceover_mumble_end_to_end(capsys, tmp_path):
    out_dir = tmp_path / "vo_out"
    rc, out = _run(capsys, "voiceover", "--topic", "the buried file",
                   "--backend", "mumble", "--out", str(out_dir), "--sr", "8000")
    assert rc == 0
    assert "VO READY" in out and "PLACEHOLDER" in out
    assert (out_dir / "vo_track.wav").is_file()
    assert (out_dir / "vo_scenes.json").is_file()


def test_cli_voiceover_rejects_bad_backend(capsys):
    rc, _ = _run(capsys, "voiceover", "--topic", "x", "--backend", "yodel")
    assert rc == 2


def test_cli_mix_reads_board_and_limits(capsys, tmp_path, monkeypatch):
    sr = 8000
    vo = [0.4 * math.sin(2 * math.pi * 200 * i / sr) for i in range(sr)]
    wav = tmp_path / "vo.wav"
    audio.write_wav(wav, vo, sr)
    board = {"scenes": [{"id": 1, "t_start": 0.0, "t_end": 0.6,
                         "sfx": "heartbeat"}]}
    bp = tmp_path / "board.json"
    bp.write_text(json.dumps(board), encoding="utf-8")
    rc, out = _run(capsys, "mix", "--vo", str(wav), "--duration", "1.2",
                   "--board", str(bp), "--out", str(tmp_path / "m.wav"))
    assert rc == 0
    assert "MIX READY" in out
    assert (tmp_path / "m.wav").is_file()


def test_cli_make_video_rejects_bad_animation(capsys, tmp_path, monkeypatch):
    rc, out = _run(capsys, "make-video", "--topic", "x",
                   "--animation", "bullet-time", "--out", str(tmp_path / "o"))
    assert rc == 2
