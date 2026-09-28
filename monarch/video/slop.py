"""W-B3 — the SLOP AUDIT (CHAOS §2): channel-level survival check.

YouTube's inauthentic-content enforcement works at CHANNEL level (the
assembly-line pattern flags the channel, not just videos). This audit
reads the last N render dirs and measures the tripwires BEFORE
YouTube's reviewers ever see them:

  1. template-distance  - consecutive boards' VO text similarity with
     the topic tokens STRIPPED (the noun-swap detector; the reported
     reviewer rule-of-thumb is 5+ same-template videos with <20%
     script variation)
  2. genre variety      - >=4 consecutive same-genre renders = variety
     advisory (variation in TOPIC, consistency in GRAMMAR is the law)
  3. cadence            - >=4 renders in 24h = cadence-mismatch
     advisory (claimed depth vs production method)
  4. persona presence   - every dir must carry the stickman-engine
     artifacts (frames/ + board.json) - the face-equivalent strategy
  5. disclosure shield  - the AI-disclosure line must ship in the kit
     (the 3-strike ladder starts with a warning; we pre-empt it)
  6. commentary ratio   - VO coverage of the runtime (the <30%
     commentary tripwire's conservative proxy: we demand >=50%)

Deterministic, stdlib-only, honest: a channel with <2 readable dirs
gets an ADVISORY, not a fake verdict.
"""

from __future__ import annotations

import re
import time
import wave
from pathlib import Path

DISCLOSURE_MARKER = "ai-generated"
DISCLOSURE_LINE = ("Disclosure: This video was produced with AI-generated "
                   "visuals and an AI voiceover (Monarch pipeline).")


def _dirs(channel: str | Path, last_n: int) -> list[Path]:
    root = Path(channel)
    if not root.is_dir():
        raise ValueError(f"channel dir not found: {root}")
    readable = []
    for d in root.iterdir():
        try:
            if d.is_dir() and (d / "board.json").is_file():
                readable.append(d)
        except OSError:
            continue                     # unreadable entries are skipped,
            # not fatal - a channel dir can hold system junk
    readable.sort(key=lambda p: p.stat().st_mtime)
    return readable[-last_n:]


def _board_vo(d: Path) -> str:
    try:
        b = json_load(d / "board.json")
    except (OSError, ValueError):
        return ""
    rows = b if isinstance(b, list) else (b.get("scenes") or b.get("rows") or [])
    return " ".join(str(r.get("vo_line") or "") for r in rows
                    if isinstance(r, dict))


def _strip_topic(text: str, title: str) -> str:
    """Remove the topic tokens - the noun-swap detector depends on it
    (swapping the animal's name must NOT count as script variation)."""
    tokens = {t for t in re.findall(r"[a-z0-9]+", title.lower()) if len(t) > 2}
    keep = [w for w in re.findall(r"[a-z0-9']+", text.lower())
            if w not in tokens]
    return " ".join(keep)


def _shingles(text: str, k: int = 3) -> set[str]:
    ws = text.split()
    if len(ws) < k:
        return {" ".join(ws)} if ws else set()
    return {" ".join(ws[i:i + k]) for i in range(len(ws) - k + 1)}


def _similarity(a: str, b: str) -> float:
    sa, sb = _shingles(a), _shingles(b)
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)          # Jaccard


def _vo_coverage_s(d: Path) -> float | None:
    for cand in (d / "vo" / "vo_track.wav", d / "master_mix.wav"):
        if cand.is_file():
            try:
                with wave.open(str(cand), "rb") as w:
                    return w.getnframes() / float(w.getframerate())
            except (wave.Error, OSError):
                return None
    return None


def _runtime_s(d: Path) -> float | None:
    try:
        t = json_load(d / "timeline.json")
        v = t.get("total_s")
        return float(v) if v else None
    except (OSError, ValueError):
        return None


def _has_disclosure(d: Path) -> bool:
    for pat in ("kit/package.json", "kit/description.txt",
                "listing.md", "description.txt", "package.json"):
        p = d / pat
        if p.is_file():
            try:
                if DISCLOSURE_MARKER in p.read_text(encoding="utf-8").lower():
                    return True
            except OSError:
                continue
    return False


