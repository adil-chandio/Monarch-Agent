"""W3 CHAOS tests — The Eye (audit) + humanize v2 (hook exemption, rewrites)."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone

import pytest

from monarch.cli import main
from monarch.video.audit import audit_dir, ctr_band, hook_score
from monarch.video.humanize import humanize
from monarch.video.pipeline import make_video

TODAY = datetime(2026, 9, 24, tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# anchored scorers
# ---------------------------------------------------------------------------


def test_hook_score_anchored_bands():
    strong = hook_score("3 files vanished in 1971 — nobody talks about the 4th")
    assert strong >= 8                     # number + open markers + cold shape
    mid = hook_score("the hidden truth of the buried vault")       # marker only
    assert 4 <= mid <= 7
    weak = hook_score("today we discuss history")                  # base + none
    assert weak <= 3


def test_ctr_bands_match_playbook():
    assert ctr_band(2.1)[0] == "P1"
    assert ctr_band(3.5)[0] == "P3"
    assert ctr_band(5.0)[0] is None
    assert ctr_band(12.0)[0] is None


# ---------------------------------------------------------------------------
# humanize v2
# ---------------------------------------------------------------------------


def test_hook_mode_exempts_first_sentence_shape():
    text = "It's not just a file — it's a confession. Moreover, people miss it."
    clean, rep = humanize(text, hook=True)
    assert rep.hook_exempt and "not-just-dash" in rep.hook_exempt[0]
    assert all("confession" not in f for f in rep.flagged)


def test_body_mode_still_flags_shape_without_hook():
    text = ("The file sat unopened for fifty years. It's not just a mystery — "
            "it's a warning. People kept walking.")
    clean, rep = humanize(text, hook=False)
    assert rep.hook_exempt == []
    assert rep.signs_before > 0


def test_rewrites_suggested_mechanically():
    clean, rep = humanize("It's not just a vault — it's a promise, and the room "
                          "kept its silence for years while the city slept.")
    assert any("and" in r for r in rep.rewrites)


# ---------------------------------------------------------------------------
# audit on a real output dir
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def video_dir(tmp_path_factory):
    d = tmp_path_factory.mktemp("mv") / "out"
    make_video("the vault nobody could open", d, length=10.5, fps=1, seed=5,
               voice_backend="mumble", do_mix=True)
    return d


def test_audit_clean_previz_reports_parked_gap_only(video_dir):
    rep = audit_dir(video_dir)
    titles = [f.title for f in rep.findings]
    assert any(t.startswith("parked gap") for t in titles)     # reported, not built
    assert not any("voice QC failed" in t for t in titles)     # TABAAHI QC held
    assert rep.score >= 90


def test_audit_fail_closed_missing_dir(tmp_path):
    with pytest.raises(ValueError):
        audit_dir(tmp_path / "nope")


def test_audit_csv_ctr_breach_and_missing_column(tmp_path):
    d = tmp_path / "x"
    d.mkdir()
    csvp = tmp_path / "s.csv"
    csvp.write_text("Video title,Impressions CTR\nweak video,2.1%\n",
                    encoding="utf-8")
    rep = audit_dir(d, csv_path=csvp)
    assert any("CTR band breach" in f.title for f in rep.findings)
    csv2 = tmp_path / "n.csv"
    csv2.write_text("Video title,Views\nweak video,10\n", encoding="utf-8")
    rep2 = audit_dir(d, csv_path=csv2)
    assert any("no CTR column" in f.title for f in rep2.findings)


def test_audit_dossier_linkrot_tie_in(tmp_path):
    d = tmp_path / "x"
    d.mkdir()
    vids = [{"id": f"v{i}", "title": f"old secret {i}", "channel": "c",
             "views": 1000 * i, "likes": 5, "duration_s": 300,
             "transcript": "the file sat unopened nobody signed " * 10,
             "date": "2020-01-01"} for i in range(1, 4)]
    dp = tmp_path / "d.json"
    dp.write_text(json.dumps({"niche": "n", "videos": vids}), encoding="utf-8")
    rep = audit_dir(d, dossier_path=dp, today=TODAY)
    assert any("link-rot" in f.title for f in rep.findings)


def test_cli_audit_json_and_render(capsys, tmp_path):
    d = tmp_path / "y"
    d.mkdir()
    rc = main(["audit", str(d), "--json"])
    out = capsys.readouterr().out
    assert rc == 0
    data = json.loads(out)
    assert "score" in data and "findings" in data
    rc2 = main(["audit", str(d)])
    text = capsys.readouterr().out
    assert rc2 == 0 and "AUDIT" in text and "P3" in text


def test_cli_audit_missing_dir_fails_closed(capsys, tmp_path):
    rc = main(["audit", str(tmp_path / "ghost")])
    out = capsys.readouterr().out
    assert rc == 2 and "FAIL" in out


def test_audit_score_penalty_math(tmp_path):
    from monarch.video.audit import AuditReport, Finding
    rep = AuditReport(subject="t")
    rep.findings = [Finding("P1", "a", "e", "f", "i"),
                    Finding("P3", "b", "e", "f", "i")]
    assert rep.score == 100 - 12 - 2
    rep.findings.append(Finding("P0", "c", "e", "f", "i"))
    rep.findings.append(Finding("P0", "d", "e", "f", "i"))
    rep.findings.append(Finding("P0", "e", "e", "f", "i"))
    rep.findings.append(Finding("P0", "f", "e", "f", "i"))
    assert rep.score == 0          # never negative


def test_audit_render_priority_order(tmp_path):
    from monarch.video.audit import AuditReport, Finding
    rep = AuditReport(subject="t")
    rep.findings = [Finding("P3", "z-note", "e", "f", "i"),
                    Finding("P1", "a-major", "e", "f", "i")]
    text = rep.render()
    assert text.index("a-major") < text.index("z-note")


def test_hook_score_never_out_of_range():
    from monarch.video.audit import hook_score as hs
    for line in ("", "x" * 200, "1 2 3 why nobody you secret hidden", "!!!"):
        assert 1 <= hs(line) <= 10


def test_hook_band_on_real_board(video_dir):
    board = json.loads((video_dir / "board.json").read_text(encoding="utf-8"))
    hook_line = str(board["scenes"][0].get("vo_line", ""))
    hs = hook_score(hook_line)
    assert 1 <= hs <= 10                     # the eye scores the real cold open


def test_rewrite_rules_are_idempotent():
    from monarch.video.humanize import REWRITE_RULES
    text = "It's not just a vault — it's a promise, and the silence held."
    once = text
    for pat, repl in REWRITE_RULES:
        once = re.sub(pat, repl, once)
    twice = once
    for pat, repl in REWRITE_RULES:
        twice = re.sub(pat, repl, twice)
    assert once == twice                     # no infinite rewrite churn


def test_audit_json_schema_stable(video_dir):
    rep = audit_dir(video_dir)
    d = rep.as_dict()
    assert set(d) == {"subject", "score", "findings", "scores"}
    for f in d["findings"]:
        assert set(f) == {"severity", "title", "evidence", "fix", "impact"}
