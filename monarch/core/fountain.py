"""Fountain (``.fountain``) screenplay parser — stdlib only, no dependencies.

Covered syntax (https://fountain.io/syntax):

* title page keys (``Title:``, ``Credit:``, ``Author:``, ``Source:``,
  ``Draft date:``, ``Contact:``, ``Copyright:``, ``Notes:`` + free keys)
* scene headings / sluglines, forced with a leading ``.``, with ``#n#``
  scene numbers at the start or the end
* action, forced with a leading ``!``
* character cues, forced with ``@``, extensions ``(V.O.)`` ``(CONT'D)``
* dialogue paragraphs, parentheticals, dual dialogue with a trailing ``^``
* transitions (``CUT TO:``) and forced transitions (``> CUT TO:``)
* centered text (``> text <``), lyrics (``~``)
* sections (``#``), synopses (``=``), notes (``[[ ]]``)
* boneyard comments (``/* */``), page breaks (``===``), escapes (``\\``)

Monarch reads this at **M3_script**: a real screenplay becomes the gated
scene board (see :mod:`monarch.pipelines.fountain`) and the approved board
can be exported back to Fountain.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

SCENE_HEADING = "scene_heading"
ACTION = "action"
CHARACTER = "character"
DIALOGUE = "dialogue"
PARENTHETICAL = "parenthetical"
TRANSITION = "transition"
CENTERED = "centered"
LYRIC = "lyric"
SECTION = "section"
SYNOPSIS = "synopsis"
NOTE = "note"
PAGE_BREAK = "page_break"

ELEMENT_KINDS = (
    SCENE_HEADING,
    ACTION,
    CHARACTER,
    DIALOGUE,
    PARENTHETICAL,
    TRANSITION,
    CENTERED,
    LYRIC,
    SECTION,
    SYNOPSIS,
    NOTE,
    PAGE_BREAK,
)

# --------------------------------------------------------------------------
# regexes
# --------------------------------------------------------------------------

_TITLE_KEY_RE = re.compile(r"^([A-Za-z][A-Za-z0-9 ._\-/']*):[ \t]*(.*)$")
_TITLE_KEYS = {
    "title",
    "credit",
    "author",
    "authors",
    "source",
    "draft date",
    "date",
    "contact",
    "contact info",
    "copyright",
    "notes",
}

_SLUG_PREFIX = (
    r"(?:INT\.?\s*/\s*EXT\.?|EXT\.?\s*/\s*INT\.?|I\s*/\s*E\.?|INT\.?|EXT\.?|EST\.?)"
)
_SCENE_RE = re.compile(rf"^(?P<prefix>{_SLUG_PREFIX})[ \t]+(?P<rest>\S.*)$", re.IGNORECASE)
_SCENE_NUMBER_HEAD_RE = re.compile(r"^#(?P<num>[^#\s]+)#[ \t]+(?P<rest>\S.*)$")
_SCENE_NUMBER_TAIL_RE = re.compile(r"[ \t]+#(?P<num>[^#\s]+)#[ \t]*$")

_TRANSITION_RE = re.compile(r"^[A-Z][A-Z0-9 .:'’\-]*TO:[ \t]*$")
_FADE_RE = re.compile(r"^FADE (?:IN|OUT|TO)[A-Z0-9 .:'’]*$")
_NO_LOWER_RE = re.compile(r"^[^a-z]*$")
_HAS_LETTER_RE = re.compile(r"[A-Za-z]")
_CUE_EXT_RE = re.compile(r"^(?P<name>.*?)[ \t]*\((?P<ext>[^()]*)\)[ \t]*$")
_PAGE_BREAK_RE = re.compile(r"^={3,}$")
_SECTION_RE = re.compile(r"^(?P<depth>#{1,6})[ \t]*(?P<text>.*)$")

_BONEYARD_RE = re.compile(r"/\*.*?\*/", re.DOTALL)
_NOTE_RE = re.compile(r"\[\[.*?\]\]", re.DOTALL)
_INLINE_RE = re.compile(
    r"\\(?P<esc>.)|(?P<mark>\*\*\*|\*\*|\*|_)(?P<body>.+?)(?P=mark)", re.DOTALL
)
_WS_RE = re.compile(r"[ \t]+")


def plain_text(text: str) -> str:
    """Strip boneyard, notes, escapes and emphasis markers from inline text."""
    if not text:
        return ""
    t = _BONEYARD_RE.sub(" ", text)
    t = _NOTE_RE.sub(" ", t)
    t = _INLINE_RE.sub(lambda m: m.group("esc") if m.group("esc") else m.group("body"), t)
    t = _WS_RE.sub(" ", t)
    return t.strip()


# --------------------------------------------------------------------------
# title page
# --------------------------------------------------------------------------


@dataclass
class TitlePage:
    title: str = ""
    credit: str = ""
    author: str = ""
    source: str = ""
    draft_date: str = ""
    contact: str = ""
    copyright: str = ""
    notes: str = ""
    extra: dict[str, str] = field(default_factory=dict)

    @property
    def authors(self) -> list[str]:
        parts = re.split(r"\s*(?:,|&|\band\b)\s*", self.author)
        return [p for p in (x.strip() for x in parts) if p]

    @property
    def byline(self) -> str:
        return " / ".join(self.authors) or self.author

    def is_empty(self) -> bool:
        return not any(
            [
                self.title,
                self.credit,
                self.author,
                self.source,
                self.draft_date,
                self.contact,
                self.copyright,
                self.notes,
                self.extra,
            ]
        )

    def to_dict(self) -> dict:
        d = {
            "title": self.title,
            "credit": self.credit,
            "author": self.author,
            "authors": self.authors,
            "source": self.source,
            "draft_date": self.draft_date,
            "contact": self.contact,
            "copyright": self.copyright,
            "notes": self.notes,
        }
        if self.extra:
            d["extra"] = dict(self.extra)
        return d

    def _set(self, key: str, raw_key: str, value: str) -> None:
        table = {
            "title": "title",
            "credit": "credit",
            "author": "author",
            "authors": "author",
            "source": "source",
            "draft date": "draft_date",
            "date": "draft_date",
            "contact": "contact",
            "contact info": "contact",
            "copyright": "copyright",
            "notes": "notes",
        }
        canon = table.get(key.lower())
        if canon is None:
            self.extra[raw_key.strip()] = value
        else:
            setattr(self, canon, value)


# --------------------------------------------------------------------------
# elements
# --------------------------------------------------------------------------


@dataclass
class Slugline:
    """``INT. ICE CAVE - NIGHT #3#`` broken into fields."""

    prefix: str = ""
    location: str = ""
    time_of_day: str = ""
    scene_number: str | None = None

    @property
    def is_interior(self) -> bool:
        return self.prefix.upper().startswith("INT")

    @property
    def is_exterior(self) -> bool:
        return self.prefix.upper().startswith("EXT")

    def label(self) -> str:
        head = f"{self.prefix} {self.location}".strip()
        if self.time_of_day:
            return f"{head} - {self.time_of_day}"
        return head

    def to_dict(self) -> dict:
        return {
            "prefix": self.prefix,
            "location": self.location,
            "time_of_day": self.time_of_day,
            "scene_number": self.scene_number,
            "is_interior": self.is_interior,
            "is_exterior": self.is_exterior,
        }


