from __future__ import annotations

import json

import pytest

from monarch.cli import main
from monarch.core.retention import (
    RetentionCurve,
    RetentionPoint,
    load_retention_curves,
    record_retention_curve,
    retention_report,
)
from monarch.pipelines.retention import csv_points, csv_records


def test_csv_points_accepts_api_headers_percentages_and_rewatch_ratio():
    text = (
        "elapsedVideoTimeRatio,audienceWatchRatio,relativeRetentionPerformance\n"
        "0%,0.9,0.50\n"
        "50%,1.2,75%\n"
        "100%,0.4,0.25\n"
    )
    points = csv_points(text)
    assert len(points) == 3
    assert points[0].elapsed_ratio == 0.0
    assert points[1].elapsed_ratio == 0.5
    assert points[1].audience_watch_ratio == 1.2  # rewatch ratios may exceed 1
    assert points[1].relative_retention_performance == 0.75


def test_csv_points_accepts_reporting_export_aliases_and_tsv():
    text = (
        "elapsed_video_time_percentage\taudience_watch_ratio\n"
        "0.1\t0.8\n"
        "0.5\t0.6\n"
        "1.0\t0.3\n"
    )
    points = csv_points(text)
    assert [point.elapsed_ratio for point in points] == [0.1, 0.5, 1.0]
    assert [point.audience_watch_ratio for point in points] == [0.8, 0.6, 0.3]


def test_parser_fails_closed_on_aggregate_apv_only():
    with pytest.raises(ValueError, match="average percentage viewed is not a curve"):
        csv_points("Video title,Views,Average percentage viewed\na,100,50%\n")


@pytest.mark.parametrize(
    "text,match",
    [
        (
            "elapsedVideoTimeRatio,audienceWatchRatio\n0.5,0.8\n0.4,0.7\n",
            "strictly increasing",
        ),
        (
            "elapsedVideoTimeRatio,audienceWatchRatio\n0.1,-0.1\n0.2,0.5\n",
            "audience_watch_ratio must be >= 0",
        ),
        (
            "elapsedVideoTimeRatio,audienceWatchRatio\n0.1,NaN\n0.2,0.5\n",
            "must be finite",
        ),
        (
            "elapsedVideoTimeRatio,audienceWatchRatio\n0.1,0.4\n",
            "at least two",
        ),
    ],
)
def test_parser_rejects_invalid_curves(text, match):
    with pytest.raises(ValueError, match=match):
        csv_points(text)


def test_parser_rejects_mixed_video_export():
    text = (
        "video_id,elapsedVideoTimeRatio,audienceWatchRatio\n"
        "video-a,0.1,0.8\n"
        "video-b,0.2,0.7\n"
    )
    with pytest.raises(ValueError, match="does not match"):
        csv_points(text, expected_video_id="video-a")


def test_curve_validates_metadata_and_monotonic_points():
    points = (RetentionPoint(0.1, 0.9), RetentionPoint(1.0, 0.2))
    curve = RetentionCurve("abc", "Test", 100, points)
    assert curve.imported_at.endswith("Z")
    assert curve.to_dict()["source_authorization_verified"] is False
    with pytest.raises(ValueError, match="strictly increasing"):
        RetentionCurve(
            "abc", "Test", 100,
            (RetentionPoint(0.5, 0.7), RetentionPoint(0.5, 0.2)),
        )
    with pytest.raises(ValueError, match="duration_s must be > 0"):
        RetentionCurve("abc", "Test", 0, points)


def test_retention_round_trip_and_descriptive_report(tmp_path):
    points = (
        RetentionPoint(0.0, 0.95, 0.8),
        RetentionPoint(0.25, 0.9, 0.7),
        RetentionPoint(0.5, 1.2, 0.6),
        RetentionPoint(0.75, 0.4, 0.5),
    )
    curve = RetentionCurve("vid-1", "A curve", 120, points, source="authorized export (operator stated)")
    path = record_retention_curve(curve, tmp_path / "curves.jsonl")
    loaded = load_retention_curves(path)
    assert len(loaded) == 1
    assert loaded[0] == curve
    report = retention_report(loaded[0], top_drops=2)
    assert report["point_count"] == 4
    assert report["source_authorization_verified"] is False
    assert report["largest_adjacent_declines"][0]["from_time_s_approx"] == 60.0
    assert report["largest_adjacent_declines"][0]["to_time_s_approx"] == 90.0
    assert report["largest_adjacent_declines"][0]["decline_in_ratio_units"] == pytest.approx(0.8)
    assert any("may exceed 1" in note for note in report["interpretation_notes"])


def test_corrupt_retention_jsonl_fails_with_line_number(tmp_path):
    path = tmp_path / "curves.jsonl"
    valid = RetentionCurve(
        "ok", "valid", 2,
        (RetentionPoint(0.0, 0.9), RetentionPoint(1.0, 0.5)),
    ).to_dict()
    path.write_text(json.dumps(valid) + "\nnot json\n", encoding="utf-8")
    with pytest.raises(ValueError, match=r"line 2"):
        load_retention_curves(path)


def test_csv_records_validates_curve_metadata():
    text = "elapsedVideoTimeRatio,audienceWatchRatio\n0.1,0.9\n1.0,0.2\n"
    points = csv_records(text, video_id="v1", title="Title", duration_s=60)
    assert len(points) == 2
    with pytest.raises(ValueError, match="video_id is required"):
        csv_records(text, video_id="", title="Title", duration_s=60)


def test_cli_ingest_and_report_retention_curve(capsys, tmp_path):
    csv_path = tmp_path / "retention.csv"
    csv_path.write_text(
        "elapsedVideoTimeRatio,audienceWatchRatio,relativeRetentionPerformance\n"
        "0.1,0.9,0.8\n0.5,0.55,0.6\n1.0,0.2,0.4\n",
        encoding="utf-8",
    )
    log_path = tmp_path / "retention.jsonl"
    ingest_rc = main([
        "learn", "retention", "ingest", str(csv_path),
        "--video-id", "v1", "--title", "Video one", "--duration-s", "100",
        "--file", str(log_path),
    ])
    ingest_out = capsys.readouterr().out
    assert ingest_rc == 0
    assert "INGESTED retention curve" in ingest_out
    assert "NOT VERIFIED" in ingest_out
    assert log_path.exists()

    report_rc = main([
        "learn", "retention", "report", "--video-id", "v1",
        "--file", str(log_path), "--json",
    ])
    report_out = capsys.readouterr().out
    assert report_rc == 0
    payload = json.loads(report_out)
    assert payload["video_id"] == "v1"
    assert payload["point_count"] == 3
    assert payload["source_authorization_verified"] is False


def test_cli_missing_curve_is_not_measured(capsys, tmp_path):
    rc = main([
        "learn", "retention", "report", "--video-id", "missing",
        "--file", str(tmp_path / "absent.jsonl"),
    ])
    assert rc == 2
    assert "NOT MEASURED" in capsys.readouterr().out


def test_cli_retention_rejects_apv_export(capsys, tmp_path):
    csv_path = tmp_path / "aggregate.csv"
    csv_path.write_text(
        "Video title,Views,Average percentage viewed\nVideo,500,45%\n",
        encoding="utf-8",
    )
    rc = main([
        "learn", "retention", "ingest", str(csv_path), "--video-id", "v1",
        "--title", "Video", "--duration-s", "60", "--file", str(tmp_path / "curves.jsonl"),
    ])
    assert rc == 2
    assert "average percentage viewed is not a curve" in capsys.readouterr().out
