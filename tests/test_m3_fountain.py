"""M3_script integration — Fountain screenplay → gated scene board."""

import itertools
import json
import subprocess
import sys
from pathlib import Path

import pytest

from monarch.core.fountain import Screenplay
from monarch.core.gates import GateFail
from monarch.core.scene_math import compute_math
from monarch.core.state_machine import Run
from monarch.engine.project import Project
from monarch.pipelines.fountain import (
    ACTION,
    DIALOGUE,
    ScriptReport,
    beats_from_json,
    beats_from_lines,
    beats_from_screenplay,
    board_json,
    build_script,
    screenplay_from_json,
    screenplay_from_path,
    screenplay_from_text,
    split_visual,
    write_fountain,
)
from monarch.schemas import Channel, Scene

FIXTURE = Path(__file__).parent / "fixtures" / "ice_that_refused.fountain"


def fixture_report(*, sfx: str = "", **beat_kwargs) -> ScriptReport:
    sp = screenplay_from_path(FIXTURE)
    return build_script(
        beats_from_screenplay(sp, **beat_kwargs),
        60.0,
        sfx=sfx,
        title=sp.title_page.title,
        byline=sp.title_page.byline,
        source=sp.source,
    )


# --------------------------------------------------------------------- maths


def test_maths_line_is_the_law():
    m = compute_math(60, clip_s=3.5)
    assert (m.scenes, m.words_per_clip) == (18, 7)


def test_fixture_boards_exactly_18_x_7():
    report = fixture_report()
    assert len(report.scenes) == 18
    assert [s.word_count for s in report.scenes] == [7] * 18
    assert all(len(s.vo_line.split()) == 7 for s in report.scenes)
    assert report.unfit == []
    assert report.trimmed == []


def test_visual_never_counts_as_words():
    report = fixture_report()
    assert report.scenes[0].vo_line == "The ice refused to melt for years"
    assert report.scenes[0].visual == "cracked glacier face"
    assert report.scenes[0].match_cut == "cracked glacier face"
    assert "cracked glacier face" not in report.scenes[0].vo_line


def test_board_maths_is_consistent():
    report = fixture_report()
    scenes = report.scenes
    assert scenes[0].t_start == 0.0
    assert scenes[0].t_end == 2.5
    assert scenes[0].t_end - scenes[0].t_start <= 3.01  # open must force the watch
    assert report.scenes[1].t_start == 2.5
    for a, b in itertools.pairwise(scenes):
        assert a.t_end == b.t_start
        assert b.t_end > b.t_start
        assert round(b.t_end - b.t_start, 3) == round(7 / 2.2, 3)
    assert scenes[-1].t_end == report.board_s


def test_retention_jobs_and_sfx():
    report = fixture_report(sfx="sub-hit")
    assert report.scenes[0].retention_job == "hook"
    assert report.scenes[-1].retention_job == "payoff"
    assert {s.retention_job for s in report.scenes[1:-1]} == {"advance"}
    assert all(s.sfx == "sub-hit" for s in report.scenes)


def test_screenplay_lineage_survives():
    report = fixture_report()
    assert report.title == "The ice that refused to melt"
    assert report.byline == "Adil Chandio"
    assert [b.screen_scene for b in report.beats] == [1] * 3 + [2] * 3 + [3] * 3 + [4] * 3 + [5] * 3 + [6] * 3
    assert report.beats[0].kind == DIALOGUE
    assert report.beats[0].speaker == "VOICEOVER"
    assert report.beats[0].extension == "V.O."
    assert report.beats[0].slug == "EXT. GLACIER - DAY"
    assert report.beats[0].source_line > 0
    assert [b.number for b in report.beats] == list(range(1, 19))
    assert report.units[0][1].id == 1


# ----------------------------------------------------------------- gates


def test_trim_reported_never_hidden():
    beats = beats_from_lines(["one two three four five six seven eight nine"])
    report = build_script(beats, 30.0, gate=False, clip_s=4.0)
    assert report.scenes[0].word_count == report.maths.words_per_clip
    assert report.beats[0].fitted
    assert "trimmed" in report.beats[0].issues[0]
    assert "nine" not in report.scenes[0].vo_line


