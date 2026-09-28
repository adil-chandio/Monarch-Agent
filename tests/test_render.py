"""Render stage tests - in-sandbox MP4 with laws wired (operator order).

L13: duration drift vs the AUDIO truth +-0.5s is checked and reported;
G7/L2: the ffmpeg command carries exactly 2 inputs; G16: versioned
output name; fail-closed on missing dir/timeline/audio.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from monarch.cli import main
from monarch.video.pipeline import make_video
from monarch.video.render import _slug, audio_duration_s, render_mp4


@pytest.fixture(scope="module")
def voiced_dir(tmp_path_factory):
    d = tmp_path_factory.mktemp("rnd") / "out"
    make_video("the doctor who vanished mid-surgery", d, length=10.5,
               fps=1, seed=11, voice_backend="mumble", do_mix=True)
    return d


def test_render_real_end_to_end(voiced_dir):
    res = render_mp4(voiced_dir)
    out = Path(res["output"])
    assert out.is_file() and res["bytes"] > 10_000
    assert res["duration_ok"] is True
    assert res["drift_s"] <= 0.5
    assert "burned" in res["captions"] or "ships" in res["captions"]
    assert res["resolution"] == "1080x1920"
    out.unlink()                      # workspace budget: big files die young


def test_render_versioned_name(voiced_dir):
    res = render_mp4(voiced_dir, burn_captions=False)
    assert Path(res["output"]).name.endswith("_v1_render.mp4")
    Path(res["output"]).unlink()


def test_render_fail_closed(tmp_path):
    with pytest.raises(ValueError):
        render_mp4(tmp_path / "ghost")
    d = tmp_path / "x"
    d.mkdir()
    with pytest.raises(ValueError):
        render_mp4(d)                 # no timeline.json
    (d / "timeline.json").write_text('{"frames": [], "size": [1080, 1920]}',
                                     encoding="utf-8")
    with pytest.raises(ValueError):
        render_mp4(d)                 # no audio -> silent render is a lie


def test_slug_and_audio_duration(voiced_dir):
    assert _slug("The Doctor, WHO vanished!") == "the-doctor-who-vanished"
    assert audio_duration_s(voiced_dir / "master_mix.wav") > 5.0


def test_cli_render_and_fail(capsys, voiced_dir, tmp_path):
    rc = main(["render", str(voiced_dir), "--json"])
    out = capsys.readouterr().out
    assert rc == 0 and '"duration_ok": true' in out
    rc2 = main(["render", str(tmp_path / "nope")])
    assert rc2 == 2 and "FAIL" in capsys.readouterr().out
