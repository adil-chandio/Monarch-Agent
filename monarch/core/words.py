from __future__ import annotations

import re

_WORD = re.compile(r"[A-Za-z0-9']+")


def tokenize(line: str) -> list[str]:
    return _WORD.findall(line or "")


def count_words(line: str) -> int:
    return len(tokenize(line))


def assert_word_count(line: str, expected: int) -> str:
    n = count_words(line)
    if n != expected:
        raise ValueError(f"word count {n} != {expected}: {line!r}")
    return line
