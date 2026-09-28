"""W-B4 — ENGAGED-CLASS VITALS + the repurpose queue (final wave).

The scoreboard discipline (ABYSS A): since Aug 24 2026 the public view
counts from the first frame, but earnings/YPP/CTR/AVD/retention all run
on ENGAGED views. This module never fetches analytics (egress-honest):
it EVALUATES the numbers the operator reads out of YouTube Studio and
emits the post-launch sheet with band verdicts from the 2026 research:

  CTR            4-8% normal · 10%+ excellent · <2% critical
  swipe-through  >50% strong · <30% dead · ~70% = velocity gate
  AVP            hold 50%+ at midpoint · 70%+ = priority distribution
  inflation      public/engaged ~1.67x typical (Agentio 75k study);
                 much higher = bounce-heavy open (first seconds leak)
  returning %    the satisfaction proxy (2026's #1 signal) - heuristic
                 bands, marked advisory

Plus the repurposing queue (ARSENAL F42): one long render -> the 5-15
Shorts skeleton, moments picked from the board (hook-remix, payoff-tease
cut BEFORE the reveal - Zeigarnik, WTF-detail beats, loop-cut), each in
the 22-45 s band. Anti-slop law baked in: vary the TOPIC, keep the
GRAMMAR.

Deterministic, stdlib-only, honest: missing numbers become [fill]
placeholders - never a fake verdict.
"""

from __future__ import annotations

CUTOVER = "2026-08-24"
TYPICAL_INFLATION = 1.67


# ---------------------------------------------------------------------------
# vitals evaluation
# ---------------------------------------------------------------------------


def evaluate_vitals(*, impressions: int | None = None,
                    clicks: int | None = None,
                    public_views: int | None = None,
                    engaged_views: int | None = None,
                    viewed: int | None = None,
                    swiped: int | None = None,
                    avp_pct: float | None = None,
                    returning_pct: float | None = None) -> dict:
    f: list[dict] = []

    def F(pri: str, msg: str) -> None:
        f.append({"priority": pri, "finding": msg})

    ctr = swipe = inflation = None
    # CTR (long-form packaging axis; judged on the channel's own average)
    if impressions and clicks is not None:
        ctr = 100.0 * clicks / impressions
        if ctr < 2.0:
            F("P1", f"CTR {ctr:.1f}% - critical band (<2%): rewrite the "
                    "title/thumbnail promise (RPE: the payoff must exceed it)")
        elif ctr < 4.0:
            F("P2", f"CTR {ctr:.1f}% - below the 4-8% normal band")
        elif ctr >= 10.0:
            F("OK", f"CTR {ctr:.1f}% - excellent band (10%+)")
        else:
            F("OK", f"CTR {ctr:.1f}% - normal band (4-8%)")

    # the split: public vs engaged (the Aug-24 law)
    if public_views and engaged_views:
        inflation = public_views / engaged_views
        if inflation > 2.2:
            F("P2", f"public/engaged = {inflation:.2f}x (typical ~"
                    f"{TYPICAL_INFLATION}x) - bounce-heavy open: the first "
                    "seconds leak; tighten the 0.5s window")
        else:
            F("OK", f"public/engaged = {inflation:.2f}x - within the "
                    f"~{TYPICAL_INFLATION}x typical spread")
    # swipe gate (Shorts)
    if viewed is not None and swiped is not None and (viewed + swiped) > 0:
        swipe = 100.0 * viewed / (viewed + swiped)
        if swipe < 30.0:
            F("P1", f"swipe-through {swipe:.0f}% - dead (<30% stops "
                    "distribution): packaging problem, fix the first frame")
        elif swipe < 50.0:
            F("P2", f"swipe-through {swipe:.0f}% - weak (50%+ = strong); "
                    f"~70% unlocks the velocity gate")
        else:
            F("OK", f"swipe-through {swipe:.0f}% - strong (velocity gate "
                    f"at ~70%)")
    # AVP (structure axis)
    if avp_pct is not None:
        if avp_pct < 50.0:
            F("P2", f"AVP {avp_pct:.0f}% - below the midpoint-hold law "
                    "(structure problem: tighten the middle, kill skippable "
                    "parts")
        elif avp_pct >= 70.0:
            F("OK", f"AVP {avp_pct:.0f}% - priority-distribution band (70%+)")
        else:
            F("OK", f"AVP {avp_pct:.0f}% - holds the midpoint law (50%+)")
    # returning viewers (the satisfaction proxy)
    if returning_pct is not None:
        if returning_pct < 10.0:
            F("P2", f"returning viewers {returning_pct:.0f}% - low; "
                    "satisfaction (#1 signal) proxy is thin: series/universe "
                    "formats build it")
        else:
            F("OK", f"returning viewers {returning_pct:.0f}% - satisfaction "
                    "proxy alive (advisory bands)")

    p1 = sum(1 for x in f if x["priority"] == "P1")
    p2 = sum(1 for x in f if x["priority"] == "P2")
    has_any = any(v is not None for v in (impressions, public_views,
                                          viewed, avp_pct, returning_pct))
    return {"ok": (not p1) if has_any else None,
            "advisory_only": not has_any,
            "note": ("no vitals entered - fill from Studio (engaged-class "
                     "only) and re-run" if not has_any else
                     "compare engaged-to-engaged only; YoY breaks at "
                     f"{CUTOVER}"),
            "ratios": {"ctr": None if ctr is None else round(ctr, 2),
                       "swipe_through": None if swipe is None else round(swipe, 1),
                       "inflation": None if inflation is None else round(inflation, 2)},
            "findings": f, "score": max(0, 100 - 25 * p1 - 10 * p2)}


