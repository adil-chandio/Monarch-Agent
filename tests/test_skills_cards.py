"""Accuracy tests: skills reference real commands, agents map to real states.

The repo's promise is "commands are real, gates are real" — these tests keep
the ruflo-inspired docs honest. If a skill mentions ``monarch <cmd>``, that
command must exist in the CLI; if a role card claims an M-state, that state
must exist in the state machine.
"""

from __future__ import annotations

import re
from pathlib import Path

from monarch.core.state_machine import STATES

REPO = Path(__file__).resolve().parents[1]
SKILLS_DIR = REPO / "monarch" / "skills"
AGENTS_DIR = REPO / "monarch" / "agents"
CLI_SRC = (REPO / "monarch" / "cli.py").read_text(encoding="utf-8")

EXPECTED_SKILLS = {
    "make-short",
    "forensic-hunt",
    "sfx-design",
    "thumbnail-pack",
    "metadata-seo",
    "upload-day",
}


def _frontmatter(path: Path) -> dict:
    lines = path.read_text(encoding="utf-8").splitlines()
    assert lines and lines[0].strip() == "---", f"{path} missing frontmatter"
    end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    out: dict = {}
    fold_key = None
    for line in lines[1:end]:
        if line[:1] in (" ", "\t") and fold_key:  # folded (> | block) value
            out[fold_key] = f"{out[fold_key]} {line.strip()}".strip()
            continue
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        v = v.strip()
        if v in (">", "|", ">-", "|-"):  # YAML folded scalar — collect indents
            fold_key = k.strip()
            out[fold_key] = ""
        else:
            fold_key = None
            out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def _registered_commands() -> set[str]:
    """Top-level subparsers actually registered in cli.py."""
    return set(re.findall(r'sub\.add_parser\(\s*"([a-z0-9-]+)"', CLI_SRC))


def test_six_skills_exist():
    found = {p.parent.name for p in SKILLS_DIR.glob("*/SKILL.md")}
    assert found == EXPECTED_SKILLS


def test_skill_frontmatter_is_valid():
    names = set()
    for path in SKILLS_DIR.glob("*/SKILL.md"):
        fm = _frontmatter(path)
        assert fm.get("name") == path.parent.name, f"{path}: name must match dir"
        assert len(fm.get("description", "")) > 30, f"{path}: description too thin"
        names.add(fm["name"])
    assert len(names) == len(EXPECTED_SKILLS)  # unique


def test_every_command_in_skills_is_real():
    """Any `monarch <cmd>` mentioned in a skill must be a registered command."""
    registered = _registered_commands()
    for path in sorted(SKILLS_DIR.glob("*/SKILL.md")):
        text = path.read_text(encoding="utf-8")
        for cmd in set(re.findall(r"monarch ([a-z][a-z0-9-]*)", text)):
            assert cmd in registered, f"{path}: 'monarch {cmd}' is not a real command"


def test_every_repo_file_referenced_by_skills_exists():
    pattern = re.compile(r"monarch/[A-Za-z0-9_/.-]+\.(?:md|py|json)")
    for path in SKILLS_DIR.glob("*/SKILL.md"):
        for rel in set(pattern.findall(path.read_text(encoding="utf-8"))):
            assert (REPO / rel).is_file(), f"{path}: referenced {rel} does not exist"


def test_skills_mention_their_gates():
    """Fail-closed skills must name the stop, not just the happy path."""
    checks = {
        "make-short": ["HAAN"],
        "forensic-hunt": ["STOP"],
        "sfx-design": ["L2"],
        "thumbnail-pack": ["L4"],
        "metadata-seo": ["gate-title"],
        "upload-day": ["monarch memory save"],
    }
    for skill, needles in checks.items():
        text = (SKILLS_DIR / skill / "SKILL.md").read_text(encoding="utf-8")
        for needle in needles:
            assert needle in text, f"{skill}: must mention {needle!r}"


def test_five_agent_cards_exist():
    cards = sorted(AGENTS_DIR.glob("*.md"))
    assert len(cards) == 5
    assert {c.stem for c in cards} == {
        "forensic_analyst_F0_M2",
        "script_doctor_M3",
        "sfx_designer_M5",
        "thumbnail_strategist_M6",
        "seo_packer_P3",
    }


def test_agent_cards_map_to_real_states():
    for path in AGENTS_DIR.glob("*.md"):
        fm = _frontmatter(path)
        assert fm.get("state") in STATES, f"{path}: unknown state {fm.get('state')!r}"
        assert fm.get("handoff") in STATES, f"{path}: unknown handoff {fm.get('handoff')!r}"
        assert fm.get("mission"), f"{path}: mission required"


def test_lessons_file_exists_for_the_loop():
    assert (REPO / "monarch" / "self_improve" / "lessons.md").is_file()


def test_gitignore_covers_session_state():
    gitignore = (REPO / ".gitignore").read_text(encoding="utf-8")
    assert ".monarch/" in gitignore
