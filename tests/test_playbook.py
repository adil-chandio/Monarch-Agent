"""Tests for the 17-check QC system and playbook laws (L14–L16)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from monarch.core.self_qc import (
    CHECK_MAP,
    CHECKS,
    QCFail,
    QCResult,
    Stage,
    qc,
    qc_render,
    qc_script,
    qc_strict,
)
from monarch.schemas import Scene


# ---------------------------------------------------------------------------
# L14 — 17-check system
# ---------------------------------------------------------------------------


def test_all_checks_exist():
    """All 17 checks are registered."""
    assert len(CHECKS) == 17
    for i in range(1, 18):
        assert i in {c.id for c in CHECKS}, f"check {i} missing"


def test_check_names_unique():
    names = [c.name for c in CHECKS]
    assert len(names) == len(set(names))


def test_qc_all_pass():
    notes = {c.name: True for c in CHECKS}
    result = qc(notes, stage=Stage.PACKAGING)
    assert result.passed
    assert result.checked == 17


def test_qc_one_fail():
    notes = {c.name: True for c in CHECKS}
    notes["open_loop_hook"] = False
    result = qc(notes, stage=Stage.SCRIPT)
    assert not result.passed
    assert "open_loop_hook" in result.failed


def test_qc_stage_filtering():
    """Script-stage QC should not check packaging-only checks."""
    notes = {c.name: True for c in CHECKS if c.stage in (Stage.RESEARCH, Stage.SCRIPT)}
    result = qc(notes, stage=Stage.SCRIPT)
    assert result.passed
    assert result.checked < 17


def test_qc_strict_raises():
    notes = {c.name: True for c in CHECKS}
    notes["no_clone_or_top10"] = False
    with pytest.raises(QCFail) as exc:
        qc_strict(notes, stage=Stage.PACKAGING)
    assert "no_clone_or_top10" in exc.value.misses


def test_qc_strict_passes():
    notes = {c.name: True for c in CHECKS}
    qc_strict(notes, stage=Stage.PACKAGING)  # should not raise


# ---------------------------------------------------------------------------
# L14 — script QC
# ---------------------------------------------------------------------------


def test_qc_script_pass():
    scenes = [
        Scene(
            id=1,
            vo_line="He walked into the room and saw",
            word_count=8,
            retention_job="open loop — incomplete sentence",
            match_cut="pose and facing direction",
            visual="character enters doorway",
        ),
        Scene(
            id=2,
            vo_line="something that should not have been there.",
            word_count=8,
            retention_job="reveal the object",
            match_cut="",
            visual="close-up of object",
        ),
    ]
    misses = qc_script(scenes, words_per_clip=8)
    assert misses == []


def test_qc_script_wrong_word_count():
    scenes = [
        Scene(
            id=1,
            vo_line="too short",
            word_count=2,
            retention_job="hook",
            match_cut="pose",
            visual="character",
        ),
    ]
    misses = qc_script(scenes, words_per_clip=7)
    assert any("words" in m for m in misses)


def test_qc_script_missing_retention_job():
    scenes = [
        Scene(
            id=1,
            vo_line="one two three four five six seven",
            word_count=7,
            retention_job="",
            match_cut="pose",
            visual="character",
        ),
    ]
    misses = qc_script(scenes, words_per_clip=7)
    assert any("retention_job" in m for m in misses)


def test_qc_script_baked_text_flag():
    """Visual prompt with quoted text + vo_line should flag baked-text check."""
    scenes = [
        Scene(
            id=1,
            vo_line='He says "hello world"',
            word_count=4,
            retention_job="hook",
            match_cut="pose",
            visual='text on screen "hello world"',
        ),
    ]
    misses = qc_script(scenes, words_per_clip=4)
    assert any("baked_text" in m for m in misses)


# ---------------------------------------------------------------------------
# L15 — render QC
# ---------------------------------------------------------------------------


def test_qc_render_pass():
    misses = qc_render(
        scene_count=8,
        expected_scenes=8,
        total_s=60.0,
        expected_total=60.0,
        max_clip_hold=3.5,
        scene_durations=[2.5, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.5],
    )
    assert misses == []


def test_qc_render_scene_count_mismatch():
    misses = qc_render(
        scene_count=7,
        expected_scenes=8,
        total_s=60.0,
        expected_total=60.0,
    )
    assert any("scene_count" in m for m in misses)


def test_qc_render_duration_mismatch():
    misses = qc_render(
        scene_count=8,
        expected_scenes=8,
        total_s=45.0,
        expected_total=60.0,
    )
    assert any("total_duration" in m for m in misses)


def test_qc_render_clip_hold_exceeded():
    misses = qc_render(
        scene_count=3,
        expected_scenes=3,
        total_s=10.0,
        expected_total=10.0,
        max_clip_hold=3.5,
        scene_durations=[2.5, 5.0, 2.5],
    )
    assert any("hold" in m for m in misses)


# ---------------------------------------------------------------------------
# L16 — self-improvement loop integration
# ---------------------------------------------------------------------------


def test_lessons_record(tmp_path: Path):
    from monarch.core.lessons import record

    p = tmp_path / "lessons.md"
    record("open_loop_hook", "first VO line must end with ellipsis or dash", p)
    text = p.read_text()
    assert "open_loop_hook" in text
    assert "3x rule" in text


def test_qc_result_summary():
    r_pass = QCResult(passed=True, checked=17)
    assert "PASS" in r_pass.summary

    r_fail = QCResult(passed=False, failed=["open_loop_hook", "silence_sting"], checked=17)
    assert "FAIL" in r_fail.summary
    assert "2 miss" in r_fail.summary