def sheet_md(v: dict, *, title: str = "") -> str:
    """The post-launch sheet: verdicts for what was entered, honest
    [fill] slots for what was not."""
    r = v["ratios"]

    def _cell(label, key, unit=""):
        val = r.get(key)
        return f"| {label} | {val}{unit} |" if val is not None else \
               f"| {label} | [fill from Studio] |"

    lines = [
        "# 📊 POST-LAUNCH VITALS SHEET" + (f" — {title}" if title else ""),
        "",
        f"> Scoreboard law: public views = REACH, engaged views = ATTENTION.",
        f"> Earnings/YPP/CTR/AVD/retention run on ENGAGED only. YoY "
        f"comparisons break at {CUTOVER} - compare engaged-to-engaged.",
        f"> Sponsor decks quote ENGAGED views (public overstates ~"
        f"{TYPICAL_INFLATION}x).",
        "",
        "## numbers",
        "| metric | value |",
        "|---|---|",
        _cell("CTR (clicks/impressions)", "ctr", "%"),
        _cell("swipe-through (viewed vs swiped)", "swipe_through", "%"),
        _cell("public/engaged inflation", "inflation", "x"),
        "| AVP % | [fill] |",
        "| returning viewers % | [fill] |",
        "",
        "## verdicts",
    ]
    if v["findings"]:
        lines += [f"- **[{x['priority']}]** {x['finding']}" for x in v["findings"]]
    else:
        lines.append("- (no numbers evaluated yet - fill and re-run)")
    lines += ["", f"**score:** {v['score']}/100" if not v["advisory_only"]
              else f"**advisory:** {v['note']}"]
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# repurpose queue (1 long -> 5-15 Shorts skeletons)
# ---------------------------------------------------------------------------


def _role(r: dict) -> str:
    return str(r.get("retention_role") or r.get("role") or "body").lower()


