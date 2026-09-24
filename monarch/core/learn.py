"""Learn from uploaded videos — the L16 loop closed with real-world data.

Ruflo's RETRIEVE → JUDGE → DISTILL → CONSOLIDATE pipeline, Monarch-ized:

* **RETRIEVE** — ``load_performance`` reads ``.monarch/performance.jsonl``
  (one JSON line per uploaded video, written by ``monarch learn record``).
* **JUDGE** — median split on *avg % viewed*: top performers vs bottom.
* **DISTILL** — categorical deltas (N2 cohort, runtime) become honest,
  provisional statements — never laws on one observation.
* **CONSOLIDATE** — ``--apply`` writes each signal into
  ``monarch/self_improve/lessons.md`` via the existing 3x-rule recorder.

Fail-closed: bad numbers never enter the log; a corrupt JSONL line stops the
load with its line number instead of being silently skipped.
"""

from __future__ import annotations

import json
import statistics
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from monarch.core.lessons import DEFAULT as LESSONS_FILE, record as record_lesson

#: project-local performance log (gitignored session state)
PERFORMANCE_FILE = Path(".monarch") / "performance.jsonl"

MIN_VIDEOS = 3


@dataclass
class PerformanceRecord:
    """One uploaded video's real-world numbers."""

    topic: str
    views: float
    avg_pct: float  # avg % viewed (APV) — the Jenny Hoyos metric
    subs: int = 0
    cohort: str = ""
    length_s: float = 0.0
    date: str = ""
    note: str = ""

    def __post_init__(self) -> None:
        topic = (self.topic or "").strip()
        if not topic:
            raise ValueError("This is missing, could you provide it: topic.")
        if self.views < 0:
            raise ValueError("views must be >= 0")
        if not 0.0 <= self.avg_pct <= 100.0:
            raise ValueError("avg_pct must be within 0..100 (avg % viewed)")
        if self.subs < 0:
            raise ValueError("subs must be >= 0")
        if self.length_s < 0:
            raise ValueError("length must be >= 0 seconds")
        self.topic = topic
        self.date = self.date or datetime.now(timezone.utc).date().isoformat()

    def to_dict(self) -> dict:
        return {
            "topic": self.topic,
            "views": self.views,
            "avg_pct": self.avg_pct,
            "subs": self.subs,
            "cohort": self.cohort,
            "length_s": self.length_s,
            "date": self.date,
            "note": self.note,
        }

    @classmethod
    def from_dict(cls, raw: dict) -> "PerformanceRecord":
        return cls(
            topic=str(raw.get("topic", "")),
            views=float(raw.get("views", 0)),
            avg_pct=float(raw.get("avg_pct", 0)),
            subs=int(raw.get("subs", 0)),
            cohort=str(raw.get("cohort", "")),
            length_s=float(raw.get("length_s", 0)),
            date=str(raw.get("date", "")),
            note=str(raw.get("note", "")),
        )


@dataclass
class LearnReport:
    """What the loop saw and (maybe) learned."""

    total: int
    status: str  # need_more | learned | no_signal
    lessons: list[str]
    lines: list[str]

    def summary(self) -> str:
        head = {
            "need_more": f"NEED MORE — {self.total} video(s) logged, "
            f"distill needs {MIN_VIDEOS}",
            "learned": f"LEARNED — {len(self.lessons)} signal(s) from {self.total} videos",
            "no_signal": f"NO SIGNAL — {self.total} videos, top and bottom agree so far",
        }.get(self.status, self.status)
        return head


def record_performance(rec: PerformanceRecord, path: str | Path = PERFORMANCE_FILE) -> Path:
    """Append one validated record as a JSON line."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec.to_dict()) + "\n")
    return p


def load_performance(path: str | Path = PERFORMANCE_FILE) -> list[PerformanceRecord]:
    """Read the log. A corrupt line fails the load loudly (fail-closed)."""
    p = Path(path)
    if not p.is_file():
        return []
    out: list[PerformanceRecord] = []
    for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            out.append(PerformanceRecord.from_dict(json.loads(line)))
        except (ValueError, TypeError) as e:
            raise ValueError(f"{p} line {i}: {e}") from e
    return out


def _mode(values: list[str]) -> str:
    vals = [v for v in values if v]
    if not vals:
        return ""
    return statistics.mode(vals)


def _mean(values: list[float]) -> float:
    return statistics.fmean(values) if values else 0.0


def distill(records: list[PerformanceRecord], *, min_videos: int = MIN_VIDEOS) -> LearnReport:
    """Median-split the log and extract provisional retention signals."""
    total = len(records)
    if total < min_videos:
        return LearnReport(
            total=total,
            status="need_more",
            lessons=[],
            lines=[f"need {min_videos} videos to split top vs bottom, have {total}"],
        )

    pcts = [r.avg_pct for r in records]
    med = statistics.median(pcts)
    top = [r for r in records if r.avg_pct >= med]
    bottom = [r for r in records if r.avg_pct < med]
    if not top or not bottom:
        return LearnReport(
            total=total, status="no_signal", lessons=[],
            lines=["every video sits on the same retention — nothing separates top from bottom yet"],
        )

    top_pct = _mean([r.avg_pct for r in top])
    bot_pct = _mean([r.avg_pct for r in bottom])
    lines = [
        f"median split at {med:.0f}% avg viewed",
        f"top {len(top)}: {top_pct:.0f}% avg viewed | bottom {len(bottom)}: {bot_pct:.0f}%",
    ]

    lessons: list[str] = []
    top_cohort, bot_cohort = _mode([r.cohort for r in top]), _mode([r.cohort for r in bottom])
    if top_cohort and bot_cohort and top_cohort != bot_cohort:
        lessons.append(
            f"cohort '{top_cohort}' holds attention better than '{bot_cohort}' here "
            f"({top_pct:.0f}% vs {bot_pct:.0f}% avg viewed, N={total}) — provisional, "
            "promote to a channel law only after 3 consistent signals"
        )
        lines.append(f"cohort delta: top={top_cohort} vs bottom={bot_cohort} (N2 evidence)")

    top_len = _mean([r.length_s for r in top if r.length_s > 0])
    bot_len = _mean([r.length_s for r in bottom if r.length_s > 0])
    if top_len and bot_len and abs(top_len - bot_len) >= 5:
        better = f"~{top_len:.0f}s" if top_len > bot_len else f"~{bot_len:.0f}s"
        other = f"~{bot_len:.0f}s" if top_len > bot_len else f"~{top_len:.0f}s"
        lessons.append(
            f"runtime {better} outperforms {other} on avg % viewed (N={total}) — "
            "provisional until 3 consistent signals"
        )
        lines.append(f"runtime delta: top {top_len:.0f}s vs bottom {bot_len:.0f}s")

    top_views = _mean([r.views for r in top])
    bot_views = _mean([r.views for r in bottom])
    if bot_views > 0:
        lines.append(f"views: top {top_views:.0f} vs bottom {bot_views:.0f}")

    if not lessons:
        return LearnReport(
            total=total, status="no_signal", lessons=[], lines=lines + [
                "retention gap exists but no categorical delta yet — keep logging "
                "(cohort/runtime tags make the signals)"
            ]
        )
    return LearnReport(total=total, status="learned", lessons=lessons, lines=lines)


def consolidate(report: LearnReport, path: str | Path = LESSONS_FILE) -> int:
    """Write distilled signals into lessons.md (3x rule). Only when learned."""
    if report.status != "learned":
        return 0
    for lesson in report.lessons:
        record_lesson("retention_signal", lesson, Path(path))
    return len(report.lessons)
