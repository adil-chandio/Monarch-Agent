"""MONARCH V6 overlay engine — canon becomes pixels (W-A1/W-A2).

Builds a libass (ASS subtitle) layer burned by the render's existing
``subtitles`` filter — ZERO new dependencies (the binary already burns
captions, so libass is proven). What it emits:

* KARAOKE captions (W-A2): per-scene VO lines split into words with
  char-weighted timing; \\k tags fill each word as it is spoken
  (the +15% AVD lever, ARSENAL A4). Occupies the BOTTOM band (y=1450).
* TEXT_SYNCED cue texts (W-A1): V6 keyword texts at the TOP band
  (y=320 — the bottom is reserved for karaoke, so the planner's
  alternate-band output is remapped; y=750 stays forbidden).
* END SCREEN (W-A1): last 7 s, right 40% mockup, gold border,
  WATCH HERE arrow (miss #13 law).
* PROGRESS BAR (W-A1): gold, bottom edge, stepped.
* LOOP TAIL (W-A1): EVERY event ends at dur - LOOP_TAIL_S so the
  closing frames carry no overlay — the precondition for the
  end-frame==start-frame loop law.

ASS specifics used here: colors are &HAABBGGRR; \\k units are
centiseconds; drawn boxes use \\p1 paths anchored with \\an7\\pos.
"""

from __future__ import annotations

# --- laws (mirrored from shorts.py / VIRAL_SHORTS_V6) ---------------------
Y_TOP = 320            # cue band (bottom belongs to karaoke)
Y_KARAOKE = 1450       # caption band
CENTER = 540           # horizontal center for 1080
PROGRESS_H = 12        # gold bar at the very bottom edge
LOOP_TAIL_S = 0.2      # no-overlay tail: the loop-law precondition
END_SCREEN_S = 7.0     # miss #13: element lives in the last 7 s
END_W = 0.40           # right-40% mockup
SHOW_S = 1.7           # V6 text show window
FADE_S = 0.3
PLATE = "&HA0000000"   # ~ (0,0,0,160) semi-transparent plate (miss #7)
GOLD = "&H0000D7FF"    # #FFD700 in BGR
GOLD_RAW = "00D7FF"    # bare BGR hex for inline \\1C&H...& overrides
WHITE = "&H00FFFFFF"
GREY = "&H00888888"
DARK = "&H50000000"

_ANIM_TEMPLATES = {
    "pop":    r"{\fscx60\fscy60\t(0,140,\fscx112\fscy112)"
              r"\t(140,240,\fscx100\fscy100)",
    "slideL": None,   # needs \move with coordinates - handled inline
    "slideR": None,
    "fade":   r"{\alpha&HFF&\t(0,220,\alpha&H00&)",
    "bounce": r"{\fscx40\fscy40\t(0,120,\fscx118\fscy118)"
              r"\t(120,200,\fscx88\fscy88)"
              r"\t(200,300,\fscx104\fscy104)"
              r"\t(300,380,\fscx100\fscy100)",
    "zoom":   r"{\fscx320\fscy320\t(0,260,\fscx100\fscy100)",
}


# ---------------------------------------------------------------------------
# word timing (W-A2) — self-synth law: our VO is deterministic, so word
# times are computed, never guessed (forensic F5 solution)
# ---------------------------------------------------------------------------


def word_timings(text: str, t0: float, t1: float) -> list[tuple[str, float, float]]:
    """Split a VO line into (word, start, end) — char-weighted, monotonic.

    The window [t0, t1] is the scene's VO window; punctuation gets no
    extra time (weights are alpha-character counts).
    """
    words = [w for w in str(text).split() if any(ch.isalnum() for ch in w)]
    if not words:
        return []
    span = max(0.05, float(t1) - float(t0))
    weights = [max(1, sum(1 for ch in w if ch.isalnum())) for w in words]
    total = sum(weights)
    out: list[tuple[str, float, float]] = []
    cursor = float(t0)
    for w, wt in zip(words, weights):
        d = span * wt / total
        out.append((w, round(cursor, 3), round(min(float(t1), cursor + d), 3)))
        cursor += d
    return out


def _ass_time(t: float, *, cap: float | None = None) -> str:
    if cap is not None:
        t = min(t, cap)
    t = max(0.0, t)
    cs = int(round(t * 100))
    h, rem = divmod(cs, 360000)
    m, rem = divmod(rem, 6000)
    s, c = divmod(rem, 100)
    return f"{h}:{m:02d}:{s:02d}.{c:02d}"


