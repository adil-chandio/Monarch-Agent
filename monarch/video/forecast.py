"""W-B1 — the 9-link CHAIN CHECK + curve forecaster (ABYSS D / ARSENAL C3).

Pre-render gate: the plan is a chain of nine links; a video dies at its
weakest link, so the gate names the weak links BEFORE any pixels exist:

    promise -> click -> first_3s_gate -> engaged_open -> open_loops ->
    one_peak -> engineered_end -> loop -> satisfaction

Plus the retention-curve forecast: the three sicknesses (Hockey Stick,
Gradual Bleed, Camel Humps) classified from beat interest data, and the
But/Therefore beat-connector lint (ARSENAL C1). Pure stdlib, fully
deterministic (L-class law: same plan -> same verdict).
DONE criterion (protocol): a deliberately bad plan FAILS WITH THE LINK
NAMED.
"""

from __future__ import annotations

import re

LINK_NAMES = ("promise", "click", "first_3s_gate", "engaged_open",
              "open_loops", "one_peak", "engineered_end", "loop",
              "satisfaction")

#: beats whose role IS the peak (composer family naming)
_PEAK_ROLES = ("payoff",)
_END_BANS = ("thanks for watching", "in conclusion", "see you next",
             "subscribe if you", "that's all folks", "the end.")
#: open-loop cue words in VO text (fallback when no explicit connectors)
_LOOP_CUES = ("but", "why", "how", "?", "until", "what happened",
              "nobody", "wrong", "secret", "until one day")
#: neuro drivers the engine already emits as open-debt markers
_LOOP_DRIVERS = ("VALUE-DEBT", "OPEN-LOOP", "CURIOSITY")


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _rows(board) -> list[dict]:
    rows = board if isinstance(board, list) else (board or {}).get("scenes") \
        or (board or {}).get("rows") or []
    out = [r for r in rows if isinstance(r, dict)]
    if not out:
        raise ValueError("no board rows - forecast refuses to guess (L15)")
    return out


def _role(r: dict) -> str:
    return str(r.get("retention_role") or r.get("role") or "body").strip().lower()


def _text(r: dict) -> str:
    return str(r.get("vo_line") or "").strip()


def _driver(r: dict) -> str:
    return str(r.get("neuro_driver") or "").upper()


def _interest(r: dict, i: int, n: int) -> float:
    """Beat interest 0..1 from role + position (deterministic)."""
    role = _role(r)
    if role.startswith("hook"):
        return 0.9
    if role.startswith("payoff"):
        return 1.0 if "+cua" not in role else 0.9
    if "silence" in role:
        return 0.65
    if role == "cua" or "cua" == role:
        return 0.35
    # body beats escalate with position (the escalation law)
    return min(0.85, 0.5 + 0.05 * i)


# ---------------------------------------------------------------------------
# But/Therefore lint (P2 law, ARSENAL C1)
# ---------------------------------------------------------------------------


def but_therefore_lint(beats: list[dict]) -> list[str]:
    """Explicit connectors when present; else cue-based inference.
    Two consecutive dead joints (and-then / flat declaratives with no
    open-loop signal) = the Camel-Humps seed -> named findings."""
    findings: list[str] = []
    rows = _rows(beats)
    dead_run = 0
    for i in range(len(rows) - 1):
        conn = str(rows[i].get("connector") or "").strip().lower()
        if conn in ("but", "therefore"):
            dead_run = 0
            continue
        nxt = _text(rows[i + 1]).lower()
        cur = _text(rows[i]).lower()
        joined = f"{cur} {nxt}"
        cue = any(c in joined for c in _LOOP_CUES) \
            or _LOOP_DRIVER_HIT(rows[i]) or _LOOP_DRIVER_HIT(rows[i + 1])
        if conn == "and then" or (not conn and not cue):
            dead_run += 1
            if dead_run >= 2:
                findings.append(
                    f"beats {i}-{i + 1}: two consecutive AND-THEN joints "
                    "(no BUT/THEREFORE, no open-loop cue) - Camel-Humps seed")
        else:
            dead_run = 0
    return findings


