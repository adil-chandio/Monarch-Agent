from __future__ import annotations


def missing(item: str) -> str:
    return f"This is missing, could you provide it: {item}."


def require_fields(data: dict, keys: list[str]) -> list[str]:
    return [missing(k) for k in keys if not str(data.get(k, "")).strip()]
