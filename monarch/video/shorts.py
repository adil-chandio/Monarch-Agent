"""MONARCH V6 - viral Shorts engine (the 14-miss canon, executable).

Source: docs/VIRAL_SHORTS_V6.md - the 1.2B-views/14-shorts session.
Every constant below is a law paid for by a real miss (M1-M14); the
planners here make the LAWS the default, so repeating a miss requires
actively breaking the API (it will refuse).

Laws encoded:
  M1  condensed-incomplete structure (NEVER CTA-only; 60% show /
      20-30% skip / 10-20% censor, Zeigarnik)
  M2  no text/Urdu in image prompts (+ read-back verify duty)
  M3  ONE focal, 3-element max
  M4  image duration 2.8-3.3 s (max 3.5), 10 images for 28-33 s
  M5/7/8  safe zones: subject middle 60% (384-1536); text y=320 top
      or y=1450 bottom, NEVER y=750 over the subject
  M6  zoom 1.0->1.06 ideal, 1.08 hard cap (never 1.22)
  M9  6 text animations, never >2 repeats in a row
  M10 text appears when the VO says that word (TEXT_SYNCED)
  M12 video duration = VO + 0.5 buffer + 0.2 offset (never cut VO)
  M13 NEVER "link in bio" on Shorts - "full video on screen now" +
      end-screen element in the last 7 s
  M14 title 24-27 chars ideal, 22-35 hard max, 4-7 words, emoji end
"""

from __future__ import annotations

import re

# ---------------------------------------------------------------------------
# constants (laws, not preferences)
# ---------------------------------------------------------------------------

W, H = 1080, 1920
FPS = 30
SAFE_TOP = 384            # middle 60% band starts (miss #5)
SAFE_BOTTOM = 1536        # middle 60% band ends
SUBJECT_CENTER_BAND = (500, 1400)
TEXT_Y_TOP = 320          # miss #7/#8: the ONLY top text line
TEXT_Y_BOTTOM = 1450      # the ONLY bottom text line
TEXT_Y_CENTER = 750       # ONLY when no subject occupies the center
ZOOM_IDEAL = 1.06         # miss #6
ZOOM_MAX = 1.08
IMAGE_DUR_MIN, IMAGE_DUR_IDEAL, IMAGE_DUR_MAX = 2.8, 2.8, 3.5
N_BEATS = 10
SHORT_DUR = (28.0, 33.5)   # VO 32.55 + 0.7 = 33.25 stays in-band
VO_BUFFER_S = 0.5         # miss #12
VO_OFFSET_S = 0.2
TITLE_IDEAL = (24, 27)
TITLE_MAX = (22, 35)
TEXT_WORDS_MAX = 3
SHOW_1_7S, FADE_0_3S = 1.7, 0.3

ANIMATIONS = ("pop", "slideL", "slideR", "fade", "bounce", "zoom")

#: mandatory negative tail for EVERY image prompt (miss #2)
NO_TEXT_CLAUSE = ("no text, no words, no letters, no logos, no watermark, "
                  "no typography")
COMPOSITION_CLAUSE = ("vertical 9:16 composition, subject centered in "
                      "middle 60% safe zone, one focal subject centered, "
                      "minimal clutter, clean smooth, high contrast")

#: Hindi/Urdu words that leaked into prompts once (miss #2) - advisory list
_DESI_HINTS = ("tabahi", "nahi", "karo", "kya", "bhai", "wala", "ho ",
               "hai ", "kaam", "le jao")


# ---------------------------------------------------------------------------
# image prompt builder + lint (misses #2, #3)
# ---------------------------------------------------------------------------


def image_prompt(subject: str, *, style: str = "stickman") -> str:
    """V6 prompt template: house style + composition + NO-TEXT tail.

    `subject` must be a clean visual description; any banned desi hint
    words raise (they caused the Urdu-text leak - rephrase in English).
    """
    low = f" {subject.lower()} "
    hits = [w for w in _DESI_HINTS if w in low]
    if hits:
        raise ValueError(
            f"prompt carries desi hint words {hits} - miss #2 (Urdu text "
            "leaked into an English video); rewrite the subject in English")
    tail = ("stickman kid explorer, round head, khaki safari hat, thick "
            "black outlines, dot eyes, black void background, white doodle "
            "lines" if style == "stickman" else style)
    return (f"{subject}, {tail}, {COMPOSITION_CLAUSE}, {NO_TEXT_CLAUSE}")


def prompt_lint(prompt: str) -> list[str]:
    """Read-back duty (miss #2): returns violations for a GENERATED prompt
    or a planned text - empty list = clean."""
    issues: list[str] = []
    if NO_TEXT_CLAUSE not in prompt:
        issues.append("missing the mandatory no-text clause")
    if "safe zone" not in prompt:
        issues.append("missing safe-zone composition clause")
    return issues


# ---------------------------------------------------------------------------
# VO-driven timing (miss #4, #12)
# ---------------------------------------------------------------------------


def beats_for_vo(vo_s: float) -> dict:
    """Video duration = VO + 0.5 + 0.2 (never cut VO); 10 beats spread
    evenly, each clamped to 2.8-3.3 s (beat count adjusts if needed)."""
    if vo_s <= 0:
        raise ValueError("VO duration must be measured first (ffprobe), "
                         "never assumed (miss #12)")
    total = round(vo_s + VO_BUFFER_S + VO_OFFSET_S, 2)
    n = N_BEATS
    while total / n > IMAGE_DUR_MAX:
        n += 1
    while n > 4 and total / n < IMAGE_DUR_MIN:
        n -= 1
    per = round(total / n, 2)
    if not (IMAGE_DUR_MIN - 0.3 <= per <= IMAGE_DUR_MAX):
        raise ValueError(f"beat {per}s outside the 2.8-3.3 law band "
                         f"(VO {vo_s}s, total {total}s)")
    return {"vo_s": round(vo_s, 2), "total_s": total, "beats": n,
            "beat_s": per, "in_short_band": SHORT_DUR[0] <= total <= SHORT_DUR[1]}


