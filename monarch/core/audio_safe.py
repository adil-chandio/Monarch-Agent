from __future__ import annotations

import re

REPLACEMENTS = (
    (re.compile(r"\bhammer\b", re.I), "mallet"),
    (re.compile(r"\bnail\b", re.I), "peg"),
    (re.compile(r"\bexplosion\b", re.I), "concussive burst of light"),
    (re.compile(r"\bexplode\b", re.I), "burst of light"),
    (re.compile(r"\bgunshot\b", re.I), "sharp clap of air"),
    (re.compile(r"\bscream\b", re.I), "sudden breath-cut"),
)


def audio_safe(text: str) -> str:
    out = text
    for pat, b in REPLACEMENTS:
        out = pat.sub(b, out)
    return out
