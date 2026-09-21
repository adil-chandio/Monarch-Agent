"""M3_script integration: Fountain screenplay (or a JSON board) → gated scenes.

Law this module obeys:

* M3 says *numbered scenes, quoted line, [n words] exact*. The word count comes
  from :func:`monarch.core.scene_math.compute_math` — never from taste.
* Scene **duration is never invented**: ``words / speaking_wps`` (the first
  clip is clamped to ``first_clip_s`` when the line fits inside it). A rewrite
  of the screenplay keeps the maths line true.
* Fail-closed: the board passes :func:`monarch.core.gates.gate_scenes` before it
  is returned. Problems are *reported*, never silently fixed — no padding, no
  faked counts; at the M3 stop the operator answers ``perfect | improve``.
* Nothing here generates video or audio. Render still needs the HAAN gate.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from monarch.core import fountain
from monarch.core.fit_line import fit_words
from monarch.core.fountain import (
    ACTION,
    CHARACTER,
    DIALOGUE,
    ELEMENT_KINDS,
    PARENTHETICAL,
    SCENE_HEADING,
    Element,
    Screenplay,
)
from monarch.core.gates import GateFail, gate_scenes
from monarch.core.scene_math import compute_math, maths_line
from monarch.core.words import count_words, tokenize
from monarch.schemas import Scene, SceneMath

#: Visual direction per beat: prepended to the beat as ``::visual:: spoken``.
#: It is stripped before word-fit, so a visual note never counts as words.
VISUAL_MARK = "::"

#: Element kinds that can carry a spoken (VO) beat.
SPEAKABLE = (DIALOGUE, ACTION, PARENTHETICAL)


@dataclass
class FountainBeat:
    """One candidate VO beat, keeping its screenplay lineage."""

    number: int
    kind: str
    text: str
    speaker: str = ""
    extension: str = ""
    visual: str = ""
    slug: str = ""
    screen_scene: int = 1
    element_index: int = 0
    source_line: int = 0
    #: words in the screenplay beat
    words: int = 0
    #: words actually spoken after the exact-word fit
    vo_words: int = 0
    vo_line: str = ""
    fitted: bool = False
    issues: list[str] = field(default_factory=list)

    @property
    def label(self) -> str:
        head = f"[{self.kind}]"
        if self.speaker:
            head += f" {self.speaker}"
            if self.extension:
                head += f" ({self.extension})"
        return head

    def to_dict(self) -> dict:
        d = {
            "number": self.number,
            "kind": self.kind,
            "text": self.text,
            "visual": self.visual,
            "slug": self.slug,
            "screen_scene": self.screen_scene,
            "element_index": self.element_index,
            "source_line": self.source_line,
            "words": self.words,
            "vo_words": self.vo_words,
            "vo_line": self.vo_line,
            "fitted": self.fitted,
        }
        if self.speaker:
            d["speaker"] = self.speaker
        if self.extension:
            d["extension"] = self.extension
        if self.issues:
            d["issues"] = list(self.issues)
        return d


@dataclass
class ScriptReport:
    """Everything the operator needs at the M3 stop."""

    maths: SceneMath
    math_line: str
    beats: list[FountainBeat] = field(default_factory=list)
    scenes: list[Scene] = field(default_factory=list)
    title: str = ""
    byline: str = ""
    source: str = ""

    @property
    def unfit(self) -> list[FountainBeat]:
        """Beats that cannot be spoken as-is (too few words to fit, mostly)."""
        return [b for b in self.beats if not b.fitted]

    @property
    def trimmed(self) -> list[FountainBeat]:
        return [b for b in self.beats if b.fitted and b.issues]

    @property
    def units(self) -> list[tuple[FountainBeat, Scene]]:
        return list(zip(self.beats, self.scenes))

    @property
    def board_s(self) -> float:
        return round(self.scenes[-1].t_end, 3) if self.scenes else 0.0

    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "title": self.title,
            "byline": self.byline,
            "maths": {
                "line": self.math_line,
                "total_s": self.maths.total_s,
                "clip_s": self.maths.clip_s,
                "scenes": self.maths.scenes,
                "words_per_clip": self.maths.words_per_clip,
                "first_clip_s": self.maths.first_clip_s,
                "speaking_wps": self.maths.speaking_wps,
            },
            "beats": [b.to_dict() for b in self.beats],
            "scenes": [
                {
                    "id": s.id,
                    "vo_line": s.vo_line,
                    "visual": s.visual,
                    "word_count": s.word_count,
                    "t_start": s.t_start,
                    "t_end": s.t_end,
                    "sfx": s.sfx,
                    "retention_job": s.retention_job,
                    "match_cut": s.match_cut,
                }
                for s in self.scenes
            ],
        }

    def summary(self) -> str:
        rows = [
            self.math_line,
            f"title: {self.title or '<untitled>'}"
            + (f" | {self.byline}" if self.byline else ""),
        ]
        for beat in self.beats:
            visual = f" | visual: {beat.visual}" if beat.visual else ""
            flag = "" if beat.fitted else "  <-- needs work: " + "; ".join(beat.issues)
            rows.append(
                f"{beat.number:02d}. {beat.label} "
                f'"{beat.vo_line}" [{beat.vo_words or beat.words} words]{visual}{flag}'
            )
        if self.scenes:
            rows.append(
                f"board: {len(self.scenes)} clips | {self.board_s:g}s | "
                f"{self.maths.scenes} maths clips at {self.maths.clip_s:g}s | "
                f"words/clip exact {self.maths.words_per_clip}"
            )
        if self.scenes and not self.unfit and abs(self.board_s - self.maths.total_s) > 0.5:
            rows.append(
                f"length: {self.board_s:g}s spoken of {self.maths.total_s:g}s requested — "
                f"{self.maths.total_s - self.board_s:.1f}s left for SFX and silence beats"
            )
        if self.trimmed:
            rows.append(f"trimmed: {len(self.trimmed)} beat(s) to hit the exact count")
        if self.unfit:
            rows.append(
                f"needs work: {len(self.unfit)} beat(s) too short to fit "
                f"{self.maths.words_per_clip} words — add words, split the beat, "
                "or pick a longer length. (no padding, no faking the count)"
            )
        return "\n".join(rows)


# --------------------------------------------------------------------------
# screenplay sources
# --------------------------------------------------------------------------


def screenplay_from_text(text: str, source: str = "<text>") -> Screenplay:
    """Parse Fountain text (the operator's ``.fountain`` file or a paste)."""
    return fountain.parse(text, source=source)


def screenplay_from_path(path: str | Path) -> Screenplay:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"This is missing, could you provide it: fountain file {p}.")
    return fountain.parse_file(p)


