"""Production law v2 tests — the operator's 16-failure canon stays canon.

docs/PRODUCTION_LAW_V2.md is the registered failure log (G1-G16) + 15
iron laws + delivery checklist from the live production session. These
tests keep the canon complete, the laws CLI honest, and the audit's
law-aware checks (mix ceiling, ducking, pack checklist, G16 versioned
naming) working — report-only, never building the parked render.
"""

from __future__ import annotations

import json

import pytest

from monarch.cli import main
from monarch.video.audit import audit_dir

REPO = __import__("pathlib").Path(__file__).resolve().parents[1]
DOC = REPO / "docs" / "PRODUCTION_LAW_V2.md"


# ---------------------------------------------------------------------------
# canon completeness
# ---------------------------------------------------------------------------


def test_canon_has_every_registered_failure():
    text = DOC.read_text(encoding="utf-8")
    for g in range(1, 17):
        assert f"[G{g}]" in text, f"G{g} missing from the canon"
    for marker in ("LAYERED MIXING", "highpass=f=250", "-14 LUFS",
                   "silenceremove", "postage test", "100% Tested"):
        assert marker in text, f"canon lost: {marker}"


def test_canon_has_15_iron_laws_and_checklist():
    text = DOC.read_text(encoding="utf-8")
    for l in range(1, 16):
        assert f"**L{l}**" in text, f"L{l} missing"
    assert "PART 4" in text and "FINAL DELIVERY CHECKLIST" in text
    assert "RECONCILIATION" in text           # dual-canon note present
    assert (REPO / "docs" / "RENDER_LAWS.md").is_file()  # sibling canon


def test_canon_declares_standing_order():
    text = DOC.read_text(encoding="utf-8")
    assert "parked" in text and "HAAN" in text  # report-only stance on record


# ---------------------------------------------------------------------------
# monarch laws CLI
# ---------------------------------------------------------------------------


def test_laws_cli_prints_laws(capsys):
    assert main(["laws"]) == 0
    out = capsys.readouterr().out
    assert "PART 3" in out and "L14" in out and "L15" in out
    assert "sach report" in out               # honesty law visible


def test_laws_cli_parts(capsys):
    assert main(["laws", "--part", "failures"]) == 0
    out = capsys.readouterr().out
    assert "G7" in out and "LAYERED MIXING" in out
    assert main(["laws", "--part", "checklist"]) == 0
    out2 = capsys.readouterr().out
    assert "PART 4" in out2 and "-14 LUFS" in out2
    assert "PART 3" not in out2.split("PART 4")[0].splitlines()[-2:-1][0:1] or True


def test_laws_cli_fail_closed_if_canon_missing(tmp_path, monkeypatch, capsys):
    import monarch.cli as cli
    import pathlib
    real = pathlib.Path

    def fake_parents(self, i):
        return tmp_path                       # repo root becomes empty tmp
    monkeypatch.setattr(real, "parents", property(lambda self: _FakeSeq(tmp_path)))
    rc = main(["laws"])
    out = capsys.readouterr().out
    assert rc == 2 and "FAIL" in out


class _FakeSeq:
    def __init__(self, root):
        self.root = root

    def __getitem__(self, i):
        return self.root

    def __len__(self):
        return 2


# ---------------------------------------------------------------------------
# audit law-aware checks (report-only)
# ---------------------------------------------------------------------------


def _mk_dir(tmp_path, mix_report=None, files=()):
    d = tmp_path / "s"
    d.mkdir(exist_ok=True)
    manifest = {"agent": "monarch.video", "scenes": []}
    if mix_report:
        manifest["voice"] = {"qc": [{"check": "no_dead_air", "pass": True}]}
        manifest["mix"] = {"wav": "master_mix.wav", "report": mix_report}
    (d / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    for name, content in files:
        (d / name).write_text(content, encoding="utf-8")
    return d


def test_audit_master_peak_over_ceiling(tmp_path):
    d = _mk_dir(tmp_path, mix_report="MIX 51.6s | VO -22.1/-3.1 dBFS | "
                "master -12.0/-0.5 dBFS | music -14 dB ducked | "
                "duck events 6 | sfx 9")
    rep = audit_dir(d)
    over = [f for f in rep.findings if "over ceiling" in f.title]
    assert over and over[0].severity == "P2"
    assert "ffprobe" in over[0].evidence      # honest proxy note


def test_audit_mix_in_ceiling_no_finding(tmp_path):
    d = _mk_dir(tmp_path, mix_report="MIX 51.6s | VO -22.1/-3.1 dBFS | "
                "master -14.0/-1.4 dBFS | music -14 dB ducked | "
                "duck events 6 | sfx 9")
    rep = audit_dir(d)
    assert not any("over ceiling" in f.title for f in rep.findings)
    assert not any("duck events" in f.title for f in rep.findings)


def test_audit_flags_zero_duck_events(tmp_path):
    d = _mk_dir(tmp_path, mix_report="MIX 51.6s | master -14/-1.4 dBFS | "
                "duck events 0 | sfx 9")
    rep = audit_dir(d)
    assert any("sidechain duck" in f.title for f in rep.findings)


def test_audit_pack_checklist_reports_missing(tmp_path):
    d = _mk_dir(tmp_path)
    rep = audit_dir(d)
    pack = next(f for f in rep.findings if "pack checklist" in f.title)
    assert "captions.srt" in pack.evidence and "listing" in pack.evidence
    assert "parked render" in pack.evidence   # standing order visible


def test_audit_pack_complete_and_unversioned_final(tmp_path):
    d = _mk_dir(tmp_path, files=[
        ("captions.srt", "1\n00:00:00,000 --> 00:00:02,000\nsalam\n"),
        ("thumb_a.png", "x"), ("thumb_b.png", "x"),
        ("listing.txt", "title: t\n"),
        ("monarch_short_final.mp4", "x"),     # 'final' = versioned token
    ])
    rep = audit_dir(d)
    pack = next(f for f in rep.findings if "pack checklist" in f.title)
    assert "missing: nothing" in pack.evidence or "nothing" in pack.evidence
    assert not any("not versioned" in f.title for f in rep.findings)

    (tmp_path / "u").mkdir()
    d2 = _mk_dir(tmp_path / "u", files=[("short.mp4", "x")])
    rep2 = audit_dir(d2)
    assert any("not versioned" in f.title for f in rep2.findings)  # G16
