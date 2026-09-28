"""Learn 2.0 — lesson hygiene: expiry, confirmation, conflict flags (W1).

Lessons that never expire become rope: a stale "short hooks win" law will
keep steering scripts long after the audience moved on (the memory-loop
rule: a loop fed stale lessons reinforces BAD patterns).

Hunt-backed parameters (agent-memory practice, 2026):
* promotion  — a lesson is CONFIRMED at >= 3 signals (the repo's 3x rule);
* expiry     — < 3 signals and older than 90 days -> STALE (archived
               section, never deleted — honesty over erasure);
* conflict   — two different rules under the same miss-tag with >= 2 of
               them confirmed -> CONFLICTING SIGNALS flag (a deduction
               pass would auto-resolve; Monarch reports it to the operator
               instead — ground truth owns contradictions).

Fail-soft parsing: lessons.md lines that don't match the recorder format
are counted as skipped, never invented into lessons.
"""

from __future__ import annotations

import re
import statistics
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

_LINE = re.compile(r"^- (\S+) \| miss: (.+?) \| 3x rule: (.+?)\s*$")

CONFIRM_AT = 3
MAX_AGE_DAYS = 90


@dataclass
class LessonEntry:
    stamp: str
    miss: str
    rule: str


@dataclass
class HygieneReport:
    total: int
    confirmed: int
    provisional: int
    stale: int
    skipped: int
    conflicts: list[str] = field(default_factory=list)
    rows: list[dict] = field(default_factory=list)

    def summary(self) -> str:
        out = (f"lessons hygiene: {self.total} entries | confirmed {self.confirmed} | "
               f"provisional {self.provisional} | stale {self.stale}"
               + (f" | skipped {self.skipped}" if self.skipped else "")
               + (f" | CONFLICTS {len(self.conflicts)}" if self.conflicts else ""))
        for c in self.conflicts:
            out += f"\n  CONFLICT: {c}"
        return out


def parse_lessons(text: str) -> tuple[list[LessonEntry], int]:
    """lessons.md text -> (entries, skipped_line_count)."""
    out: list[LessonEntry] = []
    skipped = 0
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        m = _LINE.match(line)
        if not m:
            skipped += 1
            continue
        out.append(LessonEntry(stamp=m.group(1), miss=m.group(2).strip(),
                               rule=m.group(3).strip()))
    return out, skipped


def _age_days(stamp: str, today: datetime) -> int:
    try:
        dt = datetime.strptime(stamp, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except ValueError:
        try:
            dt = datetime.strptime(stamp, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError:
            return 0
    return max(0, (today - dt).days)


def hygiene(entries: list[LessonEntry], *, today: datetime | None = None,
            confirm_at: int = CONFIRM_AT, max_age_days: int = MAX_AGE_DAYS) -> HygieneReport:
    """Group by (miss, rule) -> confirmed / provisional / stale + conflicts."""
    now = today or datetime.now(timezone.utc)
    groups: dict[tuple[str, str], list[LessonEntry]] = {}
    for e in entries:
        groups.setdefault((e.miss, e.rule), []).append(e)

    status_of: dict[str, list[int]] = {}
    rows: list[dict] = []
    for (miss, rule), items in sorted(groups.items()):
        ages = [_age_days(i.stamp, now) for i in items]
        last_seen = min(ages)  # newest stamp = smallest age
        count = len(items)
        if count >= confirm_at:
            status = "confirmed"
        elif last_seen > max_age_days:
            status = "stale"
        else:
            status = "provisional"
        status_of.setdefault(miss, []).append(1 if status == "confirmed" else 0)
        rows.append({
            "miss": miss, "rule": rule, "count": count,
            "last_seen_days_ago": last_seen, "status": status,
        })

    conflicts: list[str] = []
    for miss, flags in status_of.items():
        rules = [r["rule"] for r in rows if r["miss"] == miss]
        if len(rules) > 1 and sum(flags) >= 2:
            conflicts.append(
                f"'{miss}' has {len(rules)} different rules with confirmed "
                f"signals — operator must arbitrate (ground truth owns contradictions)")

    rep = HygieneReport(
        total=len(entries),
        confirmed=sum(1 for r in rows if r["status"] == "confirmed"),
        provisional=sum(1 for r in rows if r["status"] == "provisional"),
        stale=sum(1 for r in rows if r["status"] == "stale"),
        skipped=0,
        conflicts=conflicts,
        rows=rows,
    )
    return rep


def hygiene_from_file(path: str | Path, **kw) -> tuple[HygieneReport, int]:
    """File wrapper -> (report, skipped_lines)."""
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    entries, skipped = parse_lessons(text)
    return hygiene(entries, **kw), skipped