def test_too_short_beat_is_not_padded():
    beats = beats_from_lines(["icy water rose fast"] * 6)
    report = build_script(beats, 30.0, gate=False)
    assert len(report.unfit) == 6
    assert report.unfit[0].vo_line == "icy water rose fast"  # never padded
    assert "never pad" in report.unfit[0].issues[0]
    assert "needs work" in report.summary()
    with pytest.raises(GateFail):
        build_script(beats_from_lines(["icy water rose fast"] * 6), 30.0)


def test_wrong_beat_count_fails_closed():
    with pytest.raises(GateFail) as e:
        build_script(beats_from_lines(["alpha bravo charlie delta echo foxtrot golf"] * 5), 60.0)
    assert "maths needs 18" in str(e.value)


def test_gate_checks_visual_and_job():
    beats = beats_from_lines(["alpha bravo charlie delta echo foxtrot golf"] * 18)
    report = build_script(beats, 60.0, gate=False)
    report.scenes[1].visual = ""
    report.scenes[2].retention_job = ""
    with pytest.raises(GateFail) as e:
        from monarch.pipelines.fountain import assert_gated

        assert_gated(report)
    assert "no visual" in str(e.value)
    assert "no retention job" in str(e.value)


# ----------------------------------------------------------------- sources


def test_split_visual():
    assert split_visual("::cracked ice:: it moved") == ("cracked ice", "it moved")
    assert split_visual("plain words here") == ("", "plain words here")
    assert split_visual("::visual only::") == ("visual only", "")


def test_include_and_speaker_filters():
    text = """INT. CAVE - DAY

A stickman watches the water.

MARA
alpha bravo charlie delta echo foxtrot

JONAS
seven six five four three two one
"""
    sp = screenplay_from_text(text)
    both = beats_from_screenplay(sp)
    assert [b.speaker for b in both] == ["", "MARA", "JONAS"]
    assert both[0].kind == ACTION
    only_dialogue = beats_from_screenplay(sp, include=(DIALOGUE,))
    assert [b.speaker for b in only_dialogue] == ["MARA", "JONAS"]
    only_mara = beats_from_screenplay(sp, speaker="MARA")
    assert [b.speaker for b in only_mara] == ["MARA"]
    only_action = beats_from_screenplay(sp, include=(ACTION,))
    assert [b.kind for b in only_action] == [ACTION]


def test_visual_hint_fills_gaps():
    sp = screenplay_from_text("INT. CAVE - DAY\n\nMARA\nalpha bravo charlie delta echo foxtrot\n")
    beats = beats_from_screenplay(sp, visual_hint="stickman in a cave")
    assert beats[0].visual == "stickman in a cave"


def test_beats_from_json_and_lines():
    doc = {
        "beats": [
            {"text": "::ice shelf:: alpha bravo charlie delta echo foxtrot golf", "kind": "dialogue"},
            {"text": "juliet kilo lima mike november oscar papa", "visual": "river"},
        ]
    }
    beats = beats_from_json(doc)
    assert beats[0].visual == "ice shelf"
    assert beats[0].words == 7
    assert beats[1].visual == "river"
    assert len(beats_from_lines(["alpha bravo charlie delta echo foxtrot golf"])) == 1
    assert beats_from_lines(["", "   "]) == []


def test_json_roundtrip_of_screenplay():
    sp = screenplay_from_path(FIXTURE)
    again = screenplay_from_json(sp.to_dict())
    assert again.title_page.title == sp.title_page.title
    assert again.scene_headings == sp.scene_headings
    assert [e.text for e in again.elements] == [e.text for e in sp.elements]


def test_screenplay_from_json_rejects_bad_kind():
    with pytest.raises(ValueError):
        screenplay_from_json({"elements": [{"kind": "monologue", "text": "x"}]})


def test_missing_file_message():
    with pytest.raises(FileNotFoundError) as e:
        screenplay_from_path("nope/missing.fountain")
    assert "This is missing" in str(e.value)


def test_shipped_template_parses():
    """The template in monarch/scripts/ must stay valid Fountain."""
    template = Path(__file__).resolve().parents[1] / "monarch" / "scripts" / "_template.fountain"
    sp = screenplay_from_path(template)
    assert sp.counts()["scene_heading"] == 3
    beats = beats_from_screenplay(sp)
    assert len(beats) == 3
    assert beats[0].speaker == "VOICEOVER"
    assert beats[0].visual.startswith("<visual:")
    # the template is not a board: the maths gate is supposed to refuse it
    with pytest.raises(GateFail):
        build_script(beats, 60.0)


