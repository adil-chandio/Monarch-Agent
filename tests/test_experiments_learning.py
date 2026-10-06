from __future__ import annotations

import json

import pytest

from monarch.cli import main
from monarch.core.experiments import (
    NativeExperimentResult,
    load_experiment_results,
    record_experiment_result,
)


def _result(**overrides):
    values = {
        "test_id": "studio-test-1",
        "video_id": "video-1",
        "title": "Test video",
        "test_type": "thumbnail",
        "variants": ("A", "B"),
        "outcome": "winner",
        "winner_variant": "A",
        "window_start": "2026-09-01",
        "window_end": "2026-09-08",
    }
    values.update(overrides)
    return NativeExperimentResult(**values)


def test_native_experiment_result_round_trip_is_explicitly_unverified(tmp_path):
    result = _result()
    path = record_experiment_result(result, tmp_path / "experiments.jsonl")
    loaded = load_experiment_results(path, video_id="video-1")
    assert loaded == [result]
    payload = result.to_dict()
    assert payload["platform"] == "YouTube Studio"
    assert payload["decision_metric"] == "watch_time"
    assert payload["outcome"] == "winner"
    assert payload["winner_variant"] == "A"
    assert payload["source_result_verified"] is False
    assert load_experiment_results(path, video_id="other") == []


def test_inconclusive_and_performed_same_cannot_be_assigned_a_winner():
    for outcome in ("inconclusive", "performed_same"):
        result = _result(outcome=outcome, winner_variant="")
        assert result.winner_variant == ""
        assert result.to_dict()["winner_variant"] is None
    with pytest.raises(ValueError, match="must not be assigned"):
        _result(outcome="inconclusive")


def test_winner_requires_variant_in_recorded_options():
    with pytest.raises(ValueError, match="winner_variant is required"):
        _result(winner_variant="")
    with pytest.raises(ValueError, match="must match"):
        _result(winner_variant="C")
    with pytest.raises(ValueError, match="winner_variant is required"):
        _result(outcome="preferred", winner_variant="")


def test_experiment_input_fails_closed_on_bad_variants_or_window():
    with pytest.raises(ValueError, match="2 or 3 variants"):
        _result(variants=("A",))
    with pytest.raises(ValueError, match="unique"):
        _result(variants=("A", "A"))
    with pytest.raises(ValueError, match="2 or 3 variants"):
        _result(variants=("A", "B", "C", "D"))
    with pytest.raises(ValueError, match="ISO date"):
        _result(window_start="yesterday")
    with pytest.raises(ValueError, match="on or before"):
        _result(window_start="2026-09-09", window_end="2026-09-08")


def test_corrupt_experiment_log_fails_with_line_number(tmp_path):
    path = tmp_path / "experiments.jsonl"
    path.write_text(json.dumps(_result().to_dict()) + "\nnot-json\n", encoding="utf-8")
    with pytest.raises(ValueError, match=r"line 2"):
        load_experiment_results(path)


def test_cli_records_inconclusive_result_and_logs_json(capsys, tmp_path):
    path = tmp_path / "experiments.jsonl"
    rc = main([
        "learn", "experiment", "record",
        "--test-id", "native-1", "--video-id", "video-1", "--title", "Video",
        "--test-type", "title_and_thumbnail", "--outcome", "inconclusive",
        "--variant", "A", "--variant", "B", "--file", str(path),
    ])
    out = capsys.readouterr().out
    assert rc == 0
    assert "inconclusive" in out
    assert "NOT VERIFIED" in out

    log_rc = main([
        "learn", "experiment", "log", "--video-id", "video-1",
        "--file", str(path), "--json",
    ])
    logged = json.loads(capsys.readouterr().out)
    assert log_rc == 0
    assert len(logged) == 1
    assert logged[0]["outcome"] == "inconclusive"
    assert logged[0]["winner_variant"] is None
    assert logged[0]["source_result_verified"] is False


def test_cli_rejects_fabricated_winner_for_inconclusive_result(capsys, tmp_path):
    rc = main([
        "learn", "experiment", "record",
        "--test-id", "native-2", "--video-id", "video-2", "--title", "Video",
        "--test-type", "thumbnail", "--outcome", "inconclusive",
        "--variant", "A", "--variant", "B", "--winner-variant", "A",
        "--file", str(tmp_path / "experiments.jsonl"),
    ])
    assert rc == 2
    assert "must not be assigned" in capsys.readouterr().out
