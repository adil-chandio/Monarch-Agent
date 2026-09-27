"""Chunk planner - MONARCH V2 miss #4 (the repetition plague).

The Every Bear session split a topic across render chunks (Sun bear
28-36 in chunk 1, 37-46 in chunk 2) and the operator heard repetition:
the story re-told itself at every seam. The fix became law:

  * chunks start at NEW topic boundaries and end on COMPLETE topics
  * a topic is NEVER split across chunks (fail-closed, not best-effort)
  * ~38-46 beats per chunk (2-minute render unit) keeps workspace fat
    off the disk (incremental merge pattern)
  * every seam gets gap 0.85 s + whoosh+riser cues so the new topic
    lands as a fresh breath, not a continuation

Deterministic, fail-closed, stdlib-only - suite-tested in
tests/test_monarch_v2.py.
"""

from __future__ import annotations

MAX_BEATS = 46          # the 2-minute chunk unit from the Bear session
BOUNDARY_GAP_S = 0.85   # 0.38s felt like a stumble; 0.85s = new breath
BOUNDARY_SFX = ("whoosh", "riser")


def plan_chunks(groups: list[dict], *, max_beats: int = MAX_BEATS,
                gap_s: float = BOUNDARY_GAP_S) -> list[dict]:
    """Group COMPLETE topics into render chunks.

    ``groups`` = [{"topic": str, "beats": [int, ...]}, ...] in story
    order (hook/verdict are topics too). Returns chunks of whole topics:

        [{"beats": [...], "topics": [...], "first": int, "last": int,
          "boundary": {"gap_s": 0.85, "sfx": ["whoosh", "riser"]}|None}]

    Raises ValueError if a single topic exceeds ``max_beats`` (split a
    topic = the repetition bug - refuse the plan instead).
    """
    chunks: list[dict] = []
    cur: dict | None = None
    for g in groups:
        topic = str(g.get("topic", "")).strip()
        beats = list(g.get("beats", []))
        if not topic or not beats:
            raise ValueError(f"bad topic group: {g!r} (topic + beats needed)")
        if len(beats) > max_beats:
            raise ValueError(
                f"topic {topic!r} has {len(beats)} beats > max {max_beats} - "
                "splitting a topic across chunks is the repetition bug "
                "(MONARCH V2 miss #4); tighten the beat plan instead")
        if cur and len(cur["beats"]) + len(beats) > max_beats:
            chunks.append(cur)
            cur = None
        if cur is None:
            cur = {"beats": [], "topics": []}
        cur["beats"].extend(beats)
        cur["topics"].append(topic)
    if cur:
        chunks.append(cur)
    out: list[dict] = []
    for i, c in enumerate(chunks):
        out.append({
            "beats": c["beats"],
            "topics": c["topics"],
            "first": c["beats"][0],
            "last": c["beats"][-1],
            "boundary": None if i == 0 else
            {"gap_s": gap_s, "sfx": list(BOUNDARY_SFX)},
        })
    return out


def verify_no_split(groups: list[dict], chunks: list[dict]) -> None:
    """Edit-verify (law 8): every topic lives in EXACTLY one chunk."""
    seen: dict[str, int] = {}
    for i, c in enumerate(chunks, 1):
        for t in c["topics"]:
            if t in seen:
                raise ValueError(
                    f"topic {t!r} appears in chunks {seen[t]} and {i} - "
                    "the repetition bug re-planned itself")
            seen[t] = 1
    planned = [g["topic"] for g in groups]
    missing = [t for t in planned if t not in seen]
    if missing:
        raise ValueError(f"topics lost by the planner: {missing}")