def slop_audit(channel: str | Path, *, last_n: int = 6,
               now: float | None = None) -> dict:
    now = time.time() if now is None else now
    dirs = _dirs(channel, last_n)
    if len(dirs) < 2:
        return {"ok": True, "advisory_only": True,
                "note": f"{len(dirs)} render dir(s) readable - channel-level "
                        "verdict needs >=2; nothing to flag yet",
                "findings": [], "dirs": [d.name for d in dirs]}
    findings: list[dict] = []

    def F(pri: str, msg: str) -> None:
        findings.append({"priority": pri, "finding": msg})

    # 1. template-distance (topic-stripped, consecutive pairs)
    texts = [(_strip_topic(_board_vo(d),
                           _title_of(d)), d.name) for d in dirs]
    template_pairs = 0
    pairs_checked = 0
    for (ta, na), (tb, nb) in zip(texts, texts[1:]):
        if not ta or not tb:
            continue
        pairs_checked += 1
        sim = _similarity(ta, tb)
        if sim >= 0.75:
            template_pairs += 1
            if template_pairs >= 2:
                F("P1", f"assembly-line signature: {template_pairs} "
                        f"consecutive pairs >=0.75 topic-stripped VO "
                        f"similarity ({na} vs {nb} = {sim:.2f}) - the "
                        "5-video/<20%-variation bulk-demonetization class")
    if pairs_checked and template_pairs == 0:
        findings.append({"priority": "OK",
                         "finding": f"script variation healthy across "
                                    f"{pairs_checked} consecutive pair(s)"})

    # 2. genre variety
    genres = [_genre_of(d) for d in dirs]
    run = best_run = 1
    for a, b in zip(genres, genres[1:]):
        run = run + 1 if a == b else 1
        best_run = max(best_run, run)
    if best_run >= 4:
        F("P2", f"{best_run} consecutive renders in the same genre "
                f"({genres[-1]}) - vary topics/angles (grammar stays "
                "consistent; topics must not)")

    # 3. cadence
    mtimes = [d.stat().st_mtime for d in dirs]
    day = [(t, n) for t, n in zip(mtimes, [d.name for d in dirs])
           if now - t <= 86400]
    if len(day) >= 4:
        F("P2", f"{len(day)} renders in the last 24h - if the content "
                "claims depth/analysis this is the cadence-mismatch flag")

    # 4. persona presence (the stickman engine ships frames + board)
    faceless = [d.name for d in dirs if not (d / "frames").is_dir()]
    if faceless:
        F("P1", f"no frames/ in {', '.join(faceless[:3])} - the "
                "stickman face-equivalent is not shipping (face-bias "
                "counter-strategy + persona requirement)")

    # 5. disclosure shield
    undisclosed = [d.name for d in dirs if not _has_disclosure(d)]
    if len(undisclosed) == len(dirs):
        F("P1", f"no AI-disclosure line in any of the last {len(dirs)} "
                "renders - run `monarch package` per render (the "
                "3-strike ladder starts at a warning)")
    elif undisclosed:
        F("P2", f"disclosure missing in: {', '.join(undisclosed[:3])}")

    # 6. commentary ratio (conservative >=50% vs the <30% tripwire)
    thin = []
    for d in dirs:
        vo_s = _vo_coverage_s(d)
        rt_s = _runtime_s(d)
        if vo_s and rt_s and rt_s > 1:
            ratio = vo_s / rt_s
            if ratio < 0.5:
                thin.append(f"{d.name} {ratio:.0%}")
    if thin:
        F("P2", f"VO coverage below 50% of runtime in: {', '.join(thin[:3])}"
                " - the <30% commentary tripwire lives nearby")

    p1 = [f for f in findings if f["priority"] == "P1"]
    score = 100 - 25 * len(p1) - 10 * len([f for f in findings
                                           if f["priority"] == "P2"])
    return {"ok": not p1, "advisory_only": False, "score": max(0, score),
            "findings": findings, "dirs": [d.name for d in dirs]}


def _title_of(d: Path) -> str:
    try:
        return str(json_load(d / "timeline.json").get("title") or d.name)
    except (OSError, ValueError):
        return d.name


def _genre_of(d: Path) -> str:
    try:
        t = json_load(d / "timeline.json")
        return str(t.get("genre") or t.get("note") or "?").lower()
    except (OSError, ValueError):
        return "?"


def json_load(p: Path):
    import json
    return json.loads(p.read_text(encoding="utf-8"))
