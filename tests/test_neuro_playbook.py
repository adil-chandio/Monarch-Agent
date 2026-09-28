"""Tests for the Neuro-Psychology Playbook (N1-N5) and its code wiring."""

from __future__ import annotations

from pathlib import Path

import monarch
from monarch.video.director import NEURO_DRIVERS

PLAYBOOK = Path(monarch.__file__).parent / "playbook" / "neuro_psychology.md"


def test_playbook_exists():
    assert PLAYBOOK.is_file()


def test_all_five_laws_present():
    text = PLAYBOOK.read_text(encoding="utf-8")
    for n in range(1, 6):
        assert f"## N{n}" in text, f"law N{n} section missing"


def test_law_subjects_named():
    text = PLAYBOOK.read_text(encoding="utf-8").lower()
    for needle in (
        "superior colliculus",
        "amygdala",
        "0.1s",
        "kids",
        "gen z",
        "adults",
        "skinner",
        "variable",
        "cialdini",
        "reciprocity",
        "40hz",
        "0.3s",
    ):
        assert needle in text, f"playbook must mention {needle!r}"


def test_every_law_has_a_gate():
    """Monarch laws are fail-closed: each N-law carries a Gate line."""
    text = PLAYBOOK.read_text(encoding="utf-8")
    for n in range(1, 6):
        section = text.split(f"## N{n}", 1)[1]
        section = section.split("## N", 1)[0] if "## N" in section else section
        assert "Gate:" in section, f"law N{n} has no gate"


def test_pipeline_mapping_table():
    text = PLAYBOOK.read_text(encoding="utf-8")
    for module in ("director", "engine", "audio", "compositor"):
        assert module in text, f"pipeline mapping must cover {module}"


def test_drivers_registry_matches_playbook():
    """The director's NEURO_DRIVERS registry is the playbook made code."""
    text = PLAYBOOK.read_text(encoding="utf-8")
    assert set(NEURO_DRIVERS) == {
        "N1 THUMB-STOP",
        "N2 DOPAMINE",
        "N3 VARIABLE-RATIO",
        "N4 VALUE-DEBT",
        "N5 SILENCE-STING",
    }
    for driver_id, meta in NEURO_DRIVERS.items():
        law_id = driver_id.split()[0]
        assert law_id in text, f"{driver_id} missing from the playbook"
        assert meta["law"] and meta["gate"]
