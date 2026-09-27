from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

DEFAULT = Path(__file__).resolve().parents[1] / "self_improve" / "lessons.md"


def record(miss: str, rule: str, path: Path = DEFAULT) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text("# Lessons\n\n", encoding="utf-8")
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with path.open("a", encoding="utf-8") as f:
        f.write(f"- {stamp} | miss: {miss} | 3x rule: {rule}\n")
