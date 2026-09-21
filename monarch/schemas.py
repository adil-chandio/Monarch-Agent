from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

VOMode = Literal["BAKED", "SILENT"]
Aspect = Literal["9:16", "16:9"]
Privacy = Literal["private", "unlisted", "public"]


@dataclass
class Channel:
    id: str
    niche: str
    aspect: Aspect = "16:9"
    language: str = "en"
    accent_color: str = "#E8B923"
    vo_mode: VOMode = "SILENT"
    character_lock: str = ""
    voice_lock: str = ""


@dataclass
class SceneMath:
    total_s: float
    clip_s: float
    scenes: int
    words_per_clip: int
    first_clip_s: float = 2.5
    speaking_wps: float = 2.2


@dataclass
class Scene:
    id: int
    vo_line: str
    visual: str = ""
    word_count: int = 0
    t_start: float = 0.0
    t_end: float = 0.0
    sfx: str = ""
    retention_job: str = ""
    match_cut: str = ""


@dataclass
class Idea:
    title: str
    hook: str
    itch: str
    visual_anchor: str
    factual: bool = True
    clone_of: str | None = None


@dataclass
class Package:
    titles: list[str] = field(default_factory=list)
    thumb_briefs: list[str] = field(default_factory=list)
    description: str = ""
    tags: list[str] = field(default_factory=list)
    privacy: Privacy = "private"


@dataclass
class ViralDNA:
    channel: str
    hook_architecture: list[str] = field(default_factory=list)
    retention_loops: list[str] = field(default_factory=list)
    sentence_rhythm: str = ""
    structure: str = ""
    template: str = ""
    elevate_notes: str = ""


GENERIC_TITLE_BANS = (
    "top 10",
    "top ten",
    "you won't believe",
    "gone wrong",
    "gone sexual",
    "in 2024",
    "in 2025",
    "in 2026",
    "subscribe",
    "link in bio",
)
