from __future__ import annotations

import math

from monarch.schemas import SceneMath


def compute_math(
    total_s: float,
    clip_s: float = 3.5,
    speaking_wps: float = 2.2,
    first_clip_s: float = 2.5,
) -> SceneMath:
    if total_s <= 0 or clip_s <= 0:
        raise ValueError("duration and clip length must be > 0")
    body = max(total_s - first_clip_s, clip_s)
    scenes = 1 + max(1, math.ceil(body / clip_s))
    words = max(4, int(round(clip_s * speaking_wps)))
    # Flow-class hard cap that caused most re-rolls in the source engine
    words = min(words, 7) if clip_s <= 4.0 else words
    return SceneMath(
        total_s=total_s,
        clip_s=clip_s,
        scenes=scenes,
        words_per_clip=words,
        first_clip_s=first_clip_s,
        speaking_wps=speaking_wps,
    )


def maths_line(m: SceneMath) -> str:
    return (
        f"{m.total_s:.0f}s | first clip {m.first_clip_s}s | "
        f"body clips {m.clip_s}s | {m.scenes} scenes | "
        f"{m.words_per_clip} words/clip exact"
    )
