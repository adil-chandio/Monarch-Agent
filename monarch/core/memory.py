"""Session memory save/restore — the new-session handoff bridge.

Ruflo-inspired (RVF), Monarch-ized: one JSON file carries everything a fresh
session needs to resume without re-asking the operator — the M-state, channel
DNA, pending approvals, notes, the lessons digest and the performance digest.

Fail-closed rules:

* ``load_state`` refuses a missing, corrupt, unknown-version or unknown-state
  file — it never guesses.
* Saving validates the M-state against :data:`monarch.core.state_machine.STATES`
  and the channel file through :func:`monarch.core.channels.load_channel`.
* The memory file (``.monarch/``) is session state — gitignored, never shipped.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from monarch.core.channels import load_channel
from monarch.core.state_machine import STATES, Run

#: project-local session state (gitignored)
MEMORY_DIR = Path(".monarch")
MEMORY_FILE = MEMORY_DIR / "memory.json"

#: lessons live here by default (L16 self-improvement loop)
LESSONS_FILE = Path(__file__).resolve().parents[1] / "self_improve" / "lessons.md"

MEMORY_VERSION = 1


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _lessons_digest(path: Path = LESSONS_FILE) -> dict:
    """Count recorded rules and keep the last few — small but honest."""
    if not path.is_file():
        return {"rules": 0, "last": []}
    rules = [
        line.strip().removeprefix("- ").strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip().startswith("- ")
    ]
    return {"rules": len(rules), "last": rules[-3:]}


def _performance_digest(path: Path) -> dict:
    """Best logged video so far (see :mod:`monarch.core.learn`)."""
    if not path.is_file():
        return {"videos": 0, "best": None}
    best = None
    count = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except ValueError:
            continue  # digest is best-effort; learn.load_performance is strict
        count += 1
        if best is None or float(rec.get("avg_pct", 0)) > float(best.get("avg_pct", 0)):
            best = rec
    if best is None:
        return {"videos": 0, "best": None}
    return {
        "videos": count,
        "best": {
            "topic": str(best.get("topic", "")),
            "avg_pct": float(best.get("avg_pct", 0.0)),
        },
    }


def save_state(
    *,
    path: str | Path = MEMORY_FILE,
    m_state: str | None = None,
    channel_path: str | Path | None = None,
    pending: list[str] | None = None,
    notes: list[str] | None = None,
    topic: str = "",
    lessons_path: Path = LESSONS_FILE,
    perf_path: Path | None = None,
) -> tuple[Path, dict]:
    """Snapshot the session into ``path``. Returns ``(path, state_dict)``."""
    state = m_state or Run().state
    if state not in STATES:
        raise ValueError(f"unknown M-state {state!r}: use one of {', '.join(STATES)}")

    channel = None
    if channel_path:
        channel = asdict(load_channel(channel_path))  # FileNotFoundError is honest

    p = Path(path)
    doc = {
        "version": MEMORY_VERSION,
        "saved_at": _utc_now(),
        "m_state": state,
        "wait_for": Run(state=state).wait_prompt(),
        "topic": topic.strip(),
        "channel": channel,
        "pending": [s.strip() for s in (pending or []) if s.strip()],
        "notes": [s.strip() for s in (notes or []) if s.strip()],
        "lessons": _lessons_digest(Path(lessons_path)),
        "performance": _performance_digest(Path(perf_path) if perf_path else MEMORY_DIR / "performance.jsonl"),
    }
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    return p, doc


def load_state(path: str | Path = MEMORY_FILE) -> dict:
    """Read a memory snapshot. Fail-closed on missing/corrupt/foreign files."""
    p = Path(path)
    if not p.is_file():
        raise ValueError(f"This is missing, could you provide it: {p}")
    try:
        doc = json.loads(p.read_text(encoding="utf-8"))
    except ValueError as e:
        raise ValueError(f"corrupt memory file {p}: {e}") from e
    if not isinstance(doc, dict):
        raise ValueError(f"memory file {p} must be a JSON object")
    version = doc.get("version")
    if version != MEMORY_VERSION:
        raise ValueError(f"unsupported memory version {version!r}: expected {MEMORY_VERSION}")
    state = doc.get("m_state")
    if state not in STATES:
        raise ValueError(f"memory file has unknown M-state {state!r}")
    doc["wait_for"] = Run(state=state).wait_prompt()
    return doc


def format_state(doc: dict) -> str:
    """One readable card an agent (or human) can resume from."""
    W = 64
    lines = [
        "👑 MONARCH MEMORY — session handoff",
        f"saved   {doc.get('saved_at', '?')}",
        f"state   {doc.get('m_state', '?')}"
        + (f"  (WAIT: {doc['wait_for']})" if doc.get("wait_for") else ""),
    ]
    ch = doc.get("channel")
    if ch:
        lines.append(
            f"channel {ch.get('id', '?')} — {ch.get('niche', '?')}"
            f" · {ch.get('aspect', '?')} · {ch.get('language', '?')}"
        )
    if doc.get("topic"):
        lines.append(f"topic   {doc['topic']}")
    for i, item in enumerate(doc.get("pending") or [], 1):
        lines.append(f"pending {i}) {item}")
    for i, item in enumerate(doc.get("notes") or [], 1):
        lines.append(f"note    {i}) {item}")
    les = doc.get("lessons") or {}
    lines.append(f"lessons {les.get('rules', 0)} rule(s) on record")
    for rule in (les.get("last") or [])[-2:]:
        lines.append(f"        · {rule[:W - 12]}")
    perf = doc.get("performance") or {}
    if perf.get("videos"):
        best = perf.get("best") or {}
        lines.append(
            f"videos  {perf['videos']} logged | best: {best.get('topic', '?')}"
            f" ({best.get('avg_pct', 0):.0f}% avg viewed)"
        )
    out = [f"╔{'═' * W}╗"]
    for line in lines:
        out.append(f"║ {line[:W - 3].ljust(W - 2)} ║")
    out.append(f"╚{'═' * W}╝")
    return "\n".join(out)