@dataclass
class Element:
    kind: str
    text: str
    start: int
    end: int
    forced: bool = False
    slugline: Slugline | None = None
    character: str = ""
    extension: str = ""
    dual: bool = False
    depth: int = 0

    @property
    def type(self) -> str:
        """Alias — both names are used in the wild."""
        return self.kind

    @property
    def scene_number(self) -> str | None:
        return self.slugline.scene_number if self.slugline else None

    def to_dict(self) -> dict:
        d = {
            "kind": self.kind,
            "text": self.text,
            "start": self.start,
            "end": self.end,
            "forced": self.forced,
        }
        if self.slugline is not None:
            d["slugline"] = self.slugline.to_dict()
        if self.character:
            d["character"] = self.character
        if self.extension:
            d["extension"] = self.extension
        if self.dual:
            d["dual"] = True
        if self.depth:
            d["depth"] = self.depth
        return d


@dataclass
class ScreenScene:
    """One screenplay scene (a heading plus everything under it).

    Not to be confused with :class:`monarch.schemas.Scene`, which is a
    Monarch video clip.
    """

    index: int
    heading: str = ""
    slugline: Slugline | None = None
    elements: list[Element] = field(default_factory=list)

    @property
    def scene_number(self) -> str | None:
        return self.slugline.scene_number if self.slugline else None

    @property
    def characters(self) -> list[str]:
        out: list[str] = []
        for e in self.elements:
            if e.kind == CHARACTER and e.text and e.text not in out:
                out.append(e.text)
        return out

    @property
    def dialogue(self) -> list[str]:
        return [e.text for e in self.elements if e.kind == DIALOGUE]

    @property
    def action(self) -> list[str]:
        return [e.text for e in self.elements if e.kind == ACTION]

    @property
    def words(self) -> int:
        from monarch.core.words import count_words

        return sum(count_words(e.text) for e in self.elements)

    def to_dict(self) -> dict:
        d = {
            "index": self.index,
            "heading": self.heading,
            "scene_number": self.scene_number,
            "characters": self.characters,
            "dialogue": self.dialogue,
            "action": self.action,
            "elements": [e.to_dict() for e in self.elements],
        }
        if self.slugline is not None:
            d["slugline"] = self.slugline.to_dict()
        return d


