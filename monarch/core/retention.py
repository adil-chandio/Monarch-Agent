"""Validated storage and cautious reporting for time-indexed retention curves.

Curves are operator-supplied, per-video aggregate data. This module does not
fetch from YouTube, verify access rights, infer causes, or treat watch ratios as
unique-viewer percentages.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

RETENTION_FILE = Path(".monarch") / "retention_curves.jsonl"
SCHEMA_VERSION = 1


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _finite_number(value: Any, name: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a number") from exc
    if not math.isfinite(number):
        raise ValueError(f"{name} must be finite")
    return number


@dataclass(frozen=True)
class RetentionPoint:
    """One Analytics bucket; the ratio is an average watch ratio, not a count."""

    elapsed_ratio: float
    audience_watch_ratio: float
    relative_retention_performance: float | None = None

    def __post_init__(self) -> None:
        elapsed = _finite_number(self.elapsed_ratio, "elapsed_ratio")
        audience = _finite_number(self.audience_watch_ratio, "audience_watch_ratio")
        relative = self.relative_retention_performance
        if not 0.0 <= elapsed <= 1.0:
            raise ValueError("elapsed_ratio must be within 0..1")
        if audience < 0.0:
            raise ValueError("audience_watch_ratio must be >= 0")
        if relative is not None:
            relative = _finite_number(relative, "relative_retention_performance")
            if not 0.0 <= relative <= 1.0:
                raise ValueError("relative_retention_performance must be within 0..1")
        object.__setattr__(self, "elapsed_ratio", elapsed)
        object.__setattr__(self, "audience_watch_ratio", audience)
        object.__setattr__(self, "relative_retention_performance", relative)

    def to_dict(self) -> dict[str, float | None]:
        return {
            "elapsed_ratio": self.elapsed_ratio,
            "audience_watch_ratio": self.audience_watch_ratio,
            "relative_retention_performance": self.relative_retention_performance,
        }

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "RetentionPoint":
        if not isinstance(raw, dict):
            raise ValueError("retention point must be an object")
        return cls(
            elapsed_ratio=raw.get("elapsed_ratio"),
            audience_watch_ratio=raw.get("audience_watch_ratio"),
            relative_retention_performance=raw.get("relative_retention_performance"),
        )


@dataclass(frozen=True)
class RetentionCurve:
    """One supplied curve tied to a single video and known duration."""

    video_id: str
    title: str
    duration_s: float
    points: tuple[RetentionPoint, ...]
    source: str = "operator-supplied export"
    imported_at: str = ""

    def __post_init__(self) -> None:
        video_id = (self.video_id or "").strip()
        title = (self.title or "").strip()
        source = (self.source or "").strip()
        duration = _finite_number(self.duration_s, "duration_s")
        points = tuple(self.points)
        if not video_id:
            raise ValueError("video_id is required")
        if not title:
            raise ValueError("title is required")
        if duration <= 0.0:
            raise ValueError("duration_s must be > 0")
        if not source:
            raise ValueError("source label is required")
        if len(points) < 2:
            raise ValueError("retention curve needs at least two data points")
        if any(not isinstance(point, RetentionPoint) for point in points):
            raise ValueError("all points must be RetentionPoint values")
        ratios = [point.elapsed_ratio for point in points]
        if any(right <= left for left, right in zip(ratios, ratios[1:])):
            raise ValueError("elapsed_ratio values must be strictly increasing")
        imported_at = (self.imported_at or "").strip() or _utc_now()
        object.__setattr__(self, "video_id", video_id)
        object.__setattr__(self, "title", title)
        object.__setattr__(self, "duration_s", duration)
        object.__setattr__(self, "points", points)
        object.__setattr__(self, "source", source)
        object.__setattr__(self, "imported_at", imported_at)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "video_id": self.video_id,
            "title": self.title,
            "duration_s": self.duration_s,
            "source": self.source,
            "source_authorization_verified": False,
            "authorization_note": "Monarch does not verify the export owner's authorization.",
            "imported_at": self.imported_at,
            "points": [point.to_dict() for point in self.points],
        }

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "RetentionCurve":
        if not isinstance(raw, dict):
            raise ValueError("retention curve record must be an object")
        raw_points = raw.get("points")
        if not isinstance(raw_points, list):
            raise ValueError("points must be a list")
        return cls(
            video_id=str(raw.get("video_id", "")),
            title=str(raw.get("title", "")),
            duration_s=raw.get("duration_s"),
            source=str(raw.get("source", "operator-supplied export")),
            imported_at=str(raw.get("imported_at", "")),
            points=tuple(RetentionPoint.from_dict(point) for point in raw_points),
        )


def record_retention_curve(
    curve: RetentionCurve, path: str | Path = RETENTION_FILE
) -> Path:
    """Append one validated curve; default storage is gitignored session state."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(curve.to_dict(), ensure_ascii=False, allow_nan=False) + "\n")
    return target


