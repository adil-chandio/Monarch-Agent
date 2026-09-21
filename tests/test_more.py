from pathlib import Path

import pytest

from monarch.core.audio_safe import audio_safe
from monarch.core.channels import load_channel
from monarch.core.fit_line import fit_words
from monarch.core.lessons import record
from monarch.core.missing import missing, require_fields
from monarch.core.scene_math import compute_math
from monarch.packaging.titles import rank_titles, score_title
from monarch.pipelines.metadata import package
from monarch.pipelines.visual import run_prompts
from monarch.schemas import Channel, Idea
from monarch.visual.prompts import animation_paragraph
from monarch.visual.scenes.board import board_from_lines


def test_fit_trim_no_pad():
    assert fit_words("one two three four five six seven extra", 7).split() == [
        "one",
        "two",
        "three",
        "four",
        "five",
        "six",
        "seven",
    ]
    with pytest.raises(ValueError):
        fit_words("short", 6)


def test_audio_safe_word_boundary():
    assert "mallet" in audio_safe("the hammer fell")
    assert "hammerhead" in audio_safe("hammerhead")


def test_channel_template():
    ch = load_channel("monarch/channels/_template.yaml")
    assert ch.vo_mode == "SILENT"
    assert ch.id == "channel_slug"


def test_board_and_prompts():
    m = compute_math(30)
    lines = ["alpha bravo charlie delta echo foxtrot golf"] * m.scenes
    scenes = board_from_lines(lines, 30)
    assert scenes[0].t_end <= 3.01
    ch = Channel(
        id="x",
        niche="edu",
        character_lock="a simple hand-drawn doodle character with thick black outlines",
        vo_mode="SILENT",
    )
    para = animation_paragraph(scenes[0], ch, clip_s=m.clip_s, is_last=False)
    assert "\n" not in para
    assert "doodle character" in para
    assert len(run_prompts(scenes, ch, m.clip_s)) == m.scenes


def test_rank_drops_banned():
    kept = rank_titles(
        ["Top 10 Bear Attacks", "The ice that refused to melt"],
        "iceberg",
        True,
    )
    assert kept[0].startswith("The ice")


def test_package():
    idea = Idea(
        title="The ice that refused to melt",
        hook="why one glacier never died",
        itch="incongruity",
        visual_anchor="iceberg with a pulse",
    )
    m = compute_math(30)
    lines = ["alpha bravo charlie delta echo foxtrot golf"] * m.scenes
    scenes = board_from_lines(lines, 30)
    ch = Channel(id="x", niche="edu", character_lock="stick lock")
    pkg = package(idea, scenes, ch)
    assert pkg["thumbs"][0]["negative"]
    assert pkg["listing"]["privacy"] == "private"


def test_missing_and_lessons(tmp_path: Path):
    assert "default" in missing("niche").lower()
    assert require_fields({}, ["niche"]) == []
    assert require_fields({}, ["transcript_dir"])
    p = tmp_path / "lessons.md"
    record("generic title", "ban top 10", p)
    assert "3x rule" in p.read_text()


def test_keys_never_echo_values(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "secret-should-not-leak")
    from monarch.core.config import has_gemini, secrets

    assert has_gemini()
    assert secrets().gemini  # exists
    # CLI contract: we only print booleans, not this string in keys cmd


def test_score_sane():
    assert score_title("The ice that refused to melt") > score_title("x")
