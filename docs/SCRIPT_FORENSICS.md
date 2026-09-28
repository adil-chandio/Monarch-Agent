# SCRIPT FORENSICS — 5 articles + 2 repos under the microscope (2026-09-24)

Operator order: deep study, 10x, no gaps. Subject: script-writing knowledge
+ two OSS script-writer repos, verdicted against Monarch's script engine.
Method: every source read live; every idea verdicted **adopt / already-had /
rejected** with the reason. Nothing adopted on vibes — everything adopted is
in `monarch/video/genres.py` + director/pipeline/audit, suite-tested (372).

## Sources

1. vidiQ — "How to Write a YouTube Video Script (Template + Examples)"
2. distribution.ai — "A Practical Guide to YouTube Script Writing" (Ross Simmonds)
3. Boords — "How to Write a Script (Step-by-Step Guide)"
4. Celtx blog — "How to Write a Script: From Idea to Screenplay"
5. Toronto Film School — "The A to Z of Script Writing Explained"
6. repo: rahulanand1103/youtube-script-writer (35⭐, LangGraph agent)
7. repo: ALwrity/ALwrity (1174⭐, FastAPI platform — youtube planner + scene builder)

## Findings → verdicts

| # | Finding | Source | Verdict |
|---|---------|--------|---------|
| F1 | **4-part structure**: hook (name the problem/result <15s) → body (3-5 points) → CTA → end-screen | vidiQ | **ADOPTED**: genres pin `hook` first + `payoff+cua` last; audit now flags a tail without CTA (P3) |
| F2 | **125-150 wpm** spoken-word budget | vidiQ | **ADOPTED (honest)**: `plan_budget` reports real wpm + ideal band; gate wider (100-170) because fit_words trims — reported, never faked |
| F3 | **Two-column audio-visual script** (industry standard) | Boords/vidIQ | **ADOPTED**: `av_script.md` now ships with every make-video (VISUAL / AUDIO+SFX / words / t_start) |
| F4 | **Logline** (2-sentence essence) before any script; chain logline→synopsis→outline | Celtx/TFS | **ADOPTED**: `logline(topic, genre)` deterministic; stamped in manifest + storyboard |
| F5 | **8 genre configs** (hook_strategy/structure/CTA per video type) | Alwrity `VIDEO_TYPE_CONFIGS` | **ADOPTED**: 8 genres in `GENRES`, faceless-vertical-tuned |
| F6 | **Duration splits**: shorts 3/24/3 hook-main-CTA, scene caps, clip ranges | Alwrity `_get_duration_context` | **ADOPTED**: 4 `LENGTH_CLASSES` (shorts30/short60/medium150/long420); short60 reproduces the shipped maths EXACTLY (2.5/3.5 → 18 beats × 7 words = 126) |
| F7 | **Blueprint → research → refined blueprint → time-boxed writer** (per-section word budgets) | rahulanand1103 | **PARTIAL**: Monarch's beats are already time+word-boxed (stricter than theirs); the *research-refine* pass needs an LLM/search in the script path — ROADMAP (see below) |
| F8 | Outcome + angle before writing; study top performers' intro speed | distribution.ai | **ALREADY-HAD**: deep-forensic DNA + ideas carry evidence + freshness (W2); angle = cohort + genre hook strategy (now explicit) |
| F9 | Sluglines INT./EXT., Courier formatting, scene-numbering | Celtx/Boords | **REJECTED**: Fountain already emitted; film-slate formatting irrelevant to faceless vertical shorts |
| F10 | Character arcs/subplots/treatments | Celtx/TFS | **REJECTED (for shorts)**: 60s faceless beats have no arc budget; storytelling genre covers the narrative case |
| F11 | Show-don't-tell (visual line first) | Boords | **ALREADY-HAD**: `:: visual :: spoken` format; visual words never counted |
| F12 | Tone/language inputs (humor/facts/emotional) | rahulanand1103 | **PARTIAL**: cohort system already tunes voice; tone presets = ROADMAP with LLM writer |
| F13 | "Reuse scenes from plan to save AI calls" | Alwrity scene_builder | **ALREADY-HAD (better)**: Monarch is deterministic-zero-LLM by design — reproducibility IS the product |
| F14 | SEO description writer | rahulanand1103 | **ALREADY-HAD**: listing/pack stage + audit checklist |

## Honest gaps left open (roadmap, not hidden)

1. **Research-refine pass (F7)**: blueprint beats re-balanced from live
   evidence needs an LLM or search inside the script loop. Sandbox egress
   (github/pypi only) blocks the LLM; the DETERMINISTIC half (dossier
   evidence stamps on beats) is possible and is the natural next wave.
2. **Tone presets (F12)**: same — needs generation, not templates.
3. **End-screen planning (vidIQ part 4)**: relevant for long-form only;
   Monarch shorts end at CTA by design. Revisit if medium/long classes
   get used in production.

## Where the code lives

- `monarch/video/genres.py` — GENRES(8), LENGTH_CLASSES(4), beat_plan,
  plan_budget, logline, av_script (fail-closed, deterministic)
- `monarch/video/director.py` — `plan_storyboard(..., genre=)`, logline
  stamped; `write_storyboard_files` emits `av_script.md`
- `monarch/video/pipeline.py` — manifest carries `genre` + `logline`
- `monarch/video/audit.py` — CTA-at-tail check (vidIQ part-3 law)
- tests: `tests/test_genres.py` (10) — maths EXACTNESS included
  (short60 == shipped 18×7/2.5/3.5)

**Rule going forward:** new script features enter through this file's
verdict table first — source, verdict, reason — then code. No vibe features.