def load_retention_curves(path: str | Path = RETENTION_FILE) -> list[RetentionCurve]:
    """Load all curves; fail loudly with the line number on malformed state."""
    target = Path(path)
    if not target.is_file():
        return []
    curves: list[RetentionCurve] = []
    for line_no, line in enumerate(target.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            curves.append(RetentionCurve.from_dict(json.loads(line)))
        except (json.JSONDecodeError, TypeError, ValueError) as exc:
            raise ValueError(f"{target} line {line_no}: {exc}") from exc
    return curves


def retention_report(curve: RetentionCurve, *, top_drops: int = 5) -> dict[str, Any]:
    """Summarize the biggest adjacent ratio declines without claiming causes."""
    if top_drops < 0:
        raise ValueError("top_drops must be >= 0")
    point_count = len(curve.points)
    first, last = curve.points[0], curve.points[-1]
    declines: list[dict[str, float]] = []
    for before, after in zip(curve.points, curve.points[1:]):
        decline = before.audience_watch_ratio - after.audience_watch_ratio
        if decline > 0:
            declines.append({
                "from_time_s_approx": round(before.elapsed_ratio * curve.duration_s, 3),
                "to_time_s_approx": round(after.elapsed_ratio * curve.duration_s, 3),
                "from_audience_watch_ratio": before.audience_watch_ratio,
                "to_audience_watch_ratio": after.audience_watch_ratio,
                "decline_in_ratio_units": decline,
            })
    declines.sort(key=lambda item: item["decline_in_ratio_units"], reverse=True)
    relative = [
        point.relative_retention_performance
        for point in curve.points
        if point.relative_retention_performance is not None
    ]
    return {
        "video_id": curve.video_id,
        "title": curve.title,
        "duration_s": curve.duration_s,
        "source": curve.source,
        "source_authorization_verified": False,
        "imported_at": curve.imported_at,
        "point_count": point_count,
        "first_audience_watch_ratio": first.audience_watch_ratio,
        "last_audience_watch_ratio": last.audience_watch_ratio,
        "relative_retention_points_available": len(relative),
        "first_relative_retention_performance": next(
            (point.relative_retention_performance for point in curve.points
             if point.relative_retention_performance is not None), None
        ),
        "last_relative_retention_performance": next(
            (point.relative_retention_performance for point in reversed(curve.points)
             if point.relative_retention_performance is not None), None
        ),
        "largest_adjacent_declines": declines[:top_drops],
        "interpretation_notes": [
            "audience_watch_ratio is an average watch ratio, not a unique-viewer percentage; it may exceed 1 when viewers replay a segment.",
            "Approximate bucket times use elapsed_ratio multiplied by the supplied duration; a bucket does not identify an exact viewer exit time.",
            "Adjacent declines are descriptive only. They do not establish a cause, audience segment, or edit-level effect.",
            "Source provenance and the export owner's authorization are not verified by Monarch.",
        ],
    }
