from __future__ import annotations

from monarch.schemas import Channel, Idea
from monarch.visual.negatives_text import NEGATIVE_IMAGE

VARIANTS = (
    "single-character close reaction, huge face, one emotion",
    "character versus giant object, scale joke",
    "before/after split, left problem right twist, no text",
    "object-hero filling the frame, character small reacting",
    "wide genre-range pose, empty upper third for editor headline",
)


def five_variants(idea: Idea, channel: Channel) -> list[dict]:
    lock = channel.character_lock or "the locked stickman character"
    out = []
    for i, v in enumerate(VARIANTS, 1):
        prompt = (
            f"{lock}, {v}, about {idea.title}, high contrast flat doodle, "
            f"accent {channel.accent_color}, generous empty space for a headline, "
            "no text in the image"
        )
        out.append(
            {
                "id": i,
                "prompt": prompt,
                "negative": NEGATIVE_IMAGE,
                "add_in_capcut": idea.title[:42],
            }
        )
    return out
