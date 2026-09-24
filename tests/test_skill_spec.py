"""W4 CHAOS tests — agentskills.io spec compliance for every SKILL.md.

The open Agent Skills standard (adopted by 26+ platforms): a skill is a
folder whose SKILL.md has YAML frontmatter with ONLY the allowed keys,
a name that matches the parent directory (lowercase/digits/hyphens,
<=64 chars, no leading/trailing/double hyphen), a description of
1..1024 chars, and a body <= 500 lines. Monarch's skills were born in
this shape — these tests keep them certified as the standard evolves.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SKILLS = REPO / "monarch" / "skills"

ALLOWED_KEYS = {"name", "description", "license", "compatibility",
                "metadata", "allowed-tools"}
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def _frontmatter(text: str) -> tuple[dict, list[str]]:
    """Minimal frontmatter parse: top-level keys + folded scalar values."""
    assert text.startswith("---\n"), f"{text[:20]}: frontmatter must start at byte 0"
    end = text.find("\n---", 3)
    assert end > 0, "frontmatter must be closed with ---"
    block = text[4:end]
    body = text[end + 4:].lstrip("\n")
    fm: dict[str, str] = {}
    key = None
    buf: list[str] = []
    for line in block.splitlines():
        top = re.match(r"^([a-z][a-z0-9-]*):(.*)$", line)
        if top and not line.startswith((" ", "\t")):
            if key:
                fm[key] = " ".join(b.strip() for b in buf if b.strip())
            key = top.group(1)
            init = top.group(2).strip()
            buf = [] if init in (">", ">-", "|", "|-") else (
                [init] if init else [])
        elif key:
            buf.append(line.strip())
    if key:
        fm[key] = " ".join(b.strip() for b in buf if b.strip())
    return fm, body.splitlines()


def test_every_skill_is_spec_compliant():
    cards = sorted(SKILLS.glob("*/SKILL.md"))
    assert len(cards) >= 7, "skill cards went missing"
    for card in cards:
        folder = card.parent.name
        fm, body_lines = _frontmatter(card.read_text(encoding="utf-8"))
        unknown = set(fm) - ALLOWED_KEYS
        assert not unknown, f"{folder}: unknown frontmatter keys {unknown}"
        name = fm.get("name", "")
        assert NAME_RE.match(name), f"{folder}: bad name {name!r}"
        assert len(name) <= 64 and name == folder, f"{folder}: name/dir mismatch"
        desc = fm.get("description", "")
        assert 1 <= len(desc) <= 1024, \
            f"{folder}: description must be 1..1024 chars (got {len(desc)})"
        assert len(body_lines) <= 500, f"{folder}: body over 500 lines"


def test_descriptions_carry_trigger_keywords():
    """Standard guidance: description = what + when (activation keywords)."""
    for card in sorted(SKILLS.glob("*/SKILL.md")):
        fm, _ = _frontmatter(card.read_text(encoding="utf-8"))
        low = fm.get("description", "").lower()
        assert "monarch" in low or "use" in low or "when" in low, \
            f"{card.parent.name}: description lacks when-to-use cue"
