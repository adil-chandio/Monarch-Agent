"""Genre + length-class engine for the script layer (SCRIPT FORENSICS 2026-09-24).

Studied: vidiQ 4-part template (hook names the problem <15s, 3-5 body
points, CTA, end screen; 125-150 wpm), distribution.ai (outcome + angle
first), Boords/Celtx (logline -> synopsis -> outline; two-column
audio-visual script), Alwrity planner (8 VIDEO_TYPE_CONFIGS + duration
splits 3/24/3 for shorts), rahulanand1103 (blueprint -> research ->
refined blueprint -> time-boxed writer).

What Monarch already had (stays canon): exact word maths, N1-N5 drivers,
variable-ratio roles, humanize. What was missing and lands here:
* GENRES - per-genre hook strategy, structure bias, CTA focus, visual
  keywords (deterministic templates; no LLM in the loop, honest)
* LENGTH_CLASSES - hook/main/cta second splits + clip/word budgets per
  class (shorts30/short60/medium150/long420); the default 60-class
  maths stays EXACTLY as shipped (60s | 2.5 | 3.5 | 18 x 7)
* logline(topic, genre) - Celtx chain step 1 as a real artifact
* av_script() - two-column VISUAL|AUDIO markdown (Boords/vidIQ format)

Fail-closed: unknown genre/class = ValueError. Deterministic: same
inputs, same plan - suite-verified.
"""

from __future__ import annotations

from monarch.core.words import count_words

#: genre -> script DNA (adapted from Alwrity VIDEO_TYPE_CONFIGS, tuned
#: for faceless vertical shorts; hook strategies follow vidIQ's
#: "name the problem/result in the first seconds" law)
GENRES: dict[str, dict] = {
    "mystery": {
        "hook_strategy": "name the unresolved question + a number (N1)",
        "structure": ("hook", "tease", "payoff", "value-debt", "payoff+cua"),
        "cta_focus": "follow for the next file that nobody opens",
        "visual_style": "high contrast, one focal subject, dark plates",
        "sfx_bias": "heartbeat",
    },
    "tutorial": {
        "hook_strategy": "problem statement or preview of the result",
        "structure": ("hook", "value-debt", "payoff", "payoff", "payoff+cua"),
        "cta_focus": "try it yourself, subscribe for more how-tos",
        "visual_style": "clean steps, one object per beat, bright plates",
        "sfx_bias": "shine",
    },
    "review": {
        "hook_strategy": "strong opinion or verdict tease",
        "structure": ("hook", "tease", "value-debt", "payoff", "payoff+cua"),
        "cta_focus": "links in the description, subscribe for verdicts",
        "visual_style": "product close-ups, split comparisons",
        "sfx_bias": "hit",
    },
    "educational": {
        "hook_strategy": "surprising fact or intriguing question",
        "structure": ("hook", "tease", "payoff", "value-debt", "payoff+cua"),
        "cta_focus": "subscribe to keep learning in 60 seconds",
        "visual_style": "concept diagrams, motion labels",
        "sfx_bias": "sonar_ping",
    },
    "entertainment": {
        "hook_strategy": "energy + immediate stakes, zero warm-up",
        "structure": ("hook", "payoff", "tease", "payoff", "payoff+cua"),
        "cta_focus": "share this with the friend who does this",
        "visual_style": "dynamic cuts, expressive motion snaps",
        "sfx_bias": "bass_drop",
    },
    "listicle": {
        "hook_strategy": "count promise (3 secrets nobody lists)",
        "structure": ("hook", "payoff", "payoff", "value-debt", "payoff+cua"),
        "cta_focus": "save this list, subscribe for the next one",
        "visual_style": "numbered frames, one item per beat",
        "sfx_bias": "shine",
    },
    "storytelling": {
        "hook_strategy": "drop the viewer mid-scene (cold open)",
        "structure": ("hook", "tease", "value-debt", "payoff", "payoff+cua"),
        "cta_focus": "follow for the rest of the story",
        "visual_style": "cinematic silhouettes, mood light",
        "sfx_bias": "heartbeat",
    },
    "product": {
        "hook_strategy": "transformation promise (before -> after)",
        "structure": ("hook", "value-debt", "payoff", "payoff", "payoff+cua"),
        "cta_focus": "get it via the link while it lasts",
        "visual_style": "polished mockups, benefit callouts",
        "sfx_bias": "shine",
    },
}

#: length class -> second splits + clip/word budgets. short60 mirrors the
#: shipped default maths exactly (2.5 first + 3.5 body -> 18 x 7 words).
LENGTH_CLASSES: dict[str, dict] = {
    "shorts30": {"target_s": 30.0, "first_clip_s": 2.0, "clip_s": 2.5,
                 "wps": 2.4, "words_per_clip": 6},
    "short60": {"target_s": 60.0, "first_clip_s": 2.5, "clip_s": 3.5,
                "wps": 2.2, "words_per_clip": 7},
    "medium150": {"target_s": 150.0, "first_clip_s": 3.0, "clip_s": 3.5,
                  "wps": 2.3, "words_per_clip": 8},
    "long420": {"target_s": 420.0, "first_clip_s": 4.0, "clip_s": 4.0,
                "wps": 2.3, "words_per_clip": 9},
}

