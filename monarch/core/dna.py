"""Viral DNA shape — rewritten from vendor skill, elevate-first."""

from __future__ import annotations

from monarch.schemas import ViralDNA


DNA_KEYS = (
    "hook_architecture",
    "retention_loops",
    "sentence_rhythm",
    "structure",
    "template",
    "elevate_notes",
)


def empty_dna(channel: str) -> ViralDNA:
    return ViralDNA(
        channel=channel,
        elevate_notes="Same itch, new picture, unpaid debt, 5x density. Never clone.",
    )


def dna_complete(d: ViralDNA) -> bool:
    return all(
        [
            d.hook_architecture,
            d.retention_loops,
            d.sentence_rhythm,
            d.structure,
            d.template,
        ]
    )
