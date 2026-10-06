"""Fail-closed CSV parsing for operator-supplied Analytics retention curves.

Only the documented time-ratio and audience-watch-ratio fields are accepted.
This importer deliberately does not fetch data or infer access authorization.
"""

from __future__ import annotations

import csv
import io
import math
import re
from typing import Any

from monarch.core.retention import RetentionPoint

_TIME_HEADERS = {
    "elapsedvideotimeratio",
    "elapsedvideotimepercentage",
    "elapsedratio",
}
_AUDIENCE_HEADERS = {
    "audiencewatchratio",
}
_RELATIVE_HEADERS = {
    "relativeretentionperformance",
}
_VIDEO_ID_HEADERS = {"videoid", "video"}


def _normalized_header(raw: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (raw or "").lower())


def _split_table(text: str) -> tuple[list[str], list[list[str]]]:
    lines = text.splitlines()
    first = lines[0] if lines else ""
    delimiter = "\t" if "\t" in first else (";" if ";" in first and "," not in first else ",")
    rows = list(csv.reader(io.StringIO(text), delimiter=delimiter))
    rows = [[cell.strip() for cell in row] for row in rows if any(cell.strip() for cell in row)]
    if not rows:
        return [], []
    return rows[0], rows[1:]


def _number(raw: str, field: str, *, percent_allowed: bool = True) -> float:
    value = (raw or "").strip().strip('"')
    if not value:
        raise ValueError(f"missing {field} value")
    is_percent = value.endswith("%")
    if is_percent:
        if not percent_allowed:
            raise ValueError(f"percent form is not accepted for {field}")
        value = value[:-1].strip()
    try:
        number = float(value)
    except ValueError as exc:
        raise ValueError(f"invalid {field} value {raw!r}") from exc
    if not math.isfinite(number):
        raise ValueError(f"{field} must be finite")
    if is_percent:
        number /= 100.0
    return number


def csv_points(text: str, *, expected_video_id: str = "") -> list[RetentionPoint]:
    """Parse a single video's exported curve into validated points.

    Accepted time headers include ``elapsedVideoTimeRatio`` and the Analytics
    export spelling ``elapsed_video_time_percentage``. The audience column must
    explicitly mean ``audienceWatchRatio``; average-percentage-viewed is not a
    replacement. Rows must already be in increasing time order.
    """
    header, rows = _split_table(text)
    if not rows:
        raise ValueError("no retention data rows found")
    normalized = [_normalized_header(cell) for cell in header]
    if len(set(normalized)) != len(normalized):
        raise ValueError("duplicate normalized CSV headers are ambiguous")

    def find(aliases: set[str], label: str) -> int | None:
        matches = [index for index, name in enumerate(normalized) if name in aliases]
        if len(matches) > 1:
            raise ValueError(f"multiple {label} columns are ambiguous")
        return matches[0] if matches else None

    time_col = find(_TIME_HEADERS, "elapsed-time")
    audience_col = find(_AUDIENCE_HEADERS, "audience-watch-ratio")
    relative_col = find(_RELATIVE_HEADERS, "relative-retention")
    video_col = find(_VIDEO_ID_HEADERS, "video-id")
    if time_col is None or audience_col is None:
        raise ValueError(
            "unrecognized retention export: need elapsedVideoTimeRatio and "
            "audienceWatchRatio columns; average percentage viewed is not a curve"
        )

    points: list[RetentionPoint] = []
    expected_id = (expected_video_id or "").strip()
    for row_no, row in enumerate(rows, 2):
        if len(row) > len(header):
            raise ValueError(f"row {row_no}: has more values than the header")
        row += [""] * (len(header) - len(row))
        if video_col is not None:
            row_video_id = row[video_col].strip()
            if expected_id and row_video_id and row_video_id != expected_id:
                raise ValueError(
                    f"row {row_no}: video id {row_video_id!r} does not match "
                    f"requested {expected_id!r}"
                )
        try:
            elapsed = _number(row[time_col], "elapsedVideoTimeRatio")
            audience = _number(row[audience_col], "audienceWatchRatio")
            relative_raw = row[relative_col] if relative_col is not None else ""
            relative = (
                _number(relative_raw, "relativeRetentionPerformance")
                if relative_raw.strip() else None
            )
            points.append(RetentionPoint(
                elapsed_ratio=elapsed,
                audience_watch_ratio=audience,
                relative_retention_performance=relative,
            ))
        except ValueError as exc:
            raise ValueError(f"row {row_no}: {exc}") from exc
    if len(points) < 2:
        raise ValueError("retention export needs at least two valid data points")
    ratios = [point.elapsed_ratio for point in points]
    if any(right <= left for left, right in zip(ratios, ratios[1:])):
        raise ValueError("elapsedVideoTimeRatio values must be strictly increasing")
    return points


def csv_records(
    text: str,
    *,
    video_id: str,
    title: str,
    duration_s: float,
    source: str = "operator-supplied export",
) -> list[RetentionPoint]:
    """Validate curve metadata and return its points, for CLI ingestion."""
    video_id = (video_id or "").strip()
    title = (title or "").strip()
    source = (source or "").strip()
    try:
        duration = float(duration_s)
    except (TypeError, ValueError) as exc:
        raise ValueError("duration_s must be a number") from exc
    if not math.isfinite(duration) or duration <= 0:
        raise ValueError("duration_s must be finite and > 0")
    if not video_id:
        raise ValueError("video_id is required")
    if not title:
        raise ValueError("title is required")
    if not source:
        raise ValueError("source label is required")
    return csv_points(text, expected_video_id=video_id)
