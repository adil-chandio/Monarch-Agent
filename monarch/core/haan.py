"""Full generate/render/upload does not run without operator HAAN."""

from __future__ import annotations

_YES = frozenset({"haan", "han", "yes", "ok", "lock"})


def require_haan(operator: str, action: str) -> None:
    token = (operator or "").strip().lower()
    if token not in _YES:
        raise PermissionError(
            f"HAAN required before {action}. Ask: full {action} — haan?"
        )