def _LOOP_DRIVER_HIT(r: dict) -> bool:
    return any(d in _driver(r) for d in _LOOP_DRIVERS)


# ---------------------------------------------------------------------------
# curve forecast (ARSENAL C3)
# ---------------------------------------------------------------------------


def curve_forecast(beats: list[dict]) -> dict:
    rows = _rows(beats)
    ints = [_interest(r, i, len(rows)) for i, r in enumerate(rows)]
    roles = [_role(r) for r in rows]

    # Hockey Stick: the opening never earns attention
    if not roles[0].startswith("hook") or ints[0] < 0.5:
        return {"sickness": "hockey_stick",
                "why": f"first beat role={roles[0]!r} interest={ints[0]:.2f} "
                       "- the hook drop kills the video in seconds",
                "interest": ints}

    dips = sum(1 for i in range(1, len(ints) - 1)
               if ints[i] < ints[i - 1] and ints[i] < ints[i + 1])
    peaks_after = [i for i, r in enumerate(roles) if r.startswith("payoff")]
    has_peak = bool(peaks_after)

    # Gradual Bleed: monotonic decline after the hook, no peak
    tail = ints[1:]
    if not has_peak and all(a >= b for a, b in zip(tail, tail[1:])):
        return {"sickness": "gradual_bleed",
                "why": "interest only declines after the hook and no payoff "
                       "beat exists - the boring lecture curve",
                "interest": ints}

    # Camel Humps: >= 2 dips = skippable middle (inconsistent loops)
    if dips >= 2:
        return {"sickness": "camel_humps",
                "why": f"{dips} dips in the interest line - skippable parts, "
                       "viewers fast-forward (fix: But/Therefore between beats)",
                "interest": ints}

    if not has_peak:
        return {"sickness": "gradual_bleed",
                "why": "no payoff/peak beat scheduled - the remembered high "
                       "cannot exist (peak-end law)",
                "interest": ints}

    peak_i = peaks_after[0]
    if peak_i == 0 or peak_i < len(rows) * 0.5:
        return {"sickness": "peak_too_early",
                "why": f"peak at beat {peak_i + 1}/{len(rows)} - escalation "
                       "law says each segment must out-interest the last",
                "interest": ints}

    return {"sickness": "healthy",
            "why": f"hook -> escalating body -> peak at beat "
                   f"{peak_i + 1}/{len(rows)} - curve holds",
            "interest": ints}


# ---------------------------------------------------------------------------
# the 9-link chain check
# ---------------------------------------------------------------------------


