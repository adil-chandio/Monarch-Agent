from __future__ import annotations

CHECKS = (
    "research_not_skipped",
    "gates_not_hidden",
    "ijazat_asked",
    "no_clone_or_top10",
    "duration_matches_vo",
)


def qc(notes: dict[str, bool]) -> list[str]:
    return [k for k in CHECKS if not notes.get(k, False)]