# --------------------------------------------------------------------------
# slugline helper
# --------------------------------------------------------------------------


def parse_slugline(text: str) -> Slugline | None:
    """Parse a scene heading. Returns ``None`` if it is not one."""
    t = (text or "").strip()
    scene_number: str | None = None
    m = _SCENE_NUMBER_HEAD_RE.match(t)
    if m:
        scene_number = m.group("num")
        t = m.group("rest").strip()
    m = _SCENE_RE.match(t)
    if not m:
        return None
    rest = m.group("rest").strip()
    tail = _SCENE_NUMBER_TAIL_RE.search(rest)
    if tail:
        scene_number = tail.group("num")
        rest = rest[: tail.start()].strip()
    prefix = re.sub(r"\s*/\s*", "/", m.group("prefix").upper())
    if not prefix.endswith(".") and "/" not in prefix:
        prefix += "."
    location, _, time_of_day = rest.partition(" - ")
    return Slugline(
        prefix=prefix,
        location=location.strip(),
        time_of_day=time_of_day.strip(),
        scene_number=scene_number,
    )


# --------------------------------------------------------------------------
# parser
# --------------------------------------------------------------------------


def _strip_boneyard(lines: list[str]) -> list[str]:
    out: list[str] = []
    inside = False
    for line in lines:
        if inside:
            end = line.find("*/")
            if end == -1:
                out.append("")
                continue
            inside = False
            line = line[end + 2 :]
        while True:
            start = line.find("/*")
            if start == -1:
                break
            end = line.find("*/", start + 2)
            if end == -1:
                line = line[:start]
                inside = True
                break
            line = line[:start] + line[end + 2 :]
        out.append(line)
    return out


def _character_cue(text: str) -> tuple[str, str, bool] | None:
    """Return ``(name, extension, dual)`` when the line is a character cue."""
    t = (text or "").strip()
    forced = t.startswith("@")
    if forced:
        t = t[1:].strip()
    dual = t.endswith("^")
    if dual:
        t = t[:-1].strip()
    if not t:
        return None
    name, extension = t, ""
    m = _CUE_EXT_RE.match(t)
    if m:
        name, extension = m.group("name").strip(), m.group("ext").strip()
    if not forced and (not _HAS_LETTER_RE.search(name) or not _NO_LOWER_RE.match(name)):
        return None
    return plain_text(name), plain_text(extension), dual


def _is_transition(s: str) -> bool:
    return bool(_TRANSITION_RE.match(s) or _FADE_RE.match(s))