#: vidIQ research band (written-word wpm; fit_words trims, so the honest
#: audit band is wider than the 125-150 ideal - reported, not invented)
WPM_IDEAL = (125.0, 150.0)
WPM_GATE = (100.0, 170.0)


def beat_plan(genre: str, length_class: str) -> list[dict]:
    """Ordered beat roles with second+word budgets (deterministic).

    The genre's structure is CYCLED across the scene count so the N3
    variable-ratio engine still owns pacing; hook and CTA stay pinned
    first/last (vidIQ 4-part law).
    """
    g = GENRES.get(genre)
    if not g:
        raise ValueError(f"unknown genre {genre!r}: use {' | '.join(GENRES)}")
    lc = LENGTH_CLASSES.get(length_class)
    if not lc:
        raise ValueError(f"unknown length class {length_class!r}: "
                         f"use {' | '.join(LENGTH_CLASSES)}")
    import math
    n = max(4, math.ceil((lc["target_s"] - lc["first_clip_s"])
                         / lc["clip_s"]) + 1)
    mid = list(g["structure"][1:-1])
    beats: list[dict] = [{"i": 1, "role": "hook",
                          "s": lc["first_clip_s"],
                          "words": lc["words_per_clip"]}]
    t = lc["first_clip_s"]
    for i in range(2, n):
        role = mid[(i - 2) % len(mid)]
        beats.append({"i": i, "role": role, "s": lc["clip_s"],
                      "words": lc["words_per_clip"]})
        t += lc["clip_s"]
    beats.append({"i": n, "role": "payoff+cua", "s": lc["clip_s"],
                  "words": lc["words_per_clip"]})
    return beats


def plan_budget(genre: str, length_class: str) -> dict:
    """Aggregate beat plan -> budget summary + honest wpm math."""
    beats = beat_plan(genre, length_class)
    total_s = sum(b["s"] for b in beats)
    total_w = sum(b["words"] for b in beats)
    wpm = total_w / total_s * 60.0 if total_s else 0.0
    return {
        "genre": genre,
        "length_class": length_class,
        "beats": beats,
        "scenes": len(beats),
        "total_s": round(total_s, 2),
        "total_words": total_w,
        "wpm": round(wpm, 1),
        "wpm_ideal": WPM_IDEAL,
        "in_ideal_band": WPM_IDEAL[0] <= wpm <= WPM_IDEAL[1],
        "structure": GENRES[genre]["structure"],
        "cta_focus": GENRES[genre]["cta_focus"],
    }


def logline(topic: str, genre: str = "mystery") -> str:
    """Celtx chain step 1: the 2-sentence essence, deterministic."""
    g = GENRES.get(genre)
    if not g:
        raise ValueError(f"unknown genre {genre!r}")
    topic = ((topic or "").strip() or "an untold file").lower()
    if topic.startswith(("the ", "a ", "an ")):
        topic = topic.split(" ", 1)[1]     # no double articles in the logline
    hooks = {
        "mystery": f"One {topic} case sat sealed for decades - and the number never added up.",
        "tutorial": f"One {topic} method breaks the task into steps anyone lands on the first try.",
        "review": f"Everyone {topic} gets one verdict - and it is not the one the ads paid for.",
        "educational": f"Everyone repeats the {topic} rule; almost nobody knows why it holds.",
        "entertainment": f"The {topic} idea sounds harmless until it is your turn.",
        "listicle": f"Three {topic} secrets exist - the third one changes the whole list.",
        "storytelling": f"The {topic} story starts where every other telling stops.",
        "product": f"The {topic} promise is simple: before and after, on camera.",
    }
    first = hooks.get(genre, hooks["mystery"])
    return f"{first} {g['cta_focus'][0].upper() + g['cta_focus'][1:]} - that is the debt this video pays."


def av_script(board_rows: list[dict], title: str = "") -> str:
    """Two-column VISUAL|AUDIO markdown (Boords/vidIQ industry format).

    Visual column = the :: visual :: field (show, don't tell); audio
    column = the spoken line + sfx cue. Counts stay engine-side: the
    board rows already carry engine-counted words.
    """
    out = [f"# AV SCRIPT - {title or 'untitled'}", "",
           "| # | VISUAL | AUDIO (VO + SFX) | words | t_start |",
           "|---|--------|-------------------|-------|---------|"]
    for s in board_rows:
        vo = str(s.get("vo_line", "")).replace("|", "/")
        visual = str(s.get("visual", "")).replace("|", "/")
        sfx = str(s.get("sfx", "")).strip()
        audio = f"{vo} **[SFX: {sfx}]**" if sfx else vo
        out.append(f"| {s.get('id', '')} | {visual} | {audio} | "
                   f"{count_words(vo)} | {s.get('t_start', '')} |")
    out.append("")
    out.append("_Format: two-column audio-visual (Boords/vidIQ standard); "
               "word counts from the engine tokenizer, never by hand._")
    return "\n".join(out) + "\n"
