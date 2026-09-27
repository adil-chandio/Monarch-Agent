from __future__ import annotations

import json
import re

from monarch.core.gates import GateFail, gate_idea
from monarch.intel.gemini import generate
from monarch.schemas import Idea

SYSTEM = (
    "You are Monarch idea hunt. Return ONLY a JSON array of 10 objects: "
    "title, hook, itch, visual_anchor. Facts must be real/researchable. "
    "No Top 10 lists, no subscribe, no conspiracy, no fake studies. "
    "Titles must force a click via unfinished/WTF/incongruity while remaining true. "
    "itch is one of: unfinished, incongruity, forbidden, self-threat, status, fomo, proof-shock."
)


def _parse_ideas(text: str) -> list[Idea]:
    m = re.search(r"\[.*\]", text, re.S)
    if not m:
        raise ValueError("gemini did not return a JSON array")
    raw = json.loads(m.group(0))
    ideas = []
    for row in raw:
        ideas.append(
            Idea(
                title=str(row.get("title", "")).strip(),
                hook=str(row.get("hook", "")).strip(),
                itch=str(row.get("itch", "")).strip(),
                visual_anchor=str(row.get("visual_anchor", "")).strip(),
            )
        )
    return ideas


def hunt(niche: str, winner_titles: list[str] | None = None) -> list[Idea]:
    winners = "\n".join(f"- {t}" for t in (winner_titles or [])[:12])
    prompt = (
        f"Niche: {niche}\nCurrent winning titles (do not clone, elevate 5x):\n{winners or '- none'}\n"
        "Produce 10 original idea objects."
    )
    text = generate(prompt, SYSTEM)
    ok: list[Idea] = []
    for idea in _parse_ideas(text):
        try:
            gate_idea(idea)
        except GateFail:
            continue
        ok.append(idea)
    if len(ok) < 3:
        raise RuntimeError(f"only {len(ok)} ideas passed gates")
    return ok