def chain_check(board, *, title: str = "", duration_s: float | None = None,
                shorts: bool = False, has_end_screen: bool = False,
                loop_planned: bool = False, has_disclosure: bool = False,
                lufs: float | None = None) -> dict:
    rows = _rows(board)
    links: dict[str, dict] = {}

    def L(name: str, ok: bool, note: str) -> None:
        links[name] = {"ok": bool(ok), "note": note}

    n = len(rows)
    roles = [_role(r) for r in rows]

    # 1 promise: the packaging claim is declared
    L("promise", bool(title.strip()),
      "title/promise declared" if title.strip()
      else "no title - the promise is undeclared")

    # 2 click: title length band (packaging earns the click)
    t = title.strip()
    lo, hi = (22, 35) if shorts else (18, 60)
    ideal = (24, 27) if shorts else None
    if not t:
        L("click", False, f"no title to score (band {lo}-{hi} chars)")
    elif lo <= len(t) <= hi:
        extra = (f" (ideal {ideal[0]}-{ideal[1]})"
                 if ideal and ideal[0] <= len(t) <= ideal[1] else "")
        L("click", True, f"title {len(t)} chars in band {lo}-{hi}{extra}")
    else:
        L("click", False, f"title {len(t)} chars outside band {lo}-{hi}")

    # 3 first_3s_gate: hook role lands inside the window
    first_end = float(rows[0].get("t_end", 0) or 0)
    if roles[0].startswith("hook") and 0 < first_end <= 4.0:
        L("first_3s_gate", True,
          f"hook at beat 1 ends {first_end:.1f}s (thumb-stop lands)")
    elif roles[0].startswith("hook"):
        L("first_3s_gate", False,
          f"hook beat drags to {first_end:.1f}s - the 0.5s window is gone")
    else:
        L("first_3s_gate", False,
          f"beat 1 role is {roles[0]!r}, not hook - no thumb-stop")

    # 4 engaged_open: the viewer who stays gets an immediate open
    t0 = float(rows[0].get("t_start", 0) or 0)
    if _text(rows[0]) and t0 <= 0.5:
        L("engaged_open", True,
          f"VO opens at {t0:.2f}s (G8 first-word law) - stay converts")
    elif not _text(rows[0]):
        L("engaged_open", False, "hook beat carries no VO - dead open")
    else:
        L("engaged_open", False, f"VO starts at {t0:.2f}s - dead air first")

    # 5 open_loops: But/Therefore / cue / driver evidence
    lint = but_therefore_lint(rows)
    L("open_loops", not lint,
      "loop cues present (driver/connector/cue-word)"
      if not lint else "; ".join(lint[:2]))

    # 6 one_peak: exactly one payoff, positioned late
    peak_idx = [i for i, r in enumerate(roles) if r.startswith(_PEAK_ROLES)]
    if len(peak_idx) == 1 and peak_idx[0] >= n // 2:
        L("one_peak", True,
          f"one peak at beat {peak_idx[0] + 1}/{n} (late = remembered)")
    elif len(peak_idx) == 0:
        L("one_peak", False, "no payoff beat - the peak cannot exist")
    elif len(peak_idx) > 1:
        L("one_peak", False,
          f"{len(peak_idx)} payoff beats {[(i + 1) for i in peak_idx]} - "
          "diluted peak (pick ONE)")
    else:
        L("one_peak", False,
          f"peak at beat {peak_idx[0] + 1}/{n} - too early (escalation law)")

    # 7 engineered_end: abrupt payoff, no end-signal phrases
    last_txt = _text(rows[-1]).lower()
    hit = next((b for b in _END_BANS if b in last_txt), None)
    if hit:
        L("engineered_end", False,
          f"last beat signals the end ({hit!r}) - peak-end law: the END is "
          "half the remembered experience")
    else:
        L("engineered_end", True,
          "no end-signal phrase - abrupt payoff preserved")

    # 8 loop: rewatch handoff or session handoff designed
    if loop_planned or has_end_screen:
        L("loop", True,
          "end-screen/loop handoff planned (rewatch = free engaged views)")
    elif any("cua" in r for r in roles):
        L("loop", True, "CTA beat present (session handoff, long-form)")
    else:
        L("loop", False,
          "no loop/end-screen/CTA handoff - the video ends into nothing")

    # 9 satisfaction: disclosure + loudness + a real voice
    probs = []
    if not any(_text(r) for r in rows):
        probs.append("no VO text anywhere")
    if has_disclosure is False:
        probs.append("AI disclosure line not planned (3-strike shield)")
    if lufs is not None and not (-16.0 <= lufs <= -12.0):
        probs.append(f"measured {lufs} LUFS outside -16..-12")
    L("satisfaction", not probs,
      "disclosure planned + VO present + loudness in band"
      if not probs else "; ".join(probs))

    weak = [k for k in LINK_NAMES if not links[k]["ok"]]
    curve = curve_forecast(rows)
    return {"links": links, "weak": weak, "curve": curve,
            "ok": not weak and curve["sickness"] in ("healthy",),
            "n_beats": n}


def verdict(report: dict) -> str:
    if report["ok"]:
        return (f"CHAIN 9/9 + curve {report['curve']['sickness']} - "
                "cleared for render")
    weak = ", ".join(report["weak"]) or report["curve"]["sickness"]
    return f"CHAIN BROKEN at: {weak} (curve: {report['curve']['sickness']})"