class _Parser:
    def __init__(self, lines: list[str], source: str = "") -> None:
        self.lines = lines
        self.source = source
        self.elements: list[Element] = []

    # -- helpers ---------------------------------------------------------
    def _add(self, kind: str, text: str, start: int, end: int | None = None, **kw) -> Element:
        el = Element(kind=kind, text=text, start=start, end=end or start, **kw)
        self.elements.append(el)
        return el

    def _add_scene_heading(self, text: str, start: int, forced: bool = False) -> None:
        t = text.strip()
        scene_number: str | None = None
        m = _SCENE_NUMBER_HEAD_RE.match(t)
        if m:
            scene_number = m.group("num")
            t = m.group("rest").strip()
        tail = _SCENE_NUMBER_TAIL_RE.search(t)
        if tail:
            scene_number = tail.group("num")
            t = t[: tail.start()].strip()
        slug = parse_slugline(t)
        if slug is None:
            slug = Slugline(location=t, scene_number=scene_number)
        elif scene_number and not slug.scene_number:
            slug.scene_number = scene_number
        self._add(SCENE_HEADING, t, start, forced=forced, slugline=slug)

    # -- title page ------------------------------------------------------
    def title_page(self) -> tuple[TitlePage, int]:
        tp = TitlePage()
        n = len(self.lines)
        i = 0
        while i < n and not self.lines[i].strip():
            i += 1
        if i >= n:
            return tp, n
        m = _TITLE_KEY_RE.match(self.lines[i])
        if not m or m.group(1).strip().lower() not in _TITLE_KEYS:
            return tp, 0
        while i < n:
            line = self.lines[i]
            if not line.strip():
                j = i + 1
                while j < n and not self.lines[j].strip():
                    j += 1
                if j < n and _TITLE_KEY_RE.match(self.lines[j]):
                    i = j
                    continue
                break
            m = _TITLE_KEY_RE.match(line)
            if not m:
                break
            key, value = m.group(1).strip(), m.group(2).strip()
            values = [value] if value else []
            i += 1
            while i < n and self.lines[i].strip() and not _TITLE_KEY_RE.match(self.lines[i]):
                values.append(self.lines[i].strip())
                i += 1
            tp._set(key, key, " ".join(v for v in values if v).strip())
        return tp, i

    # -- notes -----------------------------------------------------------
    def _note(self, start: int) -> int:
        """Consume a ``[[ ]]`` note that may span several lines.

        Returns the zero-based index of the next unconsumed line.
        """
        n = self.lines
        i = start
        buf: list[str] = []
        text = n[i].strip()[2:]  # drop the opening [[
        while True:
            close = text.find("]]")
            if close != -1:
                buf.append(text[:close])
                self._add(NOTE, " ".join(b.strip() for b in buf if b.strip()), start + 1, i + 1)
                tail = text[close + 2 :].strip()
                if tail:
                    self._add(ACTION, plain_text(tail), i + 1)
                return i + 1
            buf.append(text)
            i += 1
            if i >= len(n):
                self._add(NOTE, " ".join(b.strip() for b in buf if b.strip()), start + 1, len(n))
                return len(n)
            text = n[i].strip()

    # -- dialogue block --------------------------------------------------
    def _dialogue_block(self, cue: Element) -> None:
        n = self.lines
        i = cue.end  # zero-based index of the line after the cue
        chunk: list[str] = []
        chunk_kind = ""
        chunk_start = i

        def flush() -> None:
            nonlocal chunk, chunk_kind, chunk_start
            if chunk:
                self._add(
                    chunk_kind,
                    " ".join(chunk),
                    chunk_start + 1,
                    max(chunk_start, i - 1) + 1,
                    character=cue.text,
                    extension=cue.extension,
                    dual=cue.dual,
                )
            chunk = []
            chunk_kind = ""
            chunk_start = i

        while i < len(n) and n[i].strip():
            s = n[i].strip()
            if s.startswith("[["):
                flush()
                i = self._note(i)
                chunk_start = i
                continue
            nested = _character_cue(s) if s.endswith("^") else None
            if nested:
                flush()
                name, ext, dual = nested
                sub = self._add(CHARACTER, name, i + 1, i + 1, extension=ext, dual=dual)
                self._dialogue_block(sub)
                return
            s = plain_text(s.removeprefix("\\"))
            kind = PARENTHETICAL if (s.startswith("(") and s.endswith(")")) else DIALOGUE
            if chunk and kind != chunk_kind:
                flush()
            if not chunk:
                chunk_kind = kind
            chunk.append(s)
            i += 1
        flush()

    # -- main loop -------------------------------------------------------
    def body(self, start: int) -> None:
        n = len(self.lines)
        i = start
        while i < n:
            raw = self.lines[i]
            s = raw.strip()
            if not s:
                i += 1
                continue
            start_line = i + 1
            if _PAGE_BREAK_RE.match(s):
                self._add(PAGE_BREAK, "", start_line)
                i += 1
                continue
            if s.startswith("[["):
                i = self._note(i)
                continue
            m = _SCENE_NUMBER_HEAD_RE.match(s)
            if m and parse_slugline(m.group("rest")):
                self._add_scene_heading(s, start_line)
                i += 1
                continue
            if _SECTION_RE.match(s) and not _PAGE_BREAK_RE.match(s):
                m = _SECTION_RE.match(s)
                depth = len(m.group("depth"))
                self._add(SECTION, plain_text(m.group("text")), start_line, depth=depth)
                i += 1
                continue
            if s.startswith("="):
                self._add(SYNOPSIS, plain_text(s[1:]), start_line)
                i += 1
                continue
            if s.startswith(">"):
                if s.endswith("<") and len(s) > 2:
                    self._add(CENTERED, plain_text(s[1:-1]), start_line)
                else:
                    self._add(TRANSITION, plain_text(s[1:]), start_line, forced=True)
                i += 1
                continue
            if s.startswith("."):
                self._add_scene_heading(s[1:], start_line, forced=True)
                i += 1
                continue
            if s.startswith("\\"):
                self._add(ACTION, plain_text(s[1:]), start_line)
                i += 1
                continue
            if parse_slugline(s):
                self._add_scene_heading(s, start_line)
                i += 1
                continue
            if _is_transition(s):
                self._add(TRANSITION, plain_text(s), start_line)
                i += 1
                continue
            if s.startswith("!"):
                self._add(ACTION, plain_text(s[1:]), start_line, forced=True)
                i += 1
                continue
            if s.startswith("~"):
                self._add(LYRIC, plain_text(s[1:]), start_line)
                i += 1
                continue
            cue = _character_cue(s)
            # a cue needs a non-empty next line, unless the cue is forced with @
            if cue and (s.startswith("@") or (i + 1 < n and self.lines[i + 1].strip())):
                name, ext, dual = cue
                self._add(
                    CHARACTER,
                    name,
                    start_line,
                    forced=s.startswith("@"),
                    extension=ext,
                    dual=dual,
                )
                self._dialogue_block(self.elements[-1])
                i = self.elements[-1].end
                continue
            # action paragraph: runs until a blank line
            buf = [plain_text(s)]
            end_line = start_line
            i += 1
            while i < n and self.lines[i].strip():
                nxt = self.lines[i].strip()
                if nxt.startswith(("!", "[[")):
                    break
                buf.append(plain_text(nxt))
                end_line = i + 1
                i += 1
            self._add(ACTION, " ".join(b for b in buf if b).strip(), start_line, end_line)


