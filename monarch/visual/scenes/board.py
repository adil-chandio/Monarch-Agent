from __future__ import annotations

from monarch.core.fit_line import fit_words
from monarch.core.scene_math import compute_math
from monarch.core.words import count_words
from monarch.schemas import Scene


def board_from_lines(lines: list[str], total_s: float) -> list[Scene]:
    m = compute_math(total_s)
    if len(lines) != m.scenes:
        raise ValueError(f"need {m.scenes} lines, got {len(lines)}")
    scenes: list[Scene] = []
    t = 0.0
    for i, raw in enumerate(lines, 1):
        line = fit_words(raw, m.words_per_clip)
        dur = m.first_clip_s if i == 1 else m.clip_s
        scenes.append(
            Scene(
                id=i,
                vo_line=line,
                visual="gesture",
                word_count=count_words(line),
                t_start=t,
                t_end=t + dur,
                retention_job="hook" if i == 1 else ("payoff" if i == len(lines) else "advance"),
            )
        )
        t += dur
    return scenes
