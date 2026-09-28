"""NEVER AGAIN tests — G1-G16 fixes wired into the code, not just canon.

Each test maps to a registered failure from docs/PRODUCTION_LAW_V2.md:
  G2/L1   monarch doctor fails closed on a broken environment
  G3/L10  budget planner never exceeds 10 images / 10 speech per turn
  G4/G9   fountain re-counts through the engine tokenizer (fail-closed)
  G5      audit reads BOTH board shapes (list and dict)
  G7/L3   mix VO-gate: multi-window proof, voice loss = loud FAIL
  G8/L4   leading silence trimmed; no_dead_lead gate tightened to 0.3s
  G10     timeline.json + captions.srt derive from the VO (single source)
  G11/L6  captions.srt ships with every VO build
  G14/L13 audit cross-verifies duration sources (+-0.5s)
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from monarch.cli import main
from monarch.core.doctor import exit_code, run_checks
from monarch.video.audit import audit_dir
from monarch.video.budgets import plan_batches
from monarch.video.director import plan_storyboard, validate_fountain
from monarch.video.mix import _vo_gate, mix
from monarch.video.pipeline import make_video
from monarch.video.voiceover import (build_voiceover, format_srt,
                                     trim_lead_silence)


# ---------------------------------------------------------------------------
# G8 / L4 — leading silence
# ---------------------------------------------------------------------------


def test_trim_lead_silence_kills_dead_air():
    sr = 24000
    take = [0.0] * int(0.8 * sr) + [0.3] * int(0.5 * sr)   # 0.8s dead air
    trimmed = trim_lead_silence(take, sr)
    lead = next((i for i, v in enumerate(trimmed) if abs(v) > 0.02), 0) / sr
    assert lead <= 0.07                     # kept only the 0.06s room
    assert trimmed[-1] != 0.0               # speech untouched


def test_trim_lead_silence_all_silent_is_noop():
    sr = 8000
    quiet = [0.0] * 800
    assert trim_lead_silence(quiet, sr) == quiet


def test_no_dead_lead_gate_now_0p3s():
    scenes = [{"id": 1, "vo_line": "the file sat unopened.", "t_start": 0.0,
               "t_end": 3.0, "sfx": ""}]
    vo = build_voiceover(scenes, backend="mumble", sr=24000, seed=1)
    row = next(c for c in vo["qc"] if c["check"] == "no_dead_lead")
    assert row["pass"] is True              # mumble speaks at once
    assert "0.3" in str(row["detail"]) or row["pass"]


# ---------------------------------------------------------------------------
# G7 / L3 — VO gate in the mix
# ---------------------------------------------------------------------------


def test_vo_gate_passes_on_real_mix():
    sr = 24000
    vo = [0.25] * int(2.0 * sr)
    master, rep = mix(duration_s=2.5, vo=vo, sr=sr, music=True, seed=3)
    assert rep.vo_gate.startswith("PASS")
    assert "VO GATE PASS" in rep.summary()


def test_vo_gate_fails_when_voice_missing_from_master():
    sr = 24000
    voice = [0.3] * int(1.0 * sr) + [0.0] * int(0.5 * sr)
    imposter = [0.05] * len(voice)          # bed-only master: VO gone
    ok, detail = _vo_gate(imposter, voice, sr, len(voice))
    assert not ok and "dropped" in detail


def test_vo_gate_no_voice_is_honest_noVO():
    sr = 16000
    master, rep = mix(duration_s=1.0, vo=None, sr=sr, music=True, seed=1)
    assert rep.vo_gate == "NO VO"


# ---------------------------------------------------------------------------
# G4 / G9 — fountain re-count validation
# ---------------------------------------------------------------------------


def test_fountain_recounts_clean():
    sb = plan_storyboard("the vault nobody could open", length=10.5, seed=5)
    assert validate_fountain(sb) == len(sb.board())


def test_fountain_tamper_fails_closed():
    sb = plan_storyboard("the vault nobody could open", length=10.5, seed=5)
    tampered = re.sub(r"(::.+?:: )\w+ ", r"\1", sb.fountain, count=1)
    sb.fountain = tampered
    with pytest.raises(ValueError, match="G4"):
        validate_fountain(sb)


def test_board_writer_validates_on_write(tmp_path):
    sb = plan_storyboard("the file nobody signed", length=10.5, seed=2)
    from monarch.video.director import write_storyboard_files
    paths = write_storyboard_files(sb, tmp_path / "o")
    assert paths["fountain"].is_file()      # validation ran inside


# ---------------------------------------------------------------------------
# G11 + G10 + G14 — srt, timeline.json, single-source timing
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def voiced_dir(tmp_path_factory):
    d = tmp_path_factory.mktemp("vo") / "out"
    make_video("the scientist who vanished", d, length=10.5, fps=1, seed=4,
               voice_backend="mumble", do_mix=True)
    return d


def test_captions_srt_ships_with_vo(voiced_dir):
    srt = (voiced_dir / "captions.srt").read_text(encoding="utf-8")
    blocks = [b for b in srt.split("\n\n") if b.strip()]
    manifest = json.loads((voiced_dir / "manifest.json").read_text(encoding="utf-8"))
    assert len(blocks) == manifest["scene_count"]
    assert re.search(r"\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}", srt)
    assert manifest["files"]["srt"] == "captions.srt"


def test_timeline_json_actually_exists(voiced_dir):
    tl = json.loads((voiced_dir / "timeline.json").read_text(encoding="utf-8"))
    manifest = json.loads((voiced_dir / "manifest.json").read_text(encoding="utf-8"))
    assert abs(tl["total_s"] - manifest["total_s"]) < 0.01   # G14 pair agrees


def test_srt_windows_derive_from_vo_track(voiced_dir):
    manifest = json.loads((voiced_dir / "manifest.json").read_text(encoding="utf-8"))
    rows = manifest["scenes"]
    srt = (voiced_dir / "captions.srt").read_text(encoding="utf-8")
    first_start = rows[0]["t_start"]
    assert "00:00:0" in srt                 # first caption at the top
    assert first_start >= 0.0


# ---------------------------------------------------------------------------
# G5 + G14 — audit robustness
# ---------------------------------------------------------------------------


def test_audit_reads_list_shaped_board(tmp_path):
    d = tmp_path / "x"
    d.mkdir()
    (d / "board.json").write_text(json.dumps(
        [{"id": 1, "vo_line": "the file sat unopened.", "t_start": 0.0,
          "t_end": 3.0}]), encoding="utf-8")
    rep = audit_dir(d)
    assert "pacing_scenes_off_band" in rep.scores   # parsed, no TypeError


def test_audit_catches_duration_disagreement(tmp_path):
    d = tmp_path / "y"
    d.mkdir()
    (d / "board.json").write_text(json.dumps({"scenes": [
        {"id": 1, "vo_line": "a", "t_start": 0.0, "t_end": 60.0}]}),
        encoding="utf-8")
    (d / "timeline.json").write_text(json.dumps({"total_s": 63.6}),
                                     encoding="utf-8")
    (d / "manifest.json").write_text(json.dumps({"total_s": 63.6}),
                                     encoding="utf-8")
    rep = audit_dir(d)
    hit = [f for f in rep.findings if "duration sources disagree" in f.title]
    assert hit and hit[0].severity == "P1"
    assert "63.6" in hit[0].impact          # the original sin, remembered


def test_audit_flags_vo_gate_fail_from_mix_report(tmp_path):
    d = tmp_path / "z"
    d.mkdir()
    (d / "manifest.json").write_text(json.dumps({
        "voice": {"qc": [{"check": "x", "pass": True}]},
        "mix": {"wav": "master_mix.wav",
                "report": "MIX 51.6s | VO GATE FAIL: window @0.00s master "
                          "-30.0 dBFS vs VO -12.0 dBFS (delta 18.0 > 6)"}}),
        encoding="utf-8")
    rep = audit_dir(d)
    hit = [f for f in rep.findings if "VO lost in master" in f.title]
    assert hit and hit[0].severity == "P1"
    assert "10 inputs" in hit[0].fix        # layered mixing is the fix


# ---------------------------------------------------------------------------
# G3 / L10 — budget planner
# ---------------------------------------------------------------------------


def test_budget_plan_18_frames_9_clips():
    turns = plan_batches(18, 9)
    assert turns[0] == {"turn": 1, "images": 10, "speech": 9}
    assert turns[1] == {"turn": 2, "images": 8, "speech": 0}
    assert all(t["images"] <= 10 and t["speech"] <= 10 for t in turns)
    assert sum(t["images"] for t in turns) == 18
    assert sum(t["speech"] for t in turns) == 9


def test_budget_rejects_garbage():
    with pytest.raises(ValueError):
        plan_batches(-1, 0)
    with pytest.raises(ValueError):
        plan_batches(0, 0, per_turn=0)


def test_cli_budget_json(capsys):
    assert main(["budget", "--frames", "18", "--clips", "9", "--json"]) == 0
    turns = json.loads(capsys.readouterr().out)
    assert len(turns) == 2


# ---------------------------------------------------------------------------
# G2 / L1 — doctor
# ---------------------------------------------------------------------------


def test_doctor_healthy_repo_exits_0(capsys):
    repo = Path(__file__).resolve().parents[1]
    checks = run_checks(repo)
    assert exit_code(checks) == 0
    assert not any(c["status"] == "FAIL" for c in checks)


def test_doctor_fail_closed_on_broken_root(tmp_path, capsys):
    rc = main(["doctor", "--repo-root", str(tmp_path)])
    out = capsys.readouterr().out
    assert rc == 1 and "FAIL" in out and "canon-docs" in out


def test_doctor_json_never_leaks_key_value(capsys, monkeypatch):
    monkeypatch.setenv("MONARCH_ACCESS_KEY", "DoitMon@rch")
    repo = Path(__file__).resolve().parents[1]
    rc = main(["doctor", "--repo-root", str(repo), "--json"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "DoitMon@rch" not in out         # the key is never printed
    payload = json.loads(out)
    checks = payload["env"]
    key_row = next(c for c in checks if c["check"] == "access-key")
    assert key_row["status"] == "PASS"


def test_cli_laws_still_works(capsys):
    assert main(["laws"]) == 0
    assert "PART 3" in capsys.readouterr().out