def screenplay_from_json(data: dict | str | Path) -> Screenplay:
    """Rebuild a :class:`Screenplay` from :meth:`Screenplay.to_dict` output.

    Project JSON stays machine-readable while Fountain stays the human format.
    """
    raw = _load_json(data)
    tp_raw = raw.get("title_page", {}) or {}
    tp = fountain.TitlePage(
        title=tp_raw.get("title", ""),
        credit=tp_raw.get("credit", ""),
        author=tp_raw.get("author", ""),
        source=tp_raw.get("source", ""),
        draft_date=tp_raw.get("draft_date", ""),
        contact=tp_raw.get("contact", ""),
        copyright=tp_raw.get("copyright", ""),
        notes=tp_raw.get("notes", ""),
        extra=dict(tp_raw.get("extra", {}) or {}),
    )
    elements: list[Element] = []
    for e in raw.get("elements", []):
        kind = e.get("kind", e.get("type", ACTION))
        if kind not in ELEMENT_KINDS:
            raise ValueError(f"unknown element kind: {kind!r}")
        slug_raw = e.get("slugline")
        slug = None
        if slug_raw:
            slug = fountain.Slugline(
                prefix=slug_raw.get("prefix", ""),
                location=slug_raw.get("location", ""),
                time_of_day=slug_raw.get("time_of_day", ""),
                scene_number=slug_raw.get("scene_number"),
            )
        elements.append(
            Element(
                kind=kind,
                text=e.get("text", ""),
                start=int(e.get("start", 0)),
                end=int(e.get("end", e.get("start", 0))),
                forced=bool(e.get("forced", False)),
                slugline=slug,
                character=e.get("character", ""),
                extension=e.get("extension", ""),
                dual=bool(e.get("dual", False)),
                depth=int(e.get("depth", 0)),
            )
        )
    return Screenplay(title_page=tp, elements=elements, source=raw.get("source", "<json>"))


def _load_json(data: dict | str | Path) -> dict:
    if isinstance(data, dict):
        return data
    if isinstance(data, Path):
        return json.loads(data.read_text(encoding="utf-8"))
    text = str(data)
    p = Path(text) if "\n" not in text and len(text) < 4096 else None
    if p is not None and p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    loaded = json.loads(text)
    if not isinstance(loaded, dict):
        raise TypeError("script JSON must be an object")
    return loaded


# --------------------------------------------------------------------------
# beats
# --------------------------------------------------------------------------


