"""Humanize pass — strip the AI-writer smell from Monarch scripts.

Mined from blader/humanizer (Wikipedia's AI-writing guide concept) and
documentary VO craft. Three stages, fail-closed honesty:

1. DETECT  — regex bank of AI-tell phrases + statistical tells
   (uniform sentence length, em-dash overuse, "not just X but Y" shapes)
2. STRIP   — mechanical removal only (filler phrases, filler adverbs,
   doubled punctuation). Style is never auto-invented.
3. REPORT  — what a human (or the Script Doctor) must rewrite by hand.

The score is AI-signs per 100 words. 0.0 is clean; the gate threshold is
configurable (default 1.5). This is the cure for "robot ko bola do bol de"
scripts — the machine phrases die here, the human rhythm stays.
"""

from __future__ import annotations

import re
import statistics
from dataclasses import dataclass, field

from monarch.core.words import count_words, tokenize

#: (regex, why) — mechanical strip list. Case-insensitive, multiline.
STRIP_PATTERNS: list[tuple[str, str]] = [
    (r"\bimagine a world where\b", "AI-tell opener"),
    (r"\bin today'?s (fast[- ]paced |modern |digital )?world\b", "AI-tell opener"),
    (r"\bin the (realm|world|landscape) of\b", "AI-tell frame"),
    (r"\bwhen it comes to\b", "filler frame"),
    (r"\bat the end of the day\b", "filler frame"),
    (r"\bit'?s (important|worth) (to note|noting) (that )?\b", "filler frame"),
    (r"\bin conclusion\b", "essay tell"),
    (r"\b(furthermore|moreover|additionally)\b[ ,]", "essay connective"),
    (r"\blook no further\b", "ad-speak"),
    (r"\b(embark on|on a journey)\b", "AI-tell journey"),
    (r"\bcutting[- ]edge\b", "AI-tell adjective"),
    (r"\bseamless(ly)?\b", "AI-tell adjective"),
    (r"\belevate your\b", "ad-speak"),
    (r"\ba testament to\b", "AI-tell frame"),
    (r"\ba rich tapestry of\b", "AI-tell metaphor"),
    (r"\bnavigate the (complexities|challenges|landscape)\b", "AI-tell metaphor"),
    (r"\bever[- ]evolving\b", "AI-tell adjective"),
    (r"\bbustling\b", "AI-tell adjective"),
    (r"\bvibrant\b", "AI-tell adjective"),
    (r"\bhidden gem\b", "AI-tell cliché"),
    (r"\bthe (key|secret) (is|lies in)\b", "AI-tell frame"),
    (r"\bwhether you'?re a\b", "AI-tell hedge"),
    (r"\bplays a (crucial|vital|significant) role\b", "AI-tell frame"),
    (r"\bit goes without saying\b", "filler frame"),
    (r"\ball things considered\b", "filler frame"),
    (r"\ball in all\b", "filler frame"),
    (r"\bin a nutshell\b", "filler frame"),
    (r"\ballow me to\b", "stiff frame"),
    (r"\bwe (can't|cannot) stress enough\b", "hype frame"),
    (r"\byour (one[- ]stop|go[- ]to)\b", "ad-speak"),
]

#: softening rewrites — word-level, meaning-preserving
WORD_FIXES: list[tuple[str, str]] = [
    # inflated verbs — all inflections, grammar stays intact
    (r"\butiliz(e|es|ed|ing)\b", lambda m: {"e": "use", "es": "uses",
        "ed": "used", "ing": "using"}[m.group(1)]),
    (r"\bcommenc(e|es|ed|ing)\b", lambda m: {"e": "start", "es": "starts",
        "ed": "started", "ing": "starting"}[m.group(1)]),
    (r"\bfacilitat(e|es|ed|ing)\b", lambda m: {"e": "help", "es": "helps",
        "ed": "helped", "ing": "helping"}[m.group(1)]),
    (r"\bdelve into\b", "dig into"),
    (r"\bdelv(e|es|ed|ing)\b", lambda m: {"e": "dig", "es": "digs",
        "ed": "dug", "ing": "digging"}[m.group(1)]),
    (r"\bunleash\b", "let loose"),
    (r"\brevolutioniz(e|es|ed|ing)\b", lambda m: {
        "e": "change", "es": "changes", "ed": "changed",
        "ing": "changing"}[m.group(1)]),
    (r"\bunlock the (power|secrets?) of\b", "open"),
    (r"\bmaster the art of\b", "learn"),
    # AI-noun tells — replaced, never deleted (no article orphans)
    (r"\btapestry\b", "story"),
    (r"\b(symphony|orchestra) of\b", "mix of"),
    (r"\brealm of\b", "world of"),
    (r"\brealm\b", "field"),
    (r"\blandscape of\b", "picture of"),
    (r"\bmyriad (of )?\b", "many "),
    (r"\bplethora of\b", "plenty of"),
    (r"\bgame-changer\b", "turning point"),
    (r"\bcornerstone\b", "base"),
    (r"\btestament to\b", "proof of"),
    (r"\bbeacon of\b", "guide to"),
    (r"\bpivotal\b", "key"),
    (r"\bparamount\b", "critical"),
    (r"\buntangling\b", "unraveling"),
    # stiff connectives
    (r"\bprior to\b", "before"),
    (r"\bsubsequent to\b", "after"),
    (r"\bin order to\b", "to"),
    (r"\bdue to the fact that\b", "because"),
    (r"\bvery very\b", "very"),
    (r"\breally really\b", "really"),
]

