from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from monarch.schemas import Channel, Idea, Scene


def package_for_human_upload(
    path: str | Path,
    *,
    idea: Idea,
    titles: list[str],
    listing: dict,
    thumbs: list[dict],
    scenes: list[Scene],
    prompts: list[str],
    channel: Channel,
) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    doc = {
        "upload": "OPERATOR — agent does not upload",
        "channel": asdict(channel),
        "idea": asdict(idea),
        "titles_ranked": titles,
        "listing": listing,
        "thumbs": thumbs,
        "scenes": [asdict(s) for s in scenes],
        "animation_prompts": prompts,
        "capcut": "Add headlines from thumbs[].add_in_capcut. No on-screen text in gen.",
    }
    p.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    return p
