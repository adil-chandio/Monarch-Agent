"""W-B3 tests - the survival layer + the launch kit.

slop.py: the channel-level inauthentic-content tripwires (assembly-line
signature via topic-stripped VO similarity, genre/cadence advisories,
persona presence, disclosure shield, VO coverage). kit.py: one-shot
launch kit (title law, disclosure MANDATORY, no-bio-link, pinned bait,
first-frame thumbnail, honest checklist). CLI: package + slop-audit rc
contracts.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from monarch.cli import main
from monarch.video.kit import emit_kit
from monarch.video.pipeline import make_video
from monarch.video.slop import slop_audit


@pytest.fixture(scope="module")
def voiced_dir(tmp_path_factory):
    d = tmp_path_factory.mktemp("wb3") / "channel" / "render-a"
    make_video("the doctor who vanished mid-surgery", d, length=10.5,
               fps=1, seed=51, voice_backend="mumble", do_mix=True,
               v6_end_screen=True)
    return d


# ---------------------------------------------------------------------------
# kit emitter
# ---------------------------------------------------------------------------


def test_kit_files_and_laws(voiced_dir):
    pkg = emit_kit(voiced_dir, shorts=True,
                   title="The Doctor Who Vanished", topics=None)
    kit = voiced_dir / "kit"
    for name in ("title.txt", "description.txt", "pinned_comment.txt",
                 "disclosure.txt", "package.json", "upload_checklist.txt"):
        assert (kit / name).is_file(), name
    assert "ai-generated" in pkg["description"].lower()      # shield ships
    assert "link in bio" not in pkg["description"].lower()   # miss #13
    assert "on screen now" in pkg["description"].lower()     # shorts pointer
    assert pkg["title_check"]["ok"] and pkg["title_check"]["chars"] == 23
    assert pkg["thumbnail"] and "first_frame" in pkg["thumbnail"]
    assert "[ ]" in "\n".join(pkg["checklist"])              # honest gaps


def test_kit_pinned_comment_carries_the_tease(voiced_dir):
    pkg = emit_kit(voiced_dir, title="The Doctor Who Vanished",
                   topics=["Panda", "Sun", "Sloth", "Polar", "Grizzly"])
    assert "YOUR TOP 3" in pkg["pinned_comment"]
    assert "censored" in pkg["pinned_comment"].lower()
    assert "Grizzly" in pkg["pinned_comment"]


def test_kit_shorts_without_end_screen_flags_the_fix(tmp_path):
    d = tmp_path / "noes"
    make_video("the doctor who vanished mid-surgery", d, length=8.0,
               fps=1, seed=53, voice_backend="mumble",
               v6_end_screen=False)
    pkg = emit_kit(d, shorts=True, title="The Doctor Vanished")
    assert "on screen now" in pkg["description"].lower()
    assert any("--v6-end-screen" in line for line in pkg["checklist"])


def test_kit_fail_closed_on_missing_board(tmp_path):
    with pytest.raises(ValueError, match="board.json"):
        emit_kit(tmp_path)


# ---------------------------------------------------------------------------
# slop audit
# ---------------------------------------------------------------------------


def _mk_channel(tmp_path, vo_lines, title="Probe Channel Topic"):
    ch = tmp_path / "channel"
    ch.mkdir(exist_ok=True)
    for i in range(len(vo_lines)):
        d = ch / f"render-{i}"
        d.mkdir(exist_ok=True)
        (d / "board.json").write_text(json.dumps(
            [{"id": j + 1, "retention_role": "body", "vo_line": v,
              "t_start": j * 3.0, "t_end": (j + 1) * 3.0,
              "neuro_driver": ""} for j, v in enumerate(vo_lines[i])]),
            encoding="utf-8")
        (d / "timeline.json").write_text(json.dumps(
            {"title": title, "total_s": 9.0, "genre": "mystery"}),
            encoding="utf-8")
        (d / "frames").mkdir(exist_ok=True)
        (d / "frames" / "frame_00001.png").write_bytes(b"\x89PNG fake")
    return ch


def test_slop_flags_the_assembly_line(tmp_path):
    same = [["The bear sat down slowly.", "Then the bear stood up.",
             "The bear walked away home."]] * 3
    ch = _mk_channel(tmp_path, same)
    r = slop_audit(ch, now=1_000_000.0)
    assert not r["ok"]
    joined = " ".join(f["finding"] for f in r["findings"])
    assert "assembly-line" in joined
    assert "no AI-disclosure" in joined          # shield missing -> P1
    assert r["score"] < 60


def test_slop_clean_channel_passes(tmp_path):
    varied = [
        ["The doctor vanished mid-surgery.", "But nobody saw him leave.",
         "The hospital locked the floor."],
        ["Polar bears rule the ice.", "But one grizzly disagreed.",
         "The whale carcass told the truth."],
        ["This lighthouse keeps no light.", "Yet ships follow it home.",
         "The keeper never existed."],
    ]
    ch = _mk_channel(tmp_path, varied)
    for i in range(3):
        emit_kit(ch / f"render-{i}",
                 title="Probe Channel Topic")   # ships the disclosure
    r = slop_audit(ch, now=1_000_000.0)
    assert r["ok"], [f for f in r["findings"] if f["priority"] == "P1"]
    assert r["score"] >= 80


def test_slop_single_dir_is_advisory(tmp_path):
    ch = _mk_channel(tmp_path, [["Only one render exists here."]])
    r = slop_audit(ch, now=1_000_000.0)
    assert r["advisory_only"] and r["ok"]


def test_slop_fail_closed_on_missing_channel(tmp_path):
    with pytest.raises(ValueError, match="not found"):
        slop_audit(tmp_path / "ghost")


# ---------------------------------------------------------------------------
# CLI contracts
# ---------------------------------------------------------------------------


def test_cli_package_and_slop(voiced_dir, capsys):
    rc = main(["package", str(voiced_dir), "--shorts",
               "--title", "The Doctor Who Vanished"])
    out = capsys.readouterr().out
    assert rc == 0 and "KIT" in out and "disclosure: shipped" in out
    ch = str(voiced_dir.parent)
    rc2 = main(["slop-audit", ch, "--json"])
    out2 = capsys.readouterr().out
    rep = json.loads(out2)
    assert rc2 == 0 and rep["ok"]
    assert "SLOP AUDIT" in out2 or "{" in out2


def test_cli_slop_audit_names_the_slop(tmp_path, capsys):
    same = [["The bear sat down slowly.", "Then the bear stood up.",
             "The bear walked away home."]] * 3
    ch = _mk_channel(tmp_path, same)
    rc = main(["slop-audit", str(ch)])
    out = capsys.readouterr().out
    assert rc == 2 and "assembly-line" in out and "P1 PRESENT" in out


def test_cli_package_missing_dir(tmp_path, capsys):
    rc = main(["package", str(tmp_path / "ghost")])
    assert rc == 2 and "FAIL" in capsys.readouterr().out
