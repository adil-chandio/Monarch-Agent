from __future__ import annotations

DEFAULTS = {
    "niche": "Educational Explainer",
    "language": "en",
    "aspect": "16:9",
    "vo_mode": "SILENT",
    "length_s": "60",
    "voice_lock": (
        "spoken by a warm friendly male narrator in his early thirties with a "
        "neutral North American accent, medium-low pitch, relaxed conversational "
        "pace, clear articulation, gentle enthusiasm, no dramatic emphasis and no announcer tone"
    ),
}


def missing(item: str) -> str:
    for k in DEFAULTS:
        if item == k or item.startswith(k):
            return f"Using default for {item}."
    return f"This is missing, could you provide it: {item}."


def require_fields(data: dict, keys: list[str]) -> list[str]:
    hard = []
    for k in keys:
        if str(data.get(k, "")).strip():
            continue
        if k in DEFAULTS:
            continue
        hard.append(missing(k))
    return hard
