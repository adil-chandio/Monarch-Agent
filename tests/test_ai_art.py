"""AI-ART fusion stage: prompt plan -> fail-closed keyframes -> render.

Laws under test: prompts English-only + no-text clause + no desi words
(V6 M4), zoom cap 1.08 (M10), fail-closed missing keyframes, drift
<= 0.5s (L13), deterministic plans, CLI ai-plan + make-video flag.
"""

from __future__ import annotations

import json
import math

import pytest
from PIL import Image

from monarch.cli import main
from monarch.video.ai_art import (DEFAULT_ARC, ROLE_ARCS, ZOOM_CAP,
                                  frame_plan, prompt_plan, render_ai_short,
                                  require_keyframes, write_prompt_plan)
from monarch.video.audio import write_wav

BOARD = {
    "title": "POLAR IS FAKE KING",
    "maths": {},
    "scenes": [
        {"t_start": 0.0, "t_end": 3.43, "retention_role": "hook",
         "visual": "one focal hook visual on a fake king, high contrast"},
        {"t_start": 3.43, "t_end": 6.59, "retention_role": "silence-sting",
         "visual": "one focal silence-sting visual on a glowing crown"},
        {"t_start": 6.59, "t_end": 9.77, "retention_role": "payoff+cua",
         "visual": "one focal payoff visual of the crowned stickman"},
    ],
}
AUDIO_S = 11.17


def test_prompt_plan_shape_and_laws():
    plan = prompt_plan(BOARD)
    assert len(plan) == 9 and [p["key"] for p in plan] == list(range(1, 10))
    roles = [p["role"] for p in plan]
    assert roles == (["hook"] * 3 + ["silence-sting"] * 3 + ["payoff+cua"] * 3)
    for p in plan:
        assert p["prompt"].endswith("no watermark")        # miss-#2 clause
        assert p["prompt"].isascii()                       # M4 English-only
        assert "single focal subject" in p["prompt"]       # M3
        assert p["prompt"].count("stickman") >= 1          # operator style
    assert set(ROLE_ARCS) >= {"hook", "silence-sting", "payoff+cua"}
    assert len(DEFAULT_ARC) == 3


def test_prompt_plan_deterministic(tmp_path):
    a = prompt_plan(BOARD)
    b = prompt_plan(BOARD)
    assert a == b
    pa = write_prompt_plan(a, tmp_path / "plan.json")
    assert json.loads(pa.read_text(encoding="utf-8")) == a


def test_prompt_plan_desi_words_fail_closed():
    bad = {"scenes": [{"t_start": 0, "t_end": 1, "retention_role": "hook",
                       "visual": "bilkul jhakaas king scene"}]}
    with pytest.raises(ValueError, match="M4"):
        prompt_plan(bad)


def test_frame_plan_sums_to_audio_truth():
    counts = frame_plan(BOARD, AUDIO_S, fps=10)
    assert sum(counts) == round(AUDIO_S * 10) == 112
    assert all(c >= 2 for c in counts)
    assert counts[-1] == max(counts)          # end-screen tail holds last
    assert counts == frame_plan(BOARD, AUDIO_S, fps=10)


def test_frame_plan_too_short_fail_closed():
    with pytest.raises(ValueError):
        frame_plan(BOARD, 0.3, fps=10)


def test_require_keyframes_fail_closed(tmp_path):
    with pytest.raises(ValueError, match="key1.png") as e:
        require_keyframes(tmp_path, 9)
    assert "ai_prompts.json" in str(e.value)
    (tmp_path / "key1.png").write_bytes(b"x")
    with pytest.raises(ValueError, match="key2.png"):
        require_keyframes(tmp_path, 9)


def test_render_zoom_cap_m10(tmp_path):
    with pytest.raises(ValueError, match="M10"):
        render_ai_short(tmp_path, tmp_path / "x.wav", tmp_path / "o.mp4",
                        BOARD, zoom=ZOOM_CAP + 0.01)


def _tiny_frames(d, n=3, w=216, h=384):
    d.mkdir(parents=True, exist_ok=True)
    for i in range(1, n + 1):
        img = Image.new("RGB", (w, h), (6, 6, 10))
        for y in range(0, h, 16):
            for x in range(0, w, 16):
                img.putpixel((x, y), (240, 240, 240))
        img.save(d / f"key{i}.png")


def _tone(path, sec=0.8, sr=8000):
    samples = [0.3 * math.sin(2 * math.pi * 440 * i / sr)
               for i in range(int(sec * sr))]
    return write_wav(path, samples, sr=sr)


def test_render_ai_short_tiny_e2e(tmp_path):
    frames = tmp_path / "ai_frames"
    _tiny_frames(frames, 3)
    wav = _tone(tmp_path / "master_mix.wav", 0.8)
    board = {"scenes": [{"t_start": 0.0, "t_end": 0.8,
                         "retention_role": "hook",
                         "visual": "one focal test visual of a lone king"}]}
    out = tmp_path / "ai_short.mp4"
    m = render_ai_short(frames, wav, out, board, ass=None, fps=10)
    assert out.is_file() and m["bytes"] > 0
    assert m["frames"] == sum(m["counts"]) == 8
    assert m["duration_ok"] and m["drift_s"] <= 0.5
    assert m["zoom_max"] == 1.05 and "miss-#2" in m["law_note"]
    assert (tmp_path / "ai_concat.txt").is_file()
    assert len(list(tmp_path.glob("ai_seg_*.mp4"))) == 3


def test_cli_ai_plan_pending_then_render(tmp_path, capsys):
    cli_board = {"scenes": [{"t_start": 0.0, "t_end": 0.8,
                             "retention_role": "hook",
                             "visual": "one focal test visual of a lone "
                                       "king"}]}
    (tmp_path / "board.json").write_text(json.dumps(cli_board),
                                         encoding="utf-8")
    _tone(tmp_path / "master_mix.wav", 0.8)
    rc = main(["ai-plan", str(tmp_path)])
    out = capsys.readouterr().out
    assert rc == 2 and "PENDING" in out and "key1.png" in out
    plan_p = tmp_path / "ai_prompts.json"
    assert plan_p.is_file() and len(json.loads(plan_p.read_text())) == 3
    _tiny_frames(tmp_path / "ai_frames", 3)
    rc2 = main(["ai-plan", str(tmp_path)])
    out2 = capsys.readouterr().out
    assert rc2 == 0 and "AI-ART RENDER" in out2 and "drift" in out2
    short = tmp_path / "ai_short.mp4"
    assert short.is_file() and short.stat().st_size > 0


def test_render_transition_laws(tmp_path):
    frames = tmp_path / "ai_frames"
    _tiny_frames(frames, 3)
    wav = _tone(tmp_path / "master_mix.wav", 0.8)
    board = {"scenes": [{"t_start": 0.0, "t_end": 0.8,
                         "retention_role": "hook",
                         "visual": "one focal test visual of a lone king"}]}
    with pytest.raises(ValueError, match="XFADE_SET"):
        render_ai_short(frames, wav, tmp_path / "o.mp4", board,
                        transition="hyperjump")
    m = render_ai_short(frames, wav, tmp_path / "none.mp4", board,
                        transition="none")
    assert (tmp_path / "none.mp4").is_file() and m["transition"] == "none"
    m2 = render_ai_short(frames, wav, tmp_path / "morph.mp4", board,
                         transition="zoomin")
    assert m2["transition"] == "zoomin" and m2["duration_ok"]
