from __future__ import annotations

from monarch.schemas import Idea, Scene


def listing(idea: Idea, scenes: list[Scene], title: str) -> dict:
    lines = [f"{title}", "", idea.hook, ""]
    t = 0.0
    chapters = []
    for s in scenes:
        start = s.t_start if s.t_end else t
        mm, ss = divmod(int(start), 60)
        chapters.append(f"{mm}:{ss:02d} Scene {s.id}")
        t = s.t_end or (t + 3.5)
    tags = [w.lower() for w in idea.title.split() if len(w) > 2][:12]
    if idea.itch:
        tags.append(idea.itch.lower())
    return {
        "title": title,
        "description": "\n".join(lines + chapters),
        "tags": tags,
        "privacy": "private",
    }
