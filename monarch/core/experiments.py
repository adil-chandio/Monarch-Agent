"""Local records for operator-transcribed YouTube Studio A/B outcomes.

Monarch does not start experiments, query YouTube, or validate the provenance of
an outcome. This is a structured memory of the result that Studio displayed.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

EXPERIMENT_FILE = Path(".monarch") / "experiments.jsonl"
SCHEMA_VERSION = 1
TEST_TYPES = {"thumbnail", "title", "title_and_thumbnail"}
OUTCOMES = {
    "winner",
    "preferred",
    "performed_same",
    "inconclusive",
    "in_progress",
    "not_run",
}
WINNING_OUTCOMES = {"winner", "preferred"}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _date_or_empty(value: str, name: str) -> str:
    value = (value or "").strip()
    if not value:
        return ""
    try:
        date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{name} must be an ISO date (YYYY-MM-DD)") from exc
    return value


@dataclass(frozen=True)
class NativeExperimentResult:
    """One manually recorded native-test result, without inferred significance."""

    test_id: str
    video_id: str
    title: str
    test_type: str
    variants: tuple[str, ...]
    outcome: str
    winner_variant: str = ""
    window_start: str = ""
    window_end: str = ""
    source: str = "operator-transcribed YouTube Studio result"
    notes: str = ""
    recorded_at: str = ""

    def __post_init__(self) -> None:
        test_id = (self.test_id or "").strip()
        video_id = (self.video_id or "").strip()
        title = (self.title or "").strip()
        test_type = (self.test_type or "").strip().lower().replace("+", "_").replace(" ", "_")
        outcome = (self.outcome or "").strip().lower().replace(" ", "_").replace("-", "_")
        variants = tuple(str(variant).strip() for variant in self.variants if str(variant).strip())
        winner_variant = (self.winner_variant or "").strip()
        source = (self.source or "").strip()
        window_start = _date_or_empty(self.window_start, "window_start")
        window_end = _date_or_empty(self.window_end, "window_end")
        if not test_id:
            raise ValueError("test_id is required")
        if not video_id:
            raise ValueError("video_id is required")
        if not title:
            raise ValueError("title is required")
        if test_type not in TEST_TYPES:
            raise ValueError(f"test_type must be one of {sorted(TEST_TYPES)}")
        if outcome not in OUTCOMES:
            raise ValueError(f"outcome must be one of {sorted(OUTCOMES)}")
        if not 2 <= len(variants) <= 3:
            raise ValueError("native test must record 2 or 3 variants")
        if len(set(variants)) != len(variants):
            raise ValueError("variant labels must be unique")
        if outcome in WINNING_OUTCOMES:
            if not winner_variant:
                raise ValueError(f"winner_variant is required for outcome {outcome!r}")
            if winner_variant not in variants:
                raise ValueError("winner_variant must match one of the recorded variants")
        elif winner_variant:
            raise ValueError(f"outcome {outcome!r} must not be assigned a winning variant")
        if window_start and window_end and window_start > window_end:
            raise ValueError("window_start must be on or before window_end")
        if not source:
            raise ValueError("source label is required")
        recorded_at = (self.recorded_at or "").strip() or _utc_now()
        object.__setattr__(self, "test_id", test_id)
        object.__setattr__(self, "video_id", video_id)
        object.__setattr__(self, "title", title)
        object.__setattr__(self, "test_type", test_type)
        object.__setattr__(self, "variants", variants)
        object.__setattr__(self, "outcome", outcome)
        object.__setattr__(self, "winner_variant", winner_variant)
        object.__setattr__(self, "window_start", window_start)
        object.__setattr__(self, "window_end", window_end)
        object.__setattr__(self, "source", source)
        object.__setattr__(self, "notes", (self.notes or "").strip())
        object.__setattr__(self, "recorded_at", recorded_at)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "platform": "YouTube Studio",
            "test_id": self.test_id,
            "video_id": self.video_id,
            "title": self.title,
            "test_type": self.test_type,
            "variants": list(self.variants),
            "outcome": self.outcome,
            "winner_variant": self.winner_variant or None,
            "decision_metric": "watch_time",
            "window_start": self.window_start or None,
            "window_end": self.window_end or None,
            "source": self.source,
            "source_result_verified": False,
            "verification_note": "Monarch stores the operator-transcribed outcome; it does not query or verify YouTube Studio.",
            "notes": self.notes,
            "recorded_at": self.recorded_at,
        }

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "NativeExperimentResult":
        if not isinstance(raw, dict):
            raise ValueError("experiment record must be an object")
        variants = raw.get("variants")
        if not isinstance(variants, list):
            raise ValueError("variants must be a list")
        return cls(
            test_id=str(raw.get("test_id", "")),
            video_id=str(raw.get("video_id", "")),
            title=str(raw.get("title", "")),
            test_type=str(raw.get("test_type", "")),
            variants=tuple(str(item) for item in variants),
            outcome=str(raw.get("outcome", "")),
            winner_variant=str(raw.get("winner_variant") or ""),
            window_start=str(raw.get("window_start") or ""),
            window_end=str(raw.get("window_end") or ""),
            source=str(raw.get("source", "operator-transcribed YouTube Studio result")),
            notes=str(raw.get("notes", "")),
            recorded_at=str(raw.get("recorded_at", "")),
        )


def record_experiment_result(
    result: NativeExperimentResult, path: str | Path = EXPERIMENT_FILE
) -> Path:
    """Append one result to local, gitignored session state by default."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(result.to_dict(), ensure_ascii=False, allow_nan=False) + "\n")
    return target


def load_experiment_results(
    path: str | Path = EXPERIMENT_FILE, *, video_id: str = ""
) -> list[NativeExperimentResult]:
    """Load validated records, optionally filtered by video ID; fail on corrupt lines."""
    target = Path(path)
    if not target.is_file():
        return []
    requested_video_id = (video_id or "").strip()
    results: list[NativeExperimentResult] = []
    for line_no, line in enumerate(target.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            result = NativeExperimentResult.from_dict(json.loads(line))
        except (json.JSONDecodeError, TypeError, ValueError) as exc:
            raise ValueError(f"{target} line {line_no}: {exc}") from exc
        if not requested_video_id or result.video_id == requested_video_id:
            results.append(result)
    return results