# ------------------------------------------------------------- board → .fountain


def test_write_fountain_roundtrips_the_board(tmp_path: Path):
    report = fixture_report()
    out = tmp_path / "board.fountain"
    out.write_text(
        write_fountain(report.scenes, title=report.title, author="Adil Chandio"),
        encoding="utf-8",
    )
    text = out.read_text(encoding="utf-8")
    assert "Title: The ice that refused to melt" in text
    sp = screenplay_from_path(out)
    again = build_script(beats_from_screenplay(sp), 60.0)
    assert [s.vo_line for s in again.scenes] == [s.vo_line for s in report.scenes]
    assert [s.word_count for s in again.scenes] == [s.word_count for s in report.scenes]
    assert [s.visual for s in again.scenes] == [s.visual for s in report.scenes]
    assert again.board_s == report.board_s


def test_write_fountain_uses_slugs():
    report = fixture_report()
    text = write_fountain(report.scenes, slugs=["INT. ONE - DAY"] * 18)
    assert "INT. ONE - DAY" in text
    assert "EXT. BEAT 01 - DAY" not in text


def test_board_json_is_scene_shaped():
    report = fixture_report()
    rows = json.loads(board_json(report.scenes))
    assert len(rows) == 18
    assert set(rows[0]) == {
        "id",
        "vo_line",
        "visual",
        "word_count",
        "t_start",
        "t_end",
        "retention_job",
        "match_cut",
        "sfx",
    }


# ------------------------------------------------------------- project + state


def test_project_binds_m3_board(tmp_path: Path):
    p = Project(channel=Channel(id="monarch", niche="edu"))
    report = p.m3_from_fountain(FIXTURE, 60.0, sfx="whoosh")
    assert len(p.scenes) == 18
    assert p.math.words_per_clip == 7
    assert p.screenplay is not None and p.screenplay["title_page"]["title"] == report.title
    assert p.fountain_source.endswith("ice_that_refused.fountain")
    assert all(s.sfx == "whoosh" for s in p.scenes)

    out = tmp_path / "project.json"
    p.dump(out)
    doc = json.loads(out.read_text(encoding="utf-8"))
    assert len(doc["scenes"]) == 18
    assert doc["screenplay"]["counts"]["scene_heading"] == 6
    back = Project.load(out)
    assert [s.vo_line for s in back.scenes] == [s.vo_line for s in p.scenes]
    assert back.screenplay == p.screenplay


def test_m3_state_waits_for_perfect_or_improve():
    r = Run(state="M3_script")
    assert r.wait_prompt() == "perfect | improve"
    with pytest.raises(PermissionError):
        r.advance("next")
    assert r.advance("improve") == "M3_script"  # improve rewrites, no state change
    assert r.advance("perfect") == "M4_character"


def test_m3_state_card():
    from monarch.pipelines.state_card import m3_card

    card = m3_card()
    assert card["state"] == "M3_script"
    assert card["wait"] == "perfect | improve"
    assert any("never pad" in row for row in card["law"])
    assert "STOP — WAIT: perfect | improve" in card["text"]


# ---------------------------------------------------------------------- CLI


def run_cli(*args: str, stdin: str | None = None):
    return subprocess.run(
        [sys.executable, "-m", "monarch", *args],
        cwd=Path(__file__).resolve().parents[1],
        input=stdin,
        capture_output=True,
        text=True,
        check=False,
    )


def test_cli_fountain_summary_and_json():
    r = run_cli("fountain", str(FIXTURE))
    assert r.returncode == 0
    assert "scenes: 6" in r.stdout
    r = run_cli("fountain", str(FIXTURE), "--json")
    doc = json.loads(r.stdout)
    assert doc["counts"]["dialogue"] == 18
    assert doc["title_page"]["author"] == "Adil Chandio"


def test_cli_screen_script_blocks_and_passes():
    r = run_cli("screen-script", str(FIXTURE), "--length", "short")
    assert r.returncode == 0
    assert "7 words/clip exact" in r.stdout
    assert "STOP — WAIT: perfect | improve" in r.stdout
    r = run_cli("screen-script", str(FIXTURE), "--length", "60")
    assert r.returncode == 0
    r = run_cli("screen-script", str(FIXTURE), "--length", "600")
    assert r.returncode == 2
    assert "FAIL" in r.stdout


