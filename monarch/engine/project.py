from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from dataclasses import fields as dataclass_fields
from pathlib import Path

from monarch.core.fountain import Screenplay
from monarch.schemas import Channel, Idea, Package, Scene, SceneMath, ViralDNA

#: field name → dataclass, used by :meth:`Project.load` to rebuild JSON
_NESTED = {
    "channel": Channel,
    "math": SceneMath,
    "ideas": Idea,
    "picked": Idea,
    "scenes": Scene,
    "package": Package,
    "dna": ViralDNA,
}


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
    #: M3_script — the parsed Fountain screenplay (``Screenplay.to_dict()``).
    screenplay: dict | None = None
    #: where that screenplay came from (path or "<paste>")
    fountain_source: str = ""

    def dump(self, path: str | Path) -> None:
        Path(path).write_text(
            json.dumps(asdict(self), indent=2),
            encoding="utf-8",
        )

    @classmethod
    def load(cls, path: str | Path) -> Project:
        """Rebuild a project (scenes, maths, ideas, screenplay) from JSON."""
        raw = json.loads(Path(path).read_text(encoding="utf-8"))

        def build(target, data):
            if data is None:
                return None
            if isinstance(data, list):
                return [build(target, row) for row in data]
            allowed = {f.name for f in dataclass_fields(target)}
            return target(**{k: v for k, v in data.items() if k in allowed})

        kwargs = {}
        for f in dataclass_fields(cls):
            data = raw.get(f.name)
            target = _NESTED.get(f.name)
            kwargs[f.name] = build(target, data) if target else data
        return cls(**kwargs)

    def set_screenplay(self, sp: Screenplay) -> None:
        """Store the parsed Fountain screenplay without flattening it to prose."""
        self.screenplay = sp.to_dict()
        self.fountain_source = sp.source

    def m3_from_fountain(
        self,
        path: str | Path,
        total_s: float = 60.0,
        *,
        clip_s: float = 3.5,
        include: tuple[str, ...] | None = None,
        speaker: str | None = None,
        visual_hint: str = "",
        sfx: str = "",
        gate: bool = True,
    ):
        """Parse a ``.fountain`` file and bind the gated board to this project.

        Returns the :class:`~monarch.pipelines.fountain.ScriptReport`, so the
        caller can show the M3 stop and the operator can answer
        ``perfect | improve``. Nothing is written to disk here.
        """
        from monarch.pipelines.fountain import (
            SPEAKABLE,
            beats_from_screenplay,
            build_script,
            screenplay_from_path,
        )

        sp = screenplay_from_path(path)
        self.set_screenplay(sp)
        report = build_script(
            beats_from_screenplay(
                sp,
                include=SPEAKABLE if include is None else include,
                speaker=speaker,
                visual_hint=visual_hint,
            ),
            total_s,
            clip_s=clip_s,
            gate=gate,
            sfx=sfx,
            title=sp.title_page.title,
            byline=sp.title_page.byline,
            source=sp.source,
        )
        self.math = report.maths
        self.scenes = report.scenes
        return report
