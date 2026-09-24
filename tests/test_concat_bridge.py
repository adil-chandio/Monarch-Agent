"""Concat bridge tests - Monarch truth -> jub0t/Concat agent recipe.

The bridge emits JSONL for `concat-cli api` from OUR artifacts. Laws
under test: every method/op against the REAL v0.2.4 API surface,
board/timeline stays the single truth (G14), versioned export (G16),
import-once/place-many, fail-closed on missing artifacts, determinism.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from monarch.cli import main
from monarch.video.concat_bridge import METHODS, OPS, emit_concat_plan
from monarch.video.pipeline import make_video


@pytest.fixture(scope="module")
def video_dir(tmp_path_factory):
    d = tmp_path_factory.mktemp("cb") / "out"
    make_video("the doctor who vanished mid-surgery", d, length=10.5, fps=1,
               seed=11, voice_backend="mumble", do_mix=True)
    return d


def _lines(d):
    return [json.loads(x) for x in
            (d / "concat_recipe.jsonl").read_text(encoding="utf-8").splitlines()]


def test_plan_emits_recipe_on_real_dir(video_dir):
    plan = emit_concat_plan(video_dir)
    p = Path(plan["recipe"])
    assert p.is_file()
    lines = _lines(video_dir)
    assert lines[0]["method"] == "project.create"
    assert lines[-1]["method"] == "export.run"
    assert plan["commands"] == len(lines)


def test_every_method_and_op_is_real_api(video_dir):
    for r in _lines(video_dir):
        assert r["method"] in METHODS
        if r["method"] == "edit.apply":
            assert r["params"]["command"]["op"] in OPS


def test_clip_starts_come_from_our_timeline(video_dir):
    tl = json.loads((video_dir / "timeline.json").read_text(encoding="utf-8"))
    ours = [round(f["t_start"], 3) for f in tl["frames"]]
    starts = [r["params"]["command"]["start"] for r in _lines(video_dir)
              if r["method"] == "edit.apply"
              and r["params"]["command"] == {
                  **r["params"]["command"], **{}}  # keep type checkers calm
              and r["params"]["command"].get("trackId") == "T1"]
    assert starts == ours                    # board = truth, editor obeys


def test_text_clips_are_lower_thirds_per_scene(video_dir):
    text = [r["params"]["command"] for r in _lines(video_dir)
            if r["method"] == "edit.apply"
            and r["params"]["command"]["op"] == "addTextClip"]
    board = json.loads((video_dir / "board.json").read_text(encoding="utf-8"))
    scenes = board["scenes"]
    assert len(text) == len(scenes)
    for cmd, s in zip(text, scenes):
        assert cmd["style"]["content"] == s["vo_line"]
        assert cmd["offsetY"] == -0.55       # lower third, safe zone
        assert abs(cmd["duration"] - (s["t_end"] - s["t_start"])) < 0.01


def test_export_is_versioned_and_vertical(video_dir):
    last = _lines(video_dir)[-1]["params"]
    assert last["output"].endswith("_v1_final.mp4")   # G16 cache law
    assert (last["width"], last["height"]) == (1080, 1920)
    assert last["codec"] == "h264"


def test_sfx_import_once_place_many(video_dir):
    lines = _lines(video_dir)
    imports = [r["params"]["file"] for r in lines
               if r["method"] == "media.import" and "/sfx/" in r["params"]["file"]]
    assert len(imports) == len(set(imports))          # no duplicate imports
    sfx_clips = [r["params"]["command"] for r in lines
                 if r["method"] == "edit.apply"
                 and r["params"]["command"].get("trackId") == "T3"]
    assert sfx_clips                                  # placed at clip starts


def test_missing_timeline_fails_closed(tmp_path):
    d = tmp_path / "empty"
    d.mkdir()
    with pytest.raises(ValueError):
        emit_concat_plan(d)
    with pytest.raises(ValueError):
        emit_concat_plan(tmp_path / "ghost")          # missing dir too


def test_deterministic_output(video_dir):
    a = emit_concat_plan(video_dir, out=video_dir / "r1.jsonl")
    b = emit_concat_plan(video_dir, out=video_dir / "r2.jsonl")
    assert (video_dir / "r1.jsonl").read_bytes() == \
        (video_dir / "r2.jsonl").read_bytes()
    assert a["commands"] == b["commands"]


def test_cli_happy_and_fail_closed(capsys, video_dir, tmp_path):
    rc = main(["concat-plan", str(video_dir), "--json"])
    out = capsys.readouterr().out
    assert rc == 0 and json.loads(out)["commands"] > 0
    rc2 = main(["concat-plan", str(tmp_path / "nope")])
    out2 = capsys.readouterr().out
    assert rc2 == 2 and "FAIL" in out2