#: "not just X but Y" / "it's not about X, it's about Y" — count only
SHAPE_PATTERNS: list[tuple[str, str]] = [
    (r"\bnot just .{3,40},? but\b", "not-just-but shape"),
    (r"\bit'?s not about .{3,40},? it'?s about\b", "not-about shape"),
    (r"\bthis isn'?t .{3,40};? it'?s\b", "isnt-it shape"),
    (r"\bnot just [^—,;.]{3,40} — (it'?s|this is|that'?s)\b",
     "not-just-dash shape"),
]

EMDASH = re.compile(r"—|\s–\s")
MULTI_SPACE = re.compile(r" {2,}")
SPACE_PUNCT = re.compile(r" +([,.!?;:])")

DEFAULT_GATE = 1.5  # AI-signs per 100 words


@dataclass
class HumanizeReport:
    original_words: int
    final_words: int
    signs_before: float
    signs_after: float
    stripped: list[str] = field(default_factory=list)
    flagged: list[str] = field(default_factory=list)   # needs human rewrite
    notes: list[str] = field(default_factory=list)     # statistical tells

    @property
    def clean(self) -> bool:
        return self.signs_after <= DEFAULT_GATE

    def summary(self) -> str:
        status = "CLEAN" if self.clean else "STILL ROBOTIC — rewrite flagged lines"
        return (f"{status} | signs {self.signs_before:.2f} -> {self.signs_after:.2f} "
                f"/100w | stripped {len(self.stripped)}, flagged {len(self.flagged)}, "
                f"notes {len(self.notes)}")


def _find_hits(text: str) -> list[tuple[str, str, str]]:
    """(matched_text, why, kind) for every pattern hit."""
    hits: list[tuple[str, str, str]] = []
    for pat, why in STRIP_PATTERNS:
        for m in re.finditer(pat, text, re.I):
            hits.append((m.group(0), why, "strip"))
    for pat, _fix in WORD_FIXES:
        for m in re.finditer(pat, text, re.I):
            hits.append((m.group(0), "inflated word", "fix"))
    for pat, why in SHAPE_PATTERNS:
        for m in re.finditer(pat, text, re.I):
            hits.append((m.group(0), why, "shape"))
    return hits


def _sentence_lengths(text: str) -> list[int]:
    return [count_words(s) for s in re.split(r"[.!?]+", text) if s.strip()]


def _uniformity_note(lens: list[int]) -> str | None:
    if len(lens) < 4:
        return None
    stdev = statistics.pstdev(lens)
    mean = statistics.fmean(lens) or 1.0
    if stdev / mean < 0.35:
        return (f"uniform sentence rhythm (len stdev/mean {stdev / mean:.2f}) — "
                "mix short punches with long descriptive lines")
    return None


def score_text(text: str) -> tuple[float, list[tuple[str, str, str]], list[str]]:
    """AI-signs per 100 words + every hit + statistical notes."""
    words = max(1, count_words(text))
    hits = _find_hits(text)
    notes: list[str] = []
    if EMDASH.search(text) and len(EMDASH.findall(text)) > max(1, words // 120):
        notes.append("em-dash overuse — AI punctuation tell")
    lens = _sentence_lengths(text)
    uni = _uniformity_note(lens)
    if uni:
        notes.append(uni)
    if lens:
        mean = statistics.fmean(lens)
        if mean > 24:
            notes.append(f"average sentence {mean:.0f} words — too long for the ear")
    density = len(hits) * 100 / words
    return round(density, 2), hits, notes


def strip_hits(text: str) -> tuple[str, list[str]]:
    """Mechanical removal — no style invention. Returns (clean, stripped)."""
    out = text
    stripped: list[str] = []
    for pat, why in STRIP_PATTERNS:
        new = re.sub(pat, " ", out, flags=re.I)
        if new != out:
            stripped.append(f"{why}: /{re.search(pat, out, re.I).group(0).strip()}/")
            out = new
    for pat, fix in WORD_FIXES:
        new = re.sub(pat, fix, out, flags=re.I)
        if new != out:
            stripped.append(f"word fix: {pat}")
            out = new
    out = MULTI_SPACE.sub(" ", out)
    out = SPACE_PUNCT.sub(r"\1", out)
    out = re.sub(r"\s+([.!?])", r"\1", out)
    out = _tidy(out)
    return out.strip(), stripped


def _tidy(text: str) -> str:
    """Grammar repair after mechanical strips — no dangling commas."""
    out = re.sub(r"^\s*(?:,|;|:)\s*", "", text)
    out = re.sub(r"([.!?])\s*[,;:]\s*", r"\1 ", out)
    out = re.sub(r"(^|[.!?]\s+)([a-z])",
                 lambda m: m.group(1) + m.group(2).upper(), out)
    out = re.sub(r"\b(a|an|the)\s+(that|which|,|\.|;|:|!|\?)",
                 r"\2", out)
    out = re.sub(r"\s{2,}", " ", out)
    return out


def humanize(text: str, *, gate: float = DEFAULT_GATE) -> tuple[str, HumanizeReport]:
    """Full pass: strip mechanical tells, report what needs a human."""
    words0 = count_words(text)
    signs0, hits0, notes0 = score_text(text)
    clean, stripped = strip_hits(text)
    signs1, hits1, notes1 = score_text(clean)
    flagged = [m for m, why, kind in hits1 if kind in ("strip", "shape")]
    report = HumanizeReport(
        original_words=words0,
        final_words=count_words(clean),
        signs_before=signs0,
        signs_after=signs1,
        stripped=stripped,
        flagged=flagged,
        notes=notes0 + [n for n in notes1 if n not in notes0],
    )
    if signs1 > gate:
        report.notes.append(
            f"above gate ({signs1:.2f} > {gate}) — Script Doctor rewrite, never ship"
        )
    return clean, report
