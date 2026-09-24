"""L1/G2 - environment readiness, honest fail-closed report.

Session-start law: CHECK the environment before building - canon docs
present, workspace writable, tooling honest. ffmpeg/pytest missing are
WARN (fine in-repo: render is parked, suites run on the operator's
clock); canon/workspace failures are FAIL and the exit code says so.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path

CANON = ("docs/PRODUCTION_LAW_V2.md", "docs/RENDER_LAWS.md")


def run_checks(repo_root: str | Path) -> list[dict]:
    root = Path(repo_root)
    checks: list[dict] = []

    def add(name: str, status: str, detail: str) -> None:
        checks.append({"check": name, "status": status, "detail": detail})

    missing = [c for c in CANON if not (root / c).is_file()]
    add("canon-docs", "FAIL" if missing else "PASS",
        ("missing: " + ", ".join(missing)) if missing
        else "production law v2 + render laws present")

    try:
        out = root / "output"
        out.mkdir(parents=True, exist_ok=True)
        probe = out / ".doctor_probe"
        probe.write_text("x", encoding="utf-8")
        probe.unlink()
        add("workspace-write", "PASS", "output/ writable")
    except OSError as e:
        add("workspace-write", "FAIL", f"output/ not writable: {e}")

    ff = shutil.which("ffmpeg")
    add("ffmpeg", "WARN" if not ff else "PASS",
        "not on PATH - fine in-repo (render parked); install before "
        "operator-PC renders" if not ff else f"found: {ff}")

    try:
        import pytest  # noqa: F401
        add("pytest", "PASS", "importable")
    except ImportError:
        add("pytest", "WARN", "not installed - pip install pytest before suites")

    key = os.environ.get("MONARCH_ACCESS_KEY")
    add("access-key", "PASS" if key else "WARN",
        "MONARCH_ACCESS_KEY set in env (value never printed)" if key
        else "MONARCH_ACCESS_KEY not in env - commands will prompt")
    return checks


def exit_code(checks: list[dict]) -> int:
    """FAIL = 1 (stop and fix); WARN never blocks (L1 honesty)."""
    return 1 if any(c["status"] == "FAIL" for c in checks) else 0