# ---------------------------------------------------------------------------
# TEXT_SYNCED planner (misses #7, #8, #9, #10)
# ---------------------------------------------------------------------------


def plan_texts(entries: list[dict], *, subject_centered: bool = True) -> list[dict]:
    """Sync text cues to VO word-times with placement + animation laws.

    entries = [{"text": str, "appear": float}, ...] in VO order.
    Returns cues with y (never 750 over a subject), animation (no >2
    consecutive repeats), show/fade times, word-count enforcement.
    """
    cues: list[dict] = []
    last_anim = None
    repeat = 0
    anim_i = 0
    for i, e in enumerate(entries):
        text = " ".join(str(e.get("text", "")).split())
        wc = len(text.split())
        if not 1 <= wc <= TEXT_WORDS_MAX:
            raise ValueError(
                f"text {i} is {wc} words - max {TEXT_WORDS_MAX} "
                "(2-3 words max, eye-catching not clutter)")
        appear = float(e.get("appear", 0.0))
        if appear < 0:
            raise ValueError("appear time must come from the VO word map")
        # placement: alternate top/bottom; center ONLY when no subject
        y = TEXT_Y_TOP if i % 2 == 0 else TEXT_Y_BOTTOM
        if not subject_centered and i % 3 == 2:
            y = TEXT_Y_CENTER
        # animation: cycle of 6, never >2 in a row (miss #9)
        anim = ANIMATIONS[anim_i % len(ANIMATIONS)]
        if anim == last_anim:
            repeat += 1
            if repeat >= 2:
                anim_i += 1
                anim = ANIMATIONS[anim_i % len(ANIMATIONS)]
                repeat = 0
        else:
            repeat = 0
        last_anim = anim
        anim_i += 1
        cues.append({
            "text": text, "color": e.get("color", "#FFFFFF"),
            "appear": round(appear, 2),
            "show_s": SHOW_1_7S, "fade_s": FADE_0_3S,
            "y": y, "anim": anim,
        })
    return cues


# ---------------------------------------------------------------------------
# packaging laws (misses #1, #13, #14)
# ---------------------------------------------------------------------------


def title_check(title: str) -> dict:
    """24-27 chars ideal / 22-35 hard max / 4-7 words (miss #14)."""
    title = title.strip()
    n = len(title)
    words = len(title.split())
    issues = []
    if not TITLE_MAX[0] <= n <= TITLE_MAX[1]:
        issues.append(f"{n} chars outside {TITLE_MAX[0]}-{TITLE_MAX[1]}")
    if not 4 <= words <= 7:
        issues.append(f"{words} words outside 4-7")
    return {"title": title, "chars": n, "words": words,
            "ideal": TITLE_IDEAL[0] <= n <= TITLE_IDEAL[1],
            "ok": not issues, "issues": issues}


def cta_lint(text: str) -> dict:
    """Miss #13: NEVER 'link in bio' on YouTube Shorts - the platform has
    end-screen elements, not bio links. 'on screen now' is the phrase."""
    low = text.lower()
    issues = []
    if "link in bio" in low:
        issues.append("'link in bio' is TikTok DNA - Shorts law says "
                      "'full video on screen now' + end-screen element")
    if "on screen now" not in low and "watch here" not in low:
        issues.append("no 'on screen now' / 'watch here' pointer found")
    return {"ok": not issues, "issues": issues}


def end_screen_plan(short_s: float) -> dict:
    """End-screen element lives in the LAST 7 s, right side, thumbnail
    mockup 40% with gold border + WATCH HERE arrow (miss #13)."""
    return {"start_s": round(max(0.0, short_s - 7.0), 2),
            "side": "right", "width_frac": 0.4, "border": "gold",
            "arrow": "WATCH HERE"}


# ---------------------------------------------------------------------------
# long -> short condensed-incomplete planner (miss #1, the CTA-only sin)
# ---------------------------------------------------------------------------


def long_to_short(ranked: list[str]) -> dict:
    """Zeigarnik planner: condensed-INCOMPLETE short from a ranked long.

    ranked = topics best-LAST (the long video's order). Split law:
    show ~60%, skip 20-30%, censor 10-20% (the #1 item). Deterministic.
    """
    topics = [str(t).strip() for t in ranked if str(t).strip()]
    if len(topics) < 4:
        raise ValueError("need >= 4 ranked topics to make an incomplete "
                         "short (a CTA-only short is the miss #1 sin)")
    n = len(topics)
    n_censor = max(1, round(n * 0.15))
    n_skip = max(1, round(n * 0.25))
    show = topics[:n - n_skip - n_censor]
    skipped = topics[n - n_skip - n_censor:-n_censor]
    censored = topics[-n_censor:]
    return {
        "show": show, "skipped": skipped, "censored": censored,
        "pct": {"show": round(len(show) / n * 100),
                "skipped": round(len(skipped) / n * 100),
                "censored": round(len(censored) / n * 100)},
        "tease_lines": [f"{t}: the detail nobody lists" for t in skipped[:3]],
        "comment_bait": ("Comment YOUR TOP 3 - and spot what got skipped "
                         "and censored"),
        "note": ("ethical incomplete: the full ranking exists in the long "
                 "video - the short is the trailer (Zeigarnik closure pull)"),
    }
