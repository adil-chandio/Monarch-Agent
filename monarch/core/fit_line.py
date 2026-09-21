from __future__ import annotations

from monarch.core.words import count_words, tokenize


def fit_words(line: str, n: int) -> str:
    """Trim to exactly n words. Never pad. Too short = error."""
    tokens = tokenize(line)
    if len(tokens) < n:
        raise ValueError(f"cannot pad: have {len(tokens)} need {n}")
    out = " ".join(tokens[:n])
    if count_words(out) != n:
        raise ValueError(f"fit produced {count_words(out)} not {n}")
    return out