# --------------------------------------------------------------------------
# screenplay
# --------------------------------------------------------------------------


@dataclass
class Screenplay:
    title_page: TitlePage = field(default_factory=TitlePage)
    elements: list[Element] = field(default_factory=list)
    source: str = ""

    def of_kind(self, *kinds: str) -> list[Element]:
        wanted = set(kinds)
        return [e for e in self.elements if e.kind in wanted]

    @property
    def scene_headings(self) -> list[str]:
        return [e.text for e in self.elements if e.kind == SCENE_HEADING]

    @property
    def characters(self) -> list[str]:
        out: list[str] = []
        for e in self.elements:
            if e.kind == CHARACTER and e.text and e.text not in out:
                out.append(e.text)
        return out

    @property
    def dialogue(self) -> list[str]:
        return [e.text for e in self.elements if e.kind == DIALOGUE]

    @property
    def scenes(self) -> list[ScreenScene]:
        out: list[ScreenScene] = []
        current: ScreenScene | None = None
        for e in self.elements:
            if e.kind == SCENE_HEADING or current is None:
                current = ScreenScene(
                    index=len(out) + 1,
                    heading=e.text if e.kind == SCENE_HEADING else "",
                    slugline=e.slugline if e.kind == SCENE_HEADING else None,
                )
                out.append(current)
            current.elements.append(e)
        return out

    def counts(self) -> dict[str, int]:
        counts = {k: 0 for k in ELEMENT_KINDS}
        for e in self.elements:
            counts[e.kind] = counts.get(e.kind, 0) + 1
        return counts

    @property
    def words(self) -> int:
        from monarch.core.words import count_words

        return sum(count_words(e.text) for e in self.elements)

    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "title_page": self.title_page.to_dict(),
            "counts": {k: v for k, v in self.counts().items() if v},
            "characters": self.characters,
            "words": self.words,
            "scenes": [s.to_dict() for s in self.scenes],
            "elements": [e.to_dict() for e in self.elements],
        }

    def summary(self) -> str:
        tp = self.title_page
        rows = [f"fountain: {self.source or '<text>'}"]
        for label, value in (
            ("title", tp.title),
            ("credit", tp.credit),
            ("author", tp.author),
            ("draft date", tp.draft_date),
            ("contact", tp.contact),
        ):
            if value:
                rows.append(f"{label}: {value}")
        counts = self.counts()
        rows.append("elements: " + ", ".join(f"{k}={v}" for k, v in counts.items() if v))
        rows.append(f"scenes: {len(self.scenes)} | dialogue lines: {counts.get(DIALOGUE, 0)} | words: {self.words}")
        if self.characters:
            rows.append("characters: " + ", ".join(self.characters))
        return "\n".join(rows)


def parse(text: str, *, source: str = "") -> Screenplay:
    """Parse Fountain text into a :class:`Screenplay`."""
    if text is None:
        raise ValueError("fountain text is None")
    clean = text.lstrip("\ufeff").replace("\r\n", "\n").replace("\r", "\n")
    lines = _strip_boneyard(clean.split("\n"))
    p = _Parser(lines, source=source)
    title_page, i = p.title_page()
    p.body(i)
    return Screenplay(title_page=title_page, elements=p.elements, source=source)


def parse_file(path: str | Path) -> Screenplay:
    """Parse a ``.fountain`` file (utf-8, BOM tolerated)."""
    p = Path(path)
    text = p.read_text(encoding="utf-8-sig")
    return parse(text, source=str(p))
