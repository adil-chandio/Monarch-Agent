from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
KNOWLEDGE = REPO / "monarch" / "knowledge"


def test_knowledge_index_links_resolve():
    index = (KNOWLEDGE / "README.md").read_text(encoding="utf-8")
    expected = [
        "AGENT_OPERATING_STANDARD.md",
        "ROLE_COMPETENCIES.md",
        "YOUTUBE_PERFORMANCE.md",
        "LEARNING_DESIGN_AND_AUDIO.md",
        "CAPABILITY_MAP.md",
        "EVALUATION_CATALOG.md",
        "SOURCES.md",
        "templates/channel_bible.template.json",
        "templates/evidence_record.template.json",
        "templates/experience_record.template.json",
        "templates/run_manifest.template.json",
        "templates/retention_curve_record.template.json",
        "templates/experiment_result.template.json",
        "evals/golden_cases.json",
    ]
    for relative in expected:
        assert (KNOWLEDGE / relative).is_file(), f"missing indexed reference: {relative}"
        assert relative in index


def test_channel_and_run_templates_are_cautious_by_default():
    def load_template(name: str) -> dict:
        return json.loads((KNOWLEDGE / "templates" / name).read_text(encoding="utf-8"))

    channel = load_template("channel_bible.template.json")
    run = load_template("run_manifest.template.json")
    evidence = load_template("evidence_record.template.json")
    retention = load_template("retention_curve_record.template.json")
    experiment = load_template("experiment_result.template.json")
    assert channel["approved_by_operator"] is False
    assert channel["status"] == "DRAFT"
    assert channel["brand"]["visual_style_a"]["status"] == "EXISTING_CANONICAL_WORKFLOW_UNCHANGED"
    assert run["workflow"]["current_state"] == "I0_intake"
    assert run["workflow"]["wait_owner"] == "operator"
    assert run["release"]["rights_status"] == "UNKNOWN"
    assert run["release"]["release_decision"] == "BLOCKED"
    assert evidence["class"] == "UNKNOWN"
    assert retention["source_authorization_verified"] is False
    assert experiment["source_result_verified"] is False
    assert experiment["outcome"] == "inconclusive"
    assert experiment["winner_variant"] is None


def test_experience_template_separates_prediction_observation_and_approval():
    record = json.loads(
        (KNOWLEDGE / "templates/experience_record.template.json").read_text(encoding="utf-8")
    )
    assert {"hypothesis", "prediction", "observation", "experiment", "outcome"} <= set(record)
    assert record["experiment"]["native_result"] == "NOT_RUN"
    assert record["approved_for_channel_memory"] is False
    assert record["approved_by_operator"] is None


def test_golden_cases_are_unique_and_cover_critical_regressions():
    cases = json.loads((KNOWLEDGE / "evals/golden_cases.json").read_text(encoding="utf-8"))
    ids = [case["id"] for case in cases]
    assert len(ids) >= 15
    assert len(ids) == len(set(ids))
    for case in cases:
        assert case["prompt"]
        assert case["expected_behavior"]
        assert case["must_not"]
    assert {
        "APV-TO-EXACT-DROP-01",
        "AB-INCONCLUSIVE-01",
        "STYLE-A-IMMUTABLE-01",
        "STYLE-B-CONSTRAINTS-01",
        "USER-GATE-01",
    } <= set(ids)


def test_manager_contract_keeps_human_gates_and_is_not_a_hidden_runtime():
    skill = (REPO / "monarch/skills/executive-producer/SKILL.md").read_text(encoding="utf-8")
    role = (REPO / "monarch/agents/executive_producer.md").read_text(encoding="utf-8")
    for text in (skill, role):
        assert "WAIT" in text
        assert "Style A" in text
        assert "human" in text.lower()
        assert "NOT MEASURED" in text
    assert "does not pretend Monarch has a hidden multi-agent execution service" in skill
    assert "run_manifest.template.json" in skill


def test_agent_entrypoints_integrate_manager_after_access_without_weakening_waits():
    boot = (REPO / "BOOT.md").read_text(encoding="utf-8")
    agent = (REPO / "AGENT.md").read_text(encoding="utf-8")
    for text in (boot, agent):
        assert "monarch/skills/executive-producer/SKILL.md" in text
        assert "monarch/agents/executive_producer.md" in text
        assert "knowledge/README.md" in text
        assert "WAIT" in text
    assert "After the existing access check" in boot
    assert "ask only for missing or" in boot
    assert "invalid fields, together in one concise block" in boot
    assert "not an autonomous multi-agent runtime" in boot
    assert "Style B remains additive" in boot


def test_capability_map_limits_retention_and_experiment_claims():
    capability_map = (KNOWLEDGE / "CAPABILITY_MAP.md").read_text(encoding="utf-8")
    assert "does not connect to YouTube" in capability_map
    assert "confirm account permissions" in capability_map
    assert "does not launch tests" in capability_map
    assert "verify the screenshot/source" in capability_map
    assert "NOT MEASURED" in capability_map
