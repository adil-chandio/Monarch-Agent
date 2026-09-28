"""G3/L10 - generation budget planner (10 images / 10 speech per turn).

The live session burned a turn by asking for 18 frames at once (G3).
Never again: plan the batches BEFORE generating. Images and speech each
cap at ``per_turn`` (platform limit); the plan is deterministic.
"""

from __future__ import annotations

PER_TURN = 10


def plan_batches(images: int, speech: int, *,
                 per_turn: int = PER_TURN) -> list[dict]:
    """Split (images, speech) into per-turn batches within the caps."""
    if images < 0 or speech < 0:
        raise ValueError("budgets must be >= 0")
    if per_turn <= 0:
        raise ValueError("per_turn must be > 0")
    turns: list[dict] = []
    left_i, left_s = images, speech
    n = 1
    while left_i > 0 or left_s > 0:
        take_i = min(per_turn, left_i)
        left_i -= take_i
        take_s = min(per_turn, left_s)
        left_s -= take_s
        turns.append({"turn": n, "images": take_i, "speech": take_s})
        n += 1
    if not turns:
        turns.append({"turn": 1, "images": 0, "speech": 0})
    return turns