def test_cli_screen_script_json_and_board_out(tmp_path: Path):
    board = tmp_path / "board.json"
    r = run_cli(
        "screen-script",
        str(FIXTURE),
        "--length",
        "short",
        "--json",
        "--board-out",
        str(board),
    )
    assert r.returncode == 0
    doc = json.loads(r.stdout)
    assert doc["maths"]["words_per_clip"] == 7
    assert len(doc["scenes"]) == 18
    rows = json.loads(board.read_text(encoding="utf-8"))
    assert rows[0]["vo_line"] == doc["scenes"][0]["vo_line"]
    assert [row["word_count"] for row in rows] == [7] * 18


def test_cli_screen_script_accepts_board_json(tmp_path: Path):
    board = tmp_path / "board.json"
    first = run_cli("screen-script", str(FIXTURE), "--board-out", str(board))
    assert first.returncode == 0
    rows = json.loads(board.read_text(encoding="utf-8"))
    r = run_cli("screen-script", str(board), "--length", "short", "--json")
    assert r.returncode == 0
    doc = json.loads(r.stdout)
    assert [s["vo_line"] for s in doc["scenes"]] == [row["vo_line"] for row in rows]
    assert [s["word_count"] for s in doc["scenes"]] == [7] * 18


def test_cli_fountain_reads_stdin():
    r = run_cli("fountain", stdin="INT. CAVE - DAY\n\nAction here.\n")
    assert r.returncode == 0
    assert "scenes: 1" in r.stdout


def test_cli_screen_script_from_stdin():
    text = FIXTURE.read_text(encoding="utf-8")
    r = run_cli("screen-script", "--length", "short", stdin=text)
    assert r.returncode == 0
    assert "18 scenes" in r.stdout


def test_cli_screen_script_needs_beats():
    text = "INT. CAVE - DAY\n\nA stickman watches the water.\n"
    r = run_cli("screen-script", "--length", "short", "--only", "dialogue", stdin=text)
    assert r.returncode == 2
    assert "no VO beats" in r.stdout
    # an action-only screenplay is speakable, but it still has to pass the maths
    r = run_cli("screen-script", "--length", "short", stdin=text)
    assert r.returncode == 2
    assert "maths needs 18" in r.stdout


def test_cli_script_fountain_roundtrip(tmp_path: Path):
    board = tmp_path / "board.json"
    run_cli("screen-script", str(FIXTURE), "--board-out", str(board))
    out = tmp_path / "out.fountain"
    r = run_cli(
        "script-fountain",
        str(board),
        "--out",
        str(out),
        "--title",
        "The ice that refused to melt",
        "--author",
        "Adil Chandio",
    )
    assert r.returncode == 0
    assert "wrote" in r.stdout
    again = screenplay_from_path(out)
    assert again.title_page.title == "The ice that refused to melt"
    assert again.counts()[DIALOGUE] == 18


def test_cli_script_fountain_from_report(tmp_path: Path):
    r = run_cli("screen-script", str(FIXTURE), "--json")
    out = tmp_path / "out.fountain"
    r = run_cli("script-fountain", "--out", str(out), stdin=r.stdout)
    assert r.returncode == 0
    assert len(screenplay_from_path(out).scenes) == 18


def test_cli_m3_card():
    r = run_cli("m3")
    assert r.returncode == 0
    assert "M3_script" in r.stdout
    assert "perfect | improve" in r.stdout
    r = run_cli("m3", "--json")
    assert json.loads(r.stdout)["wait"] == "perfect | improve"


def test_cli_reports_missing_file():
    r = run_cli("fountain", "tests/fixtures/nope.fountain")
    assert r.returncode == 2
    assert "This is missing" in r.stdout


# ------------------------------------------------------------------ safety net


def test_m3_never_touches_render_or_voice():
    """M3 produces a board only — no render, no VO, no haan bypass."""
    import monarch.pipelines.fountain as pipe

    report = fixture_report()
    assert isinstance(report, ScriptReport)
    assert isinstance(report.scenes[0], Scene)
    source = inspect_source(pipe)
    for forbidden in ("require_haan", "generate_speech", "ffmpeg", "subprocess"):
        assert forbidden not in source


def inspect_source(module) -> str:
    import inspect

    return inspect.getsource(module)


def test_screenplay_dataclass_is_public():
    from monarch import Screenplay as Public

    assert Public is Screenplay
    assert ACTION == "action"
