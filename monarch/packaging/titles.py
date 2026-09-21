from __future__ import annotations

from monarch.core.gates import GateFail, gate_title
from monarch.schemas import GENERIC_TITLE_BANS, Idea


def score_title(title: str) -> float:
    t = title.strip()
    low = t.lower()
    s = 0.0
    if 18 <= len(t) <= 60:
        s += 3
    elif len(t) <= 70:
        s += 1
    if any(b in low for b in GENERIC_TITLE_BANS):
        s -= 10
    if "?" in t:
        s += 1.5
    if any(ch.isdigit() for ch in t) and "top 10" not in low:
        s += 1
    if t[:1].isupper():
        s += 0.5
    words = t.split()
    if 4 <= len(words) <= 12:
        s += 1
    return s


def rank_titles(candidates: list[str], thumb: str, paid: bool) -> list[str]:
    kept: list[str] = []
    for c in candidates:
        try:
            gate_title(c, thumb, paid)
        except GateFail:
            continue
        kept.append(c)
    return sorted(kept, key=score_title, reverse=True)


def titles_from_idea(idea: Idea, extras: list[str] | None = None) -> list[str]:
    pool = [idea.title, *(extras or [])]
    return rank_titles(pool, idea.visual_anchor or "thumb", True)
