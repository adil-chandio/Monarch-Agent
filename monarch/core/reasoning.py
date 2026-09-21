from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Decision:
    action: str
    why: str
    why_not: list[str]
    viewer_pov: str
    writer_pov: str
    gate_pass: bool


def decide(
    action: str,
    why: str,
    viewer: str,
    writer: str,
    *,
    why_not: list[str] | None = None,
    gate_pass: bool = False,
) -> Decision:
    return Decision(
        action=action,
        why=why,
        why_not=why_not or [],
        viewer_pov=viewer,
        writer_pov=writer,
        gate_pass=gate_pass,
    )