def split_visual(text: str) -> tuple[str, str]:
    """``::visual:: spoken line`` → ``(visual, spoken)``; otherwise ``("", text)``."""
    t = (text or "").strip()
    if not t.startswith(VISUAL_MARK):
        return "", t
    rest = t[len(VISUAL_MARK) :]
    visual, sep, spoken = rest.partition(VISUAL_MARK)
    if not sep:
        return rest.strip(), ""
    return visual.strip(), spoken.strip()


def _wanted_speakers(speaker: str | None) -> set[str] | None:
    if not speaker:
        return None
    return {s.strip().lower() for s in speaker.split(",") if s.strip()}


def beats_from_screenplay(
    sp: Screenplay,
    *,
    include: tuple[str, ...] = SPEAKABLE,
    speaker: str | None = None,
    visual_hint: str = "",
) -> list[FountainBeat]:
    """Screenplay elements → candidate VO beats (no maths applied yet)."""
    out: list[FountainBeat] = []
    wanted = _wanted_speakers(speaker)
    scene_index = 0
    slug_label = ""
    current_speaker = ""
    current_ext = ""
    for i, e in enumerate(sp.elements):
        if e.kind == SCENE_HEADING:
            scene_index += 1
            slug_label = e.slugline.label() if e.slugline else e.text
            current_speaker = ""
            current_ext = ""
            continue
        if e.kind == CHARACTER:
            current_speaker = e.text.strip()
            current_ext = e.extension.strip()
            continue
        if e.kind not in include:
            continue
        if wanted is not None and current_speaker.lower() not in wanted:
            continue
        visual, text = split_visual(e.text)
        if not text:
            continue
        out.append(
            FountainBeat(
                number=len(out) + 1,
                kind=e.kind,
                text=text,
                speaker=current_speaker,
                extension=current_ext,
                visual=visual or visual_hint or slug_label,
                slug=slug_label,
                screen_scene=scene_index or 1,
                element_index=i,
                source_line=e.start,
                words=count_words(text),
            )
        )
    return out


def beats_from_lines(lines: list[str], visual_hint: str = "") -> list[FountainBeat]:
    """Plain lines — one beat per line, ``::`` visual supported."""
    out: list[FountainBeat] = []
    for i, raw in enumerate(lines, 1):
        visual, text = split_visual(raw or "")
        if not text:
            continue
        out.append(
            FountainBeat(
                number=len(out) + 1,
                kind=ACTION,
                text=text,
                visual=visual or visual_hint,
                screen_scene=1,
                element_index=i - 1,
                source_line=i,
                words=count_words(text),
            )
        )
    return out


def beats_from_json(data: dict | str | Path) -> list[FountainBeat]:
    """Accept ``monarch screen-script --json`` output (object or list)."""
    raw = _load_json(data) if isinstance(data, (dict, Path)) or _looks_like_json(data) else data
    items = raw.get("beats", raw) if isinstance(raw, dict) else raw
    if not isinstance(items, list):
        raise TypeError("script JSON must be a list or an object with 'beats'")
    out: list[FountainBeat] = []
    for i, item in enumerate(items, 1):
        if isinstance(item, str):
            visual, text = split_visual(item)
            item = {"text": text, "visual": visual}
        text = str(item.get("text") or item.get("vo_line") or item.get("line") or "").strip()
        visual, text = split_visual(text)
        if not visual:
            visual = str(item.get("visual") or "").strip()
        if not text:
            continue
        out.append(
            FountainBeat(
                number=len(out) + 1,
                kind=str(item.get("kind") or ACTION),
                text=text,
                speaker=str(item.get("speaker") or item.get("character") or ""),
                extension=str(item.get("extension") or ""),
                visual=visual,
                slug=str(item.get("slug") or item.get("slugline") or ""),
                screen_scene=int(item.get("screen_scene") or 1),
                element_index=i - 1,
                source_line=int(item.get("source_line") or i),
                words=count_words(text),
            )
        )
    return out


def _looks_like_json(data) -> bool:
    if isinstance(data, str):
        s = data.strip()
        return s.startswith(("{", "["))
    return False


# --------------------------------------------------------------------------
# beats → Monarch board (the M3 maths)
# --------------------------------------------------------------------------


def _fit_beat(beat: FountainBeat, words: int) -> None:
    tokens = tokenize(beat.text)
    if len(tokens) < words:
        beat.vo_line = " ".join(tokens)
        beat.fitted = False
        beat.issues.append(
            f"{len(tokens)} words, need exactly {words} — never pad, write the words"
        )
        return
    beat.vo_line = fit_words(beat.text, words)
    beat.fitted = True
    if len(tokens) > words:
        beat.issues.append(
            f"trimmed {len(tokens)} → {words} words (dropped: {' '.join(tokens[words:])})"
        )