def repurpose_queue(board, *, title: str = "", n: int = 6,
                    topics: list[str] | None = None) -> list[dict]:
    rows = board if isinstance(board, list) else \
        (board or {}).get("scenes") or []
    rows = [r for r in rows if isinstance(r, dict)]
    if not rows:
        raise ValueError("no board rows - the queue refuses to guess (L15)")
    if n < 1 or n > 15:
        raise ValueError("n must be 1..15 (the 5-15 repurposing law)")

    q: list[dict] = []

    def add(concept: str, r: dict, why: str, cut_note: str = "") -> None:
        if len(q) >= n:
            return
        q.append({
            "concept": concept,
            "source_beat": int(r.get("id", 0)),
            "vo_seed": str(r.get("vo_line") or "").strip()[:120],
            "band": "22-45s (the sweet band)",
            "why": why, "cut_note": cut_note,
            "title_hint": (title[:27].strip() or "this story") + " #shorts",
            "anti_slop": "same hook grammar, DIFFERENT topic/angle",
        })

    # 1. the thumb-stop opening, re-cut as its own short
    add("hook-remix", rows[0],
        "the N1 thumb-stop beat is a proven first frame - reuse it as the "
        "Short's first frame (first-frame thumbnail law)")

    # 2. the peak, cut BEFORE the reveal (Zeigarnik / condensed-incomplete)
    peaks = [r for r in rows if _role(r).startswith("payoff")]
    if peaks:
        add("payoff-tease", peaks[-1],
            "the PEAK beat cut just BEFORE the reveal - the gap stays open, "
            "the long video closes it (condensed-incomplete law)",
            "end on the open loop, never on the answer")

    # 3-4. WTF-detail body beats (drivers/markers first)
    marked = [r for r in rows if any(d in str(r.get("neuro_driver", "")).upper()
                                     for d in ("VALUE-DEBT", "CURIOSITY",
                                               "OPEN-LOOP"))]
    for r in marked:
        add("wtf-detail", r,
            "a debt-marked beat (curiosity driver) stands alone as a "
            "comment-bait short")

    # 5. the loop-cut: last beat + first beat stitched
    if len(rows) > 2:
        add("loop-cut", rows[-1],
            "last beat + first beat stitched = the seamless-loop practice "
            "short (earned rewatch, end frame == start frame)")

    # 6. the ranking teaser (when the operator passes ranked topics)
    if topics and len(topics) >= 4:
        from monarch.video.shorts import long_to_short
        plan = long_to_short(topics)
        if len(q) < n:
            q.append({
                "concept": "ranking-teaser",
                "source_beat": 0,
                "vo_seed": f"{len(plan['show'])} ranked, "
                           f"{plan['censored'][0]} censored",
                "band": "22-45s (the sweet band)",
                "why": f"condensed-incomplete: show {plan['pct']['show']}%, "
                       f"skip {plan['pct']['skipped']}%, censor "
                       f"{plan['pct']['censored']}% (#1) - comment bait built in",
                "cut_note": "#1 item appears blurred/censored only",
                "title_hint": (title[:27].strip() or "ranking") + " #shorts",
                "anti_slop": "same grammar, new ranking",
            })

    # top-up with plain body beats if still short
    for r in rows:
        if len(q) >= n:
            break
        if all(item["source_beat"] != int(r.get("id", 0)) or
               item["concept"] != "wtf-detail" for item in q):
            add("beat-study", r, "a solid body beat re-framed as a "
                "standalone micro-story")

    return q[:n]


def queue_md(q: list[dict], *, title: str = "") -> str:
    lines = [f"# 🔁 REPURPOSE QUEUE — {title}" if title
             else "# 🔁 REPURPOSE QUEUE", "",
             "> One long video, many Shorts. Vary the TOPIC, keep the",
             "> GRAMMAR (anti-slop law). Every cut lands in the 22-45 s",
             "> sweet band. Upload stays behind the HAAN gate.", ""]
    for i, item in enumerate(q, 1):
        lines += [f"## {i}. {item['concept']} (beat {item['source_beat']})",
                  f"- seed VO: “{item['vo_seed']}”",
                  f"- why: {item['why']}",
                  (f"- cut: {item['cut_note']}" if item["cut_note"] else None),
                  f"- title hint: {item['title_hint']}",
                  f"- band: {item['band']} · {item['anti_slop']}", ""]
    return "\n".join(x for x in lines if x is not None)
