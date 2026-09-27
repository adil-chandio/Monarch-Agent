from __future__ import annotations

from monarch.core.words import count_words
from monarch.schemas import GENERIC_TITLE_BANS, Idea, Scene


class GateFail(Exception):
    def __init__(self, misses: list[str]):
        super().__init__("; ".join(misses))
        self.misses = misses


def gate_idea(idea: Idea) -> None:
    misses: list[str] = []
    blob = f"{idea.title} {idea.hook}".lower()
    if not idea.factual:
        misses.append("not factual / not researchable")
    if idea.clone_of:
        misses.append(f"clone of {idea.clone_of}")
    if not idea.visual_anchor.strip():
        misses.append("no visual anchor")
    if not idea.itch.strip():
        misses.append("no psychology itch")
    if any(b in blob for b in GENERIC_TITLE_BANS):
        misses.append("generic banned title DNA")
    if len(idea.title.strip()) < 8:
        misses.append("title too thin")
    if misses:
        raise GateFail(misses)


def gate_scenes(scenes: list[Scene], words_per_clip: int) -> None:
    misses: list[str] = []
    if not scenes:
        misses.append("no scenes")
    for s in scenes:
        n = s.word_count or count_words(s.vo_line)
        if n != words_per_clip:
            misses.append(f"scene {s.id} words {n} != {words_per_clip}")
        if not s.retention_job:
            misses.append(f"scene {s.id} has no retention job")
        if not s.visual:
            misses.append(f"scene {s.id} has no visual")
    if scenes and (scenes[0].t_end - scenes[0].t_start) > 3.01:
        misses.append("open longer than 3s")
    if misses:
        raise GateFail(misses)


def gate_title(title: str, thumb_brief: str, payoff_in_script: bool) -> None:
    misses: list[str] = []
    t = title.lower()
    if any(b in t for b in GENERIC_TITLE_BANS):
        misses.append("banned title pattern")
    if len(title) > 70:
        misses.append("title too long for mobile scan")
    if not payoff_in_script:
        misses.append("click contract unpaid")
    if not thumb_brief.strip():
        misses.append("no thumb")
    if misses:
        raise GateFail(misses)
