"""QC selftest — 17-check system (playbook L14).

Every deliverable must pass all applicable checks before presentation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Stage(str, Enum):
    """Pipeline stage — determines which checks apply."""

    RESEARCH = "research"
    SCRIPT = "script"
    RENDER = "render"
    EDIT = "edit"
    PACKAGING = "packaging"


@dataclass
class QCCheck:
    id: int
    name: str
    stage: Stage
    fail_action: str


CHECKS: list[QCCheck] = [
    QCCheck(1, "research_not_skipped", Stage.RESEARCH, "Re-run forensic"),
    QCCheck(2, "gates_not_hidden", Stage.RESEARCH, "Re-run gates explicitly"),
    QCCheck(3, "ijazat_asked", Stage.RENDER, "Ask HAAN before proceeding"),
    QCCheck(4, "no_clone_or_top10", Stage.PACKAGING, "Rewrite title/thumb"),
    QCCheck(5, "duration_matches_vo", Stage.SCRIPT, "Recompute maths"),
    QCCheck(6, "word_count_exact", Stage.SCRIPT, "Rewrite scene to fit"),
    QCCheck(7, "open_loop_hook", Stage.SCRIPT, "Rewrite hook — must be incomplete without watching"),
    QCCheck(8, "retention_job_on_every_beat", Stage.SCRIPT, "Add retention_job to each scene"),
    QCCheck(9, "match_cut_named", Stage.SCRIPT, "Add match-cut to non-final scenes"),
    QCCheck(10, "no_baked_text_in_gen", Stage.RENDER, "Remove text from clip prompt"),
    QCCheck(11, "character_lock_verbatim", Stage.RENDER, "Insert character lock sentence"),
    QCCheck(12, "negative_prompt_attached", Stage.RENDER, "Add negative prompt to gen block"),
    QCCheck(13, "sfx_no_double_hit", Stage.EDIT, "Change SFX family — no same family on consecutive cuts"),
    QCCheck(14, "silence_sting", Stage.EDIT, "Insert silence before key fact"),
    QCCheck(15, "postage_readable_thumb", Stage.PACKAGING, "Redo thumb — must be readable at ~120 px"),
    QCCheck(16, "title_thumb_one_sentence", Stage.PACKAGING, "Rewrite — title + thumb must be one idea, not two videos"),
    QCCheck(17, "click_debt_paid", Stage.PACKAGING, "Add payoff to script — click contract must be honoured"),
]

#: Quick-lookup: name → QCCheck
CHECK_MAP: dict[str, QCCheck] = {c.name: c for c in CHECKS}


class QCFail(Exception):
    """Raised when one or more QC checks fail."""

    def __init__(self, misses: list[str]) -> None:
        super().__init__("; ".join(misses))
        self.misses = misses


@dataclass
class QCResult:
    """Result of a QC pass."""

    passed: bool
    failed: list[str] = field(default_factory=list)
    checked: int = 0

    @property
    def summary(self) -> str:
        if self.passed:
            return f"QC PASS — {self.checked} checks cleared"
        return f"QC FAIL — {len(self.failed)} miss(es): {'; '.join(self.failed)}"


def _applicable_checks(stage: Stage) -> list[QCCheck]:
    """Return checks that apply to the given stage and earlier stages."""
    order = [Stage.RESEARCH, Stage.SCRIPT, Stage.RENDER, Stage.EDIT, Stage.PACKAGING]
    idx = order.index(stage)
    return [c for c in CHECKS if order.index(c.stage) <= idx]


def qc(notes: dict[str, bool], *, stage: Stage = Stage.PACKAGING) -> QCResult:
    """Run QC for the given stage.

    ``notes`` maps check names to ``True`` (pass) or ``False``/absent (fail).
    Only checks applicable to ``stage`` (and earlier) are evaluated.
    """
    applicable = _applicable_checks(stage)
    failed = [c.name for c in applicable if not notes.get(c.name, False)]
    return QCResult(passed=not failed, failed=failed, checked=len(applicable))


def qc_strict(notes: dict[str, bool], *, stage: Stage = Stage.PACKAGING) -> None:
    """Like ``qc()`` but raises :class:`QCFail` on any miss."""
    result = qc(notes, stage=stage)
    if not result.passed:
        raise QCFail(result.failed)


def qc_script(scenes: list[Any], words_per_clip: int) -> list[str]:
    """Dedicated script QC — checks laws L6–L9 from the17-check table.

    Returns a list of miss names (empty = pass).
    """
    misses: list[str] = []
    for i, s in enumerate(scenes):
        n = getattr(s, "word_count", 0) or 0
        vo = getattr(s, "vo_line", "") or ""
        is_last = i == len(scenes) - 1
        # word_count_exact (check 6)
        if n != words_per_clip:
            misses.append(f"scene_{s.id}_words_{n}_expected_{words_per_clip}")
        # retention_job (check 8)
        if not getattr(s, "retention_job", ""):
            misses.append(f"scene_{s.id}_no_retention_job")
        # match_cut on non-final scenes only (check 9)
        if not is_last and not getattr(s, "match_cut", ""):
            misses.append(f"scene_{s.id}_no_match_cut")
        # no baked text (check 10) — visual prompt must not contain quoted spoken line
        visual = getattr(s, "visual", "") or ""
        if '"' in visual and vo:
            misses.append(f"scene_{s.id}_possible_baked_text_in_visual")
    # open loop hook (check 7) — first scene VO must feel incomplete
    if scenes:
        first_vo = (scenes[0].vo_line or "").strip()
        if first_vo.endswith("."):
            misses.append("scene_1_hook_may_be_closed_loop")
    return misses


def qc_render(
    scene_count: int,
    expected_scenes: int,
    total_s: float,
    expected_total: float,
    max_clip_hold: float = 3.5,
    scene_durations: list[float] | None = None,
) -> list[str]:
    """Dedicated render QC — checks laws L13–L15.

    Returns a list of miss names (empty = pass).
    """
    misses: list[str] = []
    if scene_count != expected_scenes:
        misses.append(f"scene_count_{scene_count}_expected_{expected_scenes}")
    if abs(total_s - expected_total) > 1.0:
        misses.append(f"total_duration_{total_s:.1f}_expected_{expected_total:.1f}")
    if scene_durations:
        for i, d in enumerate(scene_durations, 1):
            if d > max_clip_hold:
                misses.append(f"scene_{i}_hold_{d:.1f}s_exceeds_{max_clip_hold}s")
    return misses
