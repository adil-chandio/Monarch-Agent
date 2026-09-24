"""The Eye — `monarch audit`: priority-ordered weakness -> fix report (W3).

Everything the market sells as "Channel Audit Mode" (N=3 validation),
executable on Monarch's own artifacts with ZERO judgment calls:

* anchored deterministic bands (no vibes, no LLM-judge drift):
    hook 1-10  — number +3, open-loop +2, second-person +1, cold-open
                 shape +2 (proven pattern), base 2; band <5 = P2
    pacing     — Zack band 65-95 words/30s per scene
    CTR        — <3% rework / 4-6% healthy / 7-10% strong (Studio norms)
    AI-signs   — humanize gate on the spoken lines
    voice QC   — manifest voice checks (no_dead_air, clipped, ...)
    mix        — master_mix present when voice present
    freshness  — optional dossier: link-rot rows (W2 truth layer)
* severity P0(critical) / P1(major) / P2(should fix) / P3(note)
* every finding carries evidence + the exact fix command + expected impact
* gaps the operator parked (MP4 render) are REPORTED, never built
  (standing order #1 — the audit speaks, hands stay off)

Fail-closed: missing/empty subject dir -> ValueError. Nothing found to
audit -> the report says so; silence would be a lie.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from monarch.core.words import count_words
from monarch.video.humanize import score_text

SEV_ORDER = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
SEV_COST = {"P0": 25, "P1": 12, "P2": 6, "P3": 2}

ZACK_MIN, ZACK_MAX = 65.0, 95.0

_OPEN_MARKERS = ("nobody", "no one", "secret", "hidden", "why", "buried",
                 "vanished", "never")
_SECOND = ("you", "your", "aap", "tum")
_COLD_SHAPE = re.compile(r"\bnot just [^—,;.]{3,40} — ", re.I)
_NUMBER = re.compile(r"\d")


# ---------------------------------------------------------------------------
# anchored scorers (deterministic — the judge is a formula, it cannot flatter)
# ---------------------------------------------------------------------------


def hook_score(line: str) -> int:
    """1..10 anchored band: number/open-loop/second-person/cold-shape."""
    low = (line or "").lower()
    s = 2
    if _NUMBER.search(low):
        s += 3
    s += sum(2 for m in _OPEN_MARKERS if m in low) or 0
    if any(w in low for w in _SECOND):
        s += 1
    if _COLD_SHAPE.search(line or ""):
        s += 2
    return max(1, min(10, s))


def ctr_band(ctr: float) -> tuple[str, str] | None:
    """Studio-norm CTR bands -> (severity, verdict). None = nothing to say."""
    if ctr < 3.0:
        return "P1", f"CTR {ctr:.1f}% < 3% — packaging rework (title/thumbnail)"
    if ctr < 4.0:
        return "P3", f"CTR {ctr:.1f}% healthy-low (4-6% is the healthy band)"
    if ctr <= 10.0:
        return None, f"CTR {ctr:.1f}% healthy-strong"
    return None, f"CTR {ctr:.1f}% exceptional"


# ---------------------------------------------------------------------------
# the audit
# ---------------------------------------------------------------------------


@dataclass
class Finding:
    severity: str
    title: str
    evidence: str
    fix: str
    impact: str

    def line(self) -> str:
        return (f"[{self.severity}] {self.title}\n"
                f"     evidence: {self.evidence}\n"
                f"     fix: {self.fix}\n"
                f"     impact: {self.impact}")


@dataclass
class AuditReport:
    subject: str
    findings: list[Finding] = field(default_factory=list)
    scores: dict = field(default_factory=dict)

    @property
    def score(self) -> int:
        return max(0, 100 - sum(SEV_COST[f.severity] for f in self.findings))

    def sorted_findings(self) -> list[Finding]:
        return sorted(self.findings,
                      key=lambda f: (SEV_ORDER[f.severity], f.title))

    def summary(self) -> str:
        head = (f"AUDIT {Path(self.subject).name} — score {self.score}/100, "
                f"{len(self.findings)} finding(s)")
        if not self.findings:
            return head + " | nothing to report — laws held"
        return head

    def render(self) -> str:
        out = [self.summary()]
        for i, f in enumerate(self.sorted_findings(), 1):
            out.append(f"  {i}. {f.line()}")
        if any(f.title.startswith("parked gap") for f in self.findings):
            out.append("  (parked gaps are REPORTED only — standing order #1)")
        return "\n".join(out) + "\n"

    def as_dict(self) -> dict:
        return {"subject": self.subject, "score": self.score,
                "findings": [f.__dict__ for f in self.sorted_findings()],
                "scores": self.scores}


def _load_json(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def audit_dir(subject: str | Path, *, csv_path: str | Path | None = None,
              dossier_path: str | Path | None = None,
              today=None) -> AuditReport:
    """Audit one make-video output dir (+ optional Studio CSV / dossier)."""
    d = Path(subject)
    if not d.is_dir():
        raise ValueError(f"subject dir not found: {d}")
    rep = AuditReport(subject=str(d))
    board: list = []          # G5/G14: defined even when board.json absent

    manifest_p = d / "manifest.json"
    manifest: dict = {}
    if manifest_p.is_file():
        try:
            manifest = _load_json(manifest_p)
        except (json.JSONDecodeError, OSError) as e:
            rep.findings.append(Finding(
                "P1", "manifest unreadable", f"{manifest_p}: {e}",
                "re-run make-video (deterministic seed reproduces the dir)",
                "everything downstream guesses without the manifest"))
    else:
        rep.findings.append(Finding(
            "P3", "no manifest.json", f"{d} carries no manifest",
            "monarch make-video --topic ... --out <dir>",
            "audit depth limited to files present"))

    # ---- voice QC (fail-closed honesty from the TABAAHI laws)
    voice = manifest.get("voice") or {}
    qc_rows = voice.get("qc") or []
    fails = [c for c in qc_rows if not c.get("pass", True)]
    if fails:
        for c in fails:
            rep.findings.append(Finding(
                "P1", f"voice QC failed: {c.get('check')}", c.get("detail", ""),
                "rebuild voice (--voice-backend) after fixing timing/chunks",
                "dead air / clipped words leak retention"))
    if voice and not fails:
        rep.scores["voice_qc"] = "all PASS"

    # ---- mix
    if voice and not manifest.get("mix"):
        rep.findings.append(Finding(
            "P3", "voice without a master mix", "manifest has voice but no mix",
            "re-run with --with-mix (music duck + SFX + room tone + limiter)",
            "flat audio reads amateur within 5 seconds"))

    # ---- mix: law-aware ceiling + ducking (PRODUCTION_LAW_V2 L8/G7;
    #      dBFS proxy from the mix report — LUFS needs loudnorm/ffprobe)
    mix_info = manifest.get("mix") or {}
    report = str(mix_info.get("report", "")) if mix_info else ""
    if report:
        m = re.search(r"master (-?[\d.]+)/(-?[\d.]+) dBFS", report)
        if m and float(m.group(2)) >= -1.0:
            rep.findings.append(Finding(
                "P2", "master peak over ceiling (L8/G12)",
                f"mix report says master peak {m.group(2)} dBFS (ceiling -1.0); "
                "note: dBFS proxy — final -14 LUFS check needs loudnorm/ffprobe",
                "re-run mix with the limiter engaged (G7 layer 7)",
                "platform loudness normalization pumps or clips the master"))
        if "VO GATE FAIL" in report:
            rep.findings.append(Finding(
                "P1", "VO lost in master (G7 gate)",
                report,
                "re-mix in layers (max 10 inputs per command) and re-verify "
                "first/mid/last speech windows against raw VO levels",
                "the operator heard SFX where the voice should be"))
        duck = re.search(r"duck events (\d+)", report)
        if duck and int(duck.group(1)) == 0:
            rep.findings.append(Finding(
                "P3", "no sidechain duck events (L8)",
                "mix report: duck events 0 — music never ducked under VO",
                "re-run mix (music bed must breathe under voice, ~1.2x VO)",
                "voice fights the bed; intelligibility drops on phones"))
        rep.scores["mix_report"] = report[:80]

    # ---- pack checklist (PRODUCTION_LAW_V2 Part 4 / L6+L15) — report-only
    mp4s = list(d.glob("*.mp4"))
    pack_have, pack_missing = [], []
    if list(d.glob("*.srt")):
        pack_have.append("srt")
    else:
        pack_missing.append("captions.srt (L6)")
    if list(d.glob("*thumb*")):
        pack_have.append("thumbnails")
    else:
        pack_missing.append("2 thumbnails + 120px postage test (L11)")
    if any(p.name.startswith(("listing", "description", "metadata"))
           for p in d.iterdir() if p.is_file()):
        pack_have.append("listing")
    else:
        pack_missing.append("listing: title+description+tags+timestamps")
    if mp4s:
        pack_have.append(f"{len(mp4s)} mp4")
    else:
        pack_missing.append("final video (parked render — operator order)")
    rep.scores["pack_items"] = len(pack_have)
    rep.findings.append(Finding(
        "P3", "pack checklist (Part 4) status",
        f"have: {', '.join(pack_have) or 'nothing yet'}; "
        f"missing: {', '.join(pack_missing) or 'nothing'}",
        "M6/P3 pack stage: srt + thumbs + listing + versioned final "
        "(preview player points at LATEST final, G16)",
        "upload day belongs to the operator (HAAN gate)"))
    unversioned = [p.name for p in mp4s
                   if not re.search(r"(v\d+|final)", p.name, re.I)]
    if unversioned:
        rep.findings.append(Finding(
            "P3", "final not versioned (G16 cache law)",
            f"{', '.join(unversioned[:3])} — browser cache serves stale files",
            "rename with a version token (…_v2_final.mp4) and re-point "
            "the preview at LATEST",
            "operator reviews an OLD cut and re-litigates fixed problems"))

    # ---- parked gap: REPORTED, never acted on (standing order #1)
    rep.findings.append(Finding(
        "P3", "parked gap: MP4 render stage (in-repo)", 
        "previz emits frames+wav+timeline; MP4 assembly stays outside the repo "
        "by operator order (closed-in-production via the journal recipe)",
        "operator-ordered render stage OR the rebuild-script path on your PC",
        "no impact on previz/QC; upload still operator-gated (HAAN)"))

    # ---- board: pacing + anchored hook + AI-signs
    board_p = d / "board.json"
    if board_p.is_file():
        try:
            data = _load_json(board_p)
            # G5: shape-check before subscripting - boards have shipped as
            # lists AND as {title, maths, scenes} dicts. Both readable.
            board = data.get("scenes", []) if isinstance(data, dict) else data
        except (json.JSONDecodeError, OSError) as e:
            board = []
            rep.findings.append(Finding("P2", "board.json unreadable", str(e),
                                        "regenerate the storyboard", "no pacing/hook audit"))
        slow: list[str] = []
        total_words = 0
        for s in board:
            w = count_words(str(s.get("vo_line", "")))
            total_words += w
            dur = float(s.get("t_end", 0)) - float(s.get("t_start", 0))
            if dur > 0.5:
                wp30 = w / dur * 30.0
                if not (ZACK_MIN <= wp30 <= ZACK_MAX):
                    slow.append(f"s{s.get('id')}:{wp30:.0f}w/30s")
        if slow:
            rep.findings.append(Finding(
                "P2", "pacing outside the Zack band",
                f"{len(slow)} scene(s) off 65-95 words/30s: {', '.join(slow[:6])}",
                "rebalance words per scene (fit_words) or scene durations",
                "off-band pacing is the #1 APV killer (deep-forensic evidence)"))
        rep.scores["pacing_scenes_off_band"] = len(slow)

        if board:
            hook_line = str(board[0].get("vo_line", ""))
            hs = hook_score(hook_line)
            rep.scores["hook_score"] = hs
            rep.scores["hook_line"] = hook_line[:70]
            if hs < 5:
                rep.findings.append(Finding(
                    "P2", "weak cold open (anchored hook < 5)",
                    f"score {hs}/10 on: {hook_line[:60]!r}",
                    "add a number, an open loop, or direct address (you) — "
                    "N1 thumb-stop laws",
                    "first 3 seconds decide the scroll"))
            if total_words:
                signs, hits, notes = score_text(
                    " ".join(str(s.get("vo_line", "")) for s in board))
                rep.scores["ai_signs_per_100w"] = signs
                if signs > 1.5:
                    rep.findings.append(Finding(
                        "P2", "script reads mechanical (AI-signs over gate)",
                        f"{signs:.2f} signs/100w; top: "
                        + "; ".join(h[0] for h in hits[:3]),
                        "monarch humanize --file <script> then re-fit words",
                        "AI-tone = 'robot bol raha hai' complaint, instant skip"))
    else:
        rep.findings.append(Finding(
            "P3", "no board.json", f"{d} carries no board",
            "make-video emits board.json (scene rows drive the audit)",
            "pacing/hook/AI-signs unaudited"))

    # ---- G14/L13: duration sources must agree (+-0.5s), or the QC is
    #      repeating the 63.6s-video-on-a-60s-board lie
    sources: dict[str, float] = {}
    if manifest.get("total_s"):
        sources["manifest.total_s"] = float(manifest["total_s"])
    tl_p = d / "timeline.json"
    if tl_p.is_file():
        try:
            tval = _load_json(tl_p).get("total_s")
            if tval:
                sources["timeline.json"] = float(tval)
        except (json.JSONDecodeError, OSError):
            pass
    if board:
        sources["board.sum"] = round(sum(
            float(s.get("t_end", 0)) - float(s.get("t_start", 0))
            for s in board), 3)
    if len(sources) >= 2:
        vals = list(sources.values())
        spread = max(vals) - min(vals)
        rep.scores["duration_spread_s"] = round(spread, 3)
        if spread > 0.5:
            rep.findings.append(Finding(
                "P1", "duration sources disagree (G14)",
                f"{sources} - spread {spread:.2f}s > 0.5s",
                "regenerate from the board (deterministic seed) and run "
                "ffprobe on the real file before trusting any QC",
                "one trusted source is how a 63.6s video passed a 60s board"))

    # ---- optional Studio CSV: CTR bands + APV spread
    if csv_path is not None:
        from monarch.pipelines.performance import _cell  # reuse normalization? no — raw scan
        text = Path(csv_path).read_text(encoding="utf-8", errors="replace")
        rows = [r for r in text.splitlines() if r.strip()]
        header = [h.strip().lower() for h in rows[0].split("," if "," in rows[0] else "\t")]
        ctr_col = next((h for h in header
                        if h in ("ctr", "impressions ctr", "click-through rate")), None)
        if ctr_col:
            i = header.index(ctr_col)
            for line_no, row in enumerate(rows[1:], 2):
                cells = row.split("," if "," in row else "\t")
                raw = cells[i].strip().strip('"').rstrip("%") if i < len(cells) else ""
                try:
                    ctr = float(raw.replace(",", ""))
                except ValueError:
                    continue
                sev, verdict = ctr_band(ctr)
                if sev:
                    rep.findings.append(Finding(
                        sev, f"CTR band breach (row {line_no})",
                        verdict + f" — evidence: {cells[0][:40] if cells else row[:40]}",
                        "rework title/thumbnail combo, then A/B the impression",
                        "CTR < 3% burns impressions the algorithm already gave"))
        else:
            rep.findings.append(Finding(
                "P3", "CSV had no CTR column",
                f"header was {header[:8]}",
                "export Studio Advanced Mode with Impressions CTR column",
                "CTR is the packaging gate — without it the audit is half-blind"))

    # ---- optional dossier: freshness / link-rot (W2 tie-in)
    if dossier_path is not None:
        from monarch.pipelines.deep_forensic import load_dossier
        niche, vids = load_dossier(dossier_path)
        from monarch.pipelines.deep_forensic import HALF_LIFE_DAYS, analyze_dossier
        frep = analyze_dossier(niche, vids, today=today)
        rot = frep.freshness.get("linkrot_risk_ids") or []
        if rot:
            rep.findings.append(Finding(
                "P2", "stale evidence in dossier (link-rot risk)",
                f"{len(rot)} row(s) older than 2x half-life: {', '.join(rot[:5])}",
                "re-hunt the niche for fresh outliers "
                "(monarch hunt / deep-forensic refresh)",
                "stale DNA steers scripts toward a market that moved on"))
        rep.scores["dossier_median_age_days"] = frep.freshness.get("median_age_days")

    return rep
