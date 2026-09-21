from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

from monarch.schemas import Channel, Idea, Package, Scene, SceneMath, ViralDNA


@dataclass
class Project:
    channel: Channel
    math: SceneMath | None = None
    ideas: list[Idea] = field(default_factory=list)
    picked: Idea | None = None
    scenes: list[Scene] = field(default_factory=list)
    prompts: list[str] = field(default_factory=list)
    package: Package | None = None
    dna: ViralDNA | None = None

    def dump(self, path: str | Path) -> None:
        Path(path).write_text(
            json.dumps(asdict(self), indent=2),
            encoding="utf-8",
        )
