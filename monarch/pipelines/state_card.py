"""State cards — what a Monarch state actually demands (stop + commands).

Cards carry no invented niche, no fake data: they only state the law of the
state and the commands that operate it.
"""

from __future__ import annotations

from monarch.core.scene_math import compute_math, maths_line
from monarch.core.state_machine import Run


def m3_card() -> dict:
    """M3_script: Fountain screenplay → gated numbered scene board."""
    wait = Run(state="M3_script").wait_prompt()
    example = maths_line(compute_math(60))
    law = [
        "numbered scenes, quoted line, [n words] exact — never pad, never fake a count",
        "duration is words / speaking_wps; the first clip is clamped to first_clip_s",
        "fail-closed gate: scene without a visual or a retention job does not ship",
        "visual direction lives in '::visual:: text' so the visual never counts as words",
        "no render, no VO before the HAAN gate — this state only produces the board",
    ]
    commands = [
        "monarch m3",
        "monarch fountain script.fountain --json",
        "monarch screen-script script.fountain --length short --board-out board.json",
        "monarch script-fountain board.json --title '...' --out script.fountain",
    ]
    text = "\n".join(
        [
            "STATE M3_script — deliverable: numbered scenes, quoted line, [n words] exact",
            f"maths: {example}",
            "law:",
            *[f"  - {row}" for row in law],
            "commands:",
            *[f"  {row}" for row in commands],
            f"STOP — WAIT: {wait}",
        ]
    )
    return {
        "state": "M3_script",
        "deliverable": "numbered scenes, quoted line, [n words] exact",
        "wait": wait,
        "law": law,
        "commands": commands,
        "maths_example": example,
        "text": text,
    }