def _clean(text: str) -> str:
    return (str(text).replace("{", "(").replace("}", ")")
            .replace("\n", " ").strip().upper())


# ---------------------------------------------------------------------------
# the V6 ASS builder
# ---------------------------------------------------------------------------


def v6_ass(scenes: list[tuple[float, float, str]], *,
           cues: list[dict] | None = None,
           dur_s: float,
           end_screen: bool = False,
           progress: bool = True,
           karaoke: bool = True,
           w: int = 1080,
           h: int = 1920) -> str:
    """Build the complete V6 overlay layer as an ASS document.

    scenes   = [(start, end, vo_line)] — the VO windows already shipped
               as captions.srt; same windows now burn as karaoke.
    cues     = shorts.plan_texts() output (text/appear/y/anim/show_s/...).
               With karaoke on, cues are remapped to the TOP band.
    dur_s    = the video duration; every event ends at dur-LOOP_TAIL_S.
    """
    if dur_s <= 0:
        raise ValueError("duration must be > 0 (assumed durations are miss #12)")
    end_cap = max(0.05, dur_s - LOOP_TAIL_S)
    cues = cues or []
    out: list[str] = []

    # ---- header + styles -------------------------------------------------
    out.append("[Script Info]")
    out.append("ScriptType: v4.00+")
    out.append(f"PlayResX: {w}")
    out.append(f"PlayResY: {h}")
    out.append("WrapStyle: 2")
    out.append("ScaledBorderAndShadow: yes")
    out.append("")
    out.append("[V4+ Styles]")
    out.append("Format: Name, Fontname, Fontsize, PrimaryColour, "
               "SecondaryColour, OutlineColour, BackColour, Bold, Italic, "
               "Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, "
               "BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, "
               "MarginV, Encoding")
    out.append(f"Style: V6Kar,Sans,58,{WHITE},{GREY},{PLATE},&H00000000,-1,0,0,0,100,100,1,0,3,4,0,5,0,0,0,1")
    out.append(f"Style: V6Cue,Sans,76,{WHITE},{GREY},{PLATE},&H00000000,-1,0,0,0,100,100,1,0,3,8,0,5,0,0,0,1")
    out.append(f"Style: V6End,Sans,56,{GOLD},{GREY},&H96000000,&H00000000,-1,0,0,0,100,100,1,0,3,3,0,5,0,0,0,1")
    out.append(f"Style: V6Sub,Sans,40,{WHITE},{GREY},&H00000000,&H00000000,-1,0,0,0,100,100,1,0,1,2,0,5,0,0,0,1")
    out.append(f"Style: V6Draw,Sans,40,{WHITE},{GREY},&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1")
    out.append("")
    out.append("[Events]")
    out.append("Format: Layer, Start, End, Style, Name, MarginL, MarginR, "
               "MarginV, Effect, Text")

    # ---- karaoke captions (W-A2) ----------------------------------------
    if karaoke:
        for (a, b, line) in scenes:
            words = word_timings(line, a, min(b, end_cap))
            if not words:
                continue
            tags = " ".join(f"{{\\k{max(1, int(round((we - ws) * 100)))}}}{_clean(wd)}"
                            for (wd, ws, we) in words)
            out.append(f"Dialogue: 0,{_ass_time(a)},{_ass_time(min(b, end_cap))},"
                       f"V6Kar,,0,0,0,,{{\\pos({CENTER},{Y_KARAOKE})}}{tags}")

    # ---- TEXT_SYNCED cue texts (W-A1) ------------------------------------
    for c in cues:
        appear = float(c.get("appear", 0.0))
        show = float(c.get("show_s", SHOW_S))
        start = min(appear, end_cap)
        end = min(appear + show, end_cap)
        if end - start < 0.05:
            continue
        anim = str(c.get("anim", "pop"))
        y = Y_TOP                      # bottom band is karaoke's (remap)
        text = _clean(c.get("text", ""))
        if not text:
            continue
        head = _ANIM_TEMPLATES.get(anim)
        if anim == "slideL":
            body = (f"{{\\move({CENTER - 200},{y},{CENTER},{y},0,200)")
        elif anim == "slideR":
            body = (f"{{\\move({CENTER + 200},{y},{CENTER},{y},0,200)")
        elif head:
            body = head
        else:
            body = "{"
        show_ms = int((end - start) * 1000)
        fade_ms = int(FADE_S * 1000)
        body += f"\\t({max(0, show_ms - fade_ms)},{show_ms},\\alpha&HC8&)" + "}"
        out.append(f"Dialogue: 1,{_ass_time(start)},{_ass_time(end)},"
                   f"V6Cue,,0,0,0,,{{\\pos({CENTER},{y})}}{body}{text}")

    # ---- end screen (miss #13): last 7 s, right 40%, gold ----------------
    if end_screen:
        es_a = max(0.0, dur_s - END_SCREEN_S)
        es_b = end_cap
        x1 = int(w * (1 - END_W)) + 8
        y1 = int(h * 0.40)
        x2 = w - 16
        y2 = int(h * 0.66)
        bw = x2 - x1
        bh = y2 - y1
        border = 6
        # gold outer rect, dark inner rect (drawn, an7 top-left anchor)
        out.append(f"Dialogue: 2,{_ass_time(es_a)},{_ass_time(es_b)},"
                   f"V6Draw,,0,0,0,,{{\\an7\\pos({x1},{y1})\\p1}}"
                   f"m 0 0 l {bw} 0 {bw} {bh} 0 {bh}{{\\p0}}")
        out.append(f"Dialogue: 2,{_ass_time(es_a)},{_ass_time(es_b)},"
                   f"V6Draw,,0,0,0,,{{\\an7\\pos({x1 + border},{y1 + border})"
                   f"\\p1\\1C&H201010&\\3C&H201010&}}"
                   f"m 0 0 l {bw - 2 * border} 0 {bw - 2 * border} "
                   f"{bh - 2 * border} 0 {bh - 2 * border}{{\\p0}}")
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2
        out.append(f"Dialogue: 3,{_ass_time(es_a)},{_ass_time(es_b)},"
                   f"V6End,,0,0,0,,{{\\pos({cx},{cy - 34})}}FULL VIDEO")
        out.append(f"Dialogue: 3,{_ass_time(es_a)},{_ass_time(es_b)},"
                   f"V6Sub,,0,0,0,,{{\\pos({cx},{cy + 26})\\c{GOLD}}}"
                   f">>> WATCH HERE >>>")

    # ---- progress bar: gold, bottom edge, stepped -------------------------
    if progress:
        step = 0.5
        out.append(f"Dialogue: 0,{_ass_time(0.0)},{_ass_time(end_cap)},"
                   f"V6Draw,,0,0,0,,{{\\an7\\pos(0,{h - PROGRESS_H})\\p1"
                   f"\\1C&H303030&\\3C&H303030&}}"
                   f"m 0 0 l {w} 0 {w} {PROGRESS_H} 0 {PROGRESS_H}{{\\p0}}")
        t = 0.0
        while t < end_cap:
            t2 = min(t + step, end_cap)
            frac = t2 / dur_s
            bw = max(PROGRESS_H, int(w * frac))
            out.append(f"Dialogue: 1,{_ass_time(t)},{_ass_time(t2)},"
                       f"V6Draw,,0,0,0,,{{\\an7\\pos(0,{h - PROGRESS_H})\\p1"
                       f"\\1C&H{GOLD_RAW}&\\3C&H{GOLD_RAW}&}}"
                       f"m 0 0 l {bw} 0 {bw} {PROGRESS_H} 0 {PROGRESS_H}{{\\p0}}")
            t = t2
    return "\n".join(out) + "\n"


def sweep_ass(ass_text: str, dur_s: float) -> list[str]:
    """Verify the verify (L15): parse our own ASS for law breaches.

    Returns a list of violations — empty = the layer obeys: no event
    ends after dur-LOOP_TAIL_S (loop tail), no \\pos at y=750 (miss #7),
    end-screen text present iff requested... (caller checks that one).
    """
    issues: list[str] = []
    cap = dur_s - LOOP_TAIL_S + 1e-6
    for ln in ass_text.splitlines():
        if not ln.startswith("Dialogue:"):
            continue
        parts = ln.split(",")
        end = parts[1].strip()
        hh, mm, rest = end.split(":")
        end_s = int(hh) * 3600 + int(mm) * 60 + float(rest)
        if end_s > cap:
            issues.append(f"event ends {end_s:.2f}s > loop-tail cap {cap:.2f}s: {ln[:60]}")
        if "750)" in ln and "\\pos(" in ln:
            issues.append(f"possible y=750 placement: {ln[:60]}")
    return issues