def _duration(index: int, words: int, maths: SceneMath) -> float:
    seconds = words / maths.speaking_wps
    if index == 1:
        return round(min(maths.first_clip_s, seconds), 3)
    return round(seconds, 3)


def _retention_job(index: int, total: int, kind: str) -> str:
    if index == 1:
        return "hook"
    if index == total:
        return "payoff"
    if kind == PARENTHETICAL:
        return "tone"
    return "advance"


def build_script(
    beats: list[FountainBeat],
    total_s: float,
    *,
    clip_s: float = 3.5,
    speaking_wps: float = 2.2,
    first_clip_s: float = 2.5,
    gate: bool = True,
    sfx: str = "",
    title: str = "",
    byline: str = "",
    source: str = "",
) -> ScriptReport:
    """Fit beats to the M3 word maths and build the numbered scene board."""
    maths = compute_math(
        total_s,
        clip_s=clip_s,
        speaking_wps=speaking_wps,
        first_clip_s=first_clip_s,
    )
    beats = list(beats)
    for i, beat in enumerate(beats, 1):
        beat.number = i
        beat.issues = []
        _fit_beat(beat, maths.words_per_clip)

    t = 0.0
    scenes: list[Scene] = []
    for i, beat in enumerate(beats, 1):
        # the board counts what is actually spoken, never the screenplay draft
        beat.vo_words = count_words(beat.vo_line)
        dur = _duration(i, beat.vo_words, maths)
        scenes.append(
            Scene(
                id=i,
                vo_line=beat.vo_line,
                visual=beat.visual or f"stickman beat {i}",
                word_count=beat.vo_words,
                t_start=round(t, 3),
                t_end=round(t + dur, 3),
                sfx=sfx,
                retention_job=_retention_job(i, len(beats), beat.kind),
                match_cut=beat.visual or "",
            )
        )
        t += dur

    report = ScriptReport(
        maths=maths,
        math_line=maths_line(maths),
        beats=beats,
        scenes=scenes,
        title=title,
        byline=byline,
        source=source,
    )
    if gate:
        assert_gated(report)
    return report


def assert_gated(report: ScriptReport) -> None:
    """Fail closed on the maths, not on taste."""
    misses: list[str] = []
    if len(report.scenes) != report.maths.scenes:
        misses.append(
            f"script has {len(report.scenes)} beats, maths needs "
            f"{report.maths.scenes} scenes at {report.maths.clip_s:g}s clips"
        )
    if misses:
        raise GateFail(misses)
    gate_scenes(report.scenes, report.maths.words_per_clip)


def board_json(scenes: list[Scene]) -> str:
    return json.dumps(
        [
            {
                "id": s.id,
                "vo_line": s.vo_line,
                "visual": s.visual,
                "word_count": s.word_count,
                "t_start": s.t_start,
                "t_end": s.t_end,
                "retention_job": s.retention_job,
                "match_cut": s.match_cut,
                "sfx": s.sfx,
            }
            for s in scenes
        ],
        indent=2,
    )


def beats_json(beats: list[FountainBeat]) -> str:
    return json.dumps([b.to_dict() for b in beats], indent=2)


# --------------------------------------------------------------------------
# board → Fountain (hand the approved script to a human writer)
# --------------------------------------------------------------------------


def write_fountain(
    scenes: list[Scene],
    *,
    slugs: list[str] | None = None,
    title: str = "",
    author: str = "",
    draft_date: str = "",
    contact: str = "",
    sfx: str = "",
) -> str:
    """Export the board as Fountain. Word counts stay exact and re-parseable."""
    lines: list[str] = []
    for key, value in (
        ("Title", title),
        ("Author", author),
        ("Draft date", draft_date),
        ("Contact", contact),
    ):
        if value:
            lines.append(f"{key}: {value}")
    if lines:
        lines.append("")
    for i, s in enumerate(scenes):
        if i:
            lines.append("")
        heading = slugs[i] if slugs and i < len(slugs) else f"EXT. BEAT {s.id:02d} - DAY"
        lines.append(heading)
        lines.append("")
        lines.append("VOICEOVER (V.O.)")
        visual = s.visual or "beat"
        lines.append(f"{VISUAL_MARK}{visual}{VISUAL_MARK} {s.vo_line}")
        lines.append(f"[[sfx: {s.sfx or sfx or 'cut hit'} | job: {s.retention_job}]]")
    return "\n".join(lines).rstrip() + "\n"


def scene_count_line(sp: Screenplay) -> str:
    counts = sp.counts()
    parts = [f"{k}={v}" for k, v in counts.items() if v]
    return f"{len(sp.scenes)} scenes | " + ", ".join(parts)
