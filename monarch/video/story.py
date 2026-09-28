"""Story engine — the difference between a script and a STORY.

Carousel-mined refinements (the ones our playbook lacked), now law:

* **PARTIAL payoff** — deliver new information but leave the total answer
  open; the payoff itself spawns the next loop (N3.5).
* **Re-hook BEFORE the full answer** — the next question enters before the
  current one completes; the brain never gets closure-click space.
* **Information tension** — every scene must carry NEW information; a cut
  without new info is visual spam, not pacing (L3 refinement).
* **Prosody direction** — every scene carries a delivery note ([lower],
  PAUSE markers) so the VO is performed, not read.
* **Narrative arc** — hook → setup → raise → turn → partial → sting →
  climax → resolution; facts ride the story, never float loose.
* **Ear rules** — contractions, short/long sentence alternation, concrete
  verbs; checked by ear_check() and reported, not silently rewritten.
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass
from monarch.core.words import count_words

#: role -> (arc beat, prosody directive, partial-payoff flag)
ARC: dict[str, tuple[str, str, bool]] = {
    "hook": ("COLD OPEN — drop us mid-event, no preamble",
             "[urgent, close to the mic]", False),
    "tease": ("RAISE — the strange detail that doesn't fit",
              "[curious, slightly faster]", False),
    "payoff": ("PARTIAL PAYOFF — one proof lands, the bigger one stays hidden",
               "[grounded, let the number breathe]", True),
    "value-debt": ("GIVE — hand the viewer something usable, no strings",
                   "[warm, unhurried]", False),
    "silence-sting": ("THE DROP — 0.3s of nothing, then the one fact",
                      "[lower, slower — almost a whisper]", False),
    "payoff+cua": ("CLIMAX + HAND — close the arc, open the next door",
                   "[resolute, lift at the end]", False),
}

#: partial-payoff tails — the payoff deliberately incomplete
PARTIAL_TAILS = [
    "but that was the small part",
    "and the real reason sits deeper",
    "yet one thing still refuses to add up",
    "though what came next rewrote the file",
]

#: re-hook questions — enter BEFORE the answer completes
REHOOKS = [
    "so why did everyone look away",
    "then who closed the file",
    "but what was it hiding",
    "so where did the rest go",
]

_EAR_FILLERS = ("very", "just", "actually", "basically", "literally",
                "simply", "quite")
_WEAK_VERBS = ("is", "are", "was", "were", "be", "been", "being")


def plan_arc(roles: list[str]) -> list[dict]:
    """roles -> per-scene {beat, prosody, partial, rehook} plan."""
    plan: list[dict] = []
    for i, role in enumerate(roles):
        beat, prosody, partial = ARC.get(role, ("ADVANCE — move the story",
                                                "[steady]", False))
        entry = {"beat": beat, "prosody": prosody, "partial": partial}
        if partial:
            # N3.5: payoff lands partial + the re-hook enters right after
            entry["rehook"] = REHOOKS[i % len(REHOOKS)]
        plan.append(entry)
    return plan


def partialize(line: str, rng) -> str:
    """Shape a payoff line into a PARTIAL payoff (carousel law)."""
    base = line.rstrip()
    for tail in PARTIAL_TAILS:
        cand = f"{base} {tail}"
        if count_words(cand) > count_words(base):
            return cand
    return base


def rehook_into(line: str, rehook: str | None) -> str:
    """Append the next question before the answer fully lands."""
    if not rehook:
        return line
    base = line.rstrip().rstrip(".")
    return f"{base} — {rehook}?"


def ear_check(text: str) -> list[str]:
    """Write-for-the-ear audit — reported honestly, never auto-mangled."""
    notes: list[str] = []
    sentences = [s for s in __import__("re").split(r"[.!?]+", text) if s.strip()]
    lens = [count_words(s) for s in sentences]
    if lens:
        var = statistics.pstdev(lens)
        mean = statistics.fmean(lens) or 1.0
        if var / mean < 0.3:
            notes.append(
                f"rhythm too uniform (stdev/mean {var / mean:.2f}) — "
                "alternate short punches with longer lines")
        long_ones = [n for n in lens if n > 24]
        if long_ones:
            notes.append(f"{len(long_ones)} sentence(s) over 24 words — cut in two")
    words = [w.lower().strip(".,!?;:") for w in text.split()]
    fillers = sum(1 for w in words if w in _EAR_FILLERS)
    if fillers > max(2, len(words) // 60):
        notes.append(f"{fillers} filler adverbs — ears skip them, cut them")
    contr = sum(1 for w in words if "'" in w)
    if len(words) > 30 and contr == 0:
        notes.append("zero contractions — nobody talks like that; "
                     "use you'll / it's / doesn't")
    weak = sum(1 for w in words if w in _WEAK_VERBS)
    if len(words) > 40 and weak / max(1, len(words)) > 0.18:
        notes.append("too many bare is/was verbs — use concrete verbs")
    return notes


def prosody_note(entry: dict) -> str:
    """Fountain [[VO: ...]] note for a scene."""
    parts = [entry["prosody"]]
    if entry.get("partial"):
        parts.append("pause 0.3s after the proof")
    if entry.get("rehook"):
        parts.append(f"rehook: {entry['rehook']}?")
    return " | ".join(parts)
