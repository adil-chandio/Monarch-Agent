# MONARCH V2 POST-MORTEM — "Every Bear RANKED" session (2026-09-25→27)

Operator's full post-mortem, absorbed 2026-09-27. 2 days, 100+ renders,
172 beats, 9:39 master, 1920x1080@24, stickman line-art, 5-chunk
incremental render. Every miss below is PAID FOR — L16 applies: a
repeat = auto-fail. Dual-canon with RENDER_MEMORY.md (Einstein session)
and PRODUCTION_LAW_V2.md (G1–G16).

**Adoption verdicts — adopted live (suite-tested), already-had, or
rejected with reason. Nothing adopted on vibes.**

## Miss → verdict table

| # | Miss (root cause) | Fix shipped in session | Monarch verdict |
|---|---|---|---|
| 1 | **32k bitrate bug** — final merge `-b:a 32k`, VO robotic (space saving > quality) | `-c:a copy` or ≥160k | **ADOPTED ⚙**: render.py now verifies the ACTUAL file bitrate post-render (`audio_kbps`, `bitrate_ok`); audit P1 on any mp4 in the starvation class (< 72k measured — the banned 32k/48k/64k band). ENCODE TARGET stays copy/160k/192k always; the measured floor is 72k because sparse mono content measures below its target (live: 160k target → 95k measured on mono 24k mumble VO). Law: NEVER 32k/48k/64k — copy or 160k/192k |
| 2 | **Irritating beep at intro** — `s_tick` 0.07s harsh click at beat 8 for "FOMO" | `s_tick → s_crescendo` (1.8s smooth sweep 80→520Hz + rumble) | **ADOPTED ⚙**: `sfx_crescendo` registered in SFX_KINDS; mix.py auto-swaps tick→crescendo on intro/outro scenes with a warning; audit P2 on tick at edges. Law: NEVER harsh tick at intro/outro |
| 3 | **VO too quiet, BG too loud** — VO 0.92, BG 0.09, duck 0.48, harsh limiter | VO 1.15, BG 0.06, duck 0.32, gentle limiter | **ADOPTED (constants recorded)**: our mix already enforces the intent (VO gate, music ducked, peak band 0.72–0.82 from Einstein law). Duck-to ~32–40% + VO-loudest recorded as THE reference values for the long-form/master path |
| 4 | **REPETITION BUG (CRITICAL)** — Sun bear split 28–36/37–46 across chunks → story re-told itself at every seam | Clean bear boundaries: every chunk starts a NEW topic, ends a COMPLETE topic; gap 0.38→0.85s; whoosh+riser at every boundary | **ADOPTED ⚙**: `monarch/video/chunks.py` — `plan_chunks()` groups COMPLETE topics into ≤46-beat chunks, fail-closed if a topic would split; `verify_no_split()` proves every topic lives in exactly one chunk; boundary = gap 0.85s + whoosh+riser |
| 5 | **Same image for an entire chunk** — beats 145–172 reused 1 fallback image each (per-beat images missing, rushed) | 28 unique stickman images (10 AI + 18 PIL), BEAT_IMG unique per beat | **ADOPTED ⚙**: audit reads timeline.json — duplicate frame slots = P2 with the fix path (AI 10/turn + PIL fill, `monarch budget` plans). Law: unique image per beat, verify count == beats BEFORE render |
| 6 | **Image limit 10/turn** — 28 needed, 10 generated, mid-batch error | AI first 10 + PIL code for the rest (unlimited), consistent style | **ALREADY-HAD ⚙**: `monarch budget` (G3/L10) plans batches; priority rule ADOPTED in canon: style anchor + highest-emotion scenes FIRST so a cap-hit never blocks the story |

## Golden rules (R1–R6) → Monarch mapping

- **R1 audio (VO is king)** — VO 1.15x loudest, BG ≤0.06x, duck ≤0.32, gentle limiter, SFX 1.0x, bitrate copy/160k+. Mapped: VO gate + peak band (render-memory), bitrate verify (new), constants recorded for the master path.
- **R2 chunk structure** — `chunks.py` (new). NEVER split a topic; chunks start NEW topic; gap 0.85s; whoosh+riser at boundaries.
- **R3 visuals** — unique image per beat; stickman minimalist white-bg black-lines; text overlays keywords NOT verbatim captions; ONE font (DejaVu Sans Bold in-repo); motion eased NOT linear; vignette+grain+progress bar. Mapped: audit unique-frames; craft spec = canon for the animation layer.
- **R4 image pipeline** — check missing → AI 5-at-a-time → PIL fill → verify count == beats → update map → THEN render. Mapped: `monarch budget` + audit verification; order recorded in canon.
- **R5 incremental merge** — workspace cap ~128MB evicts largest first; ONE bash loop: render chunk → delete raw → concat copy to growing master → delete prev. Mapped: our workspace-diet laws (render tests unlink outputs); pattern recorded verbatim for long-form renders.
- **R6 QC before delivery** — duration/resolution/audio-bitrate/no-boundary-repetition/unique-images/no-intro-beep/keywords-not-verbatim/eased-motion. Mapped: audit checks (drift, bitrate, unique frames, tick edges) + the checklists below.

## Checklists (operator-verified from the session)

PRE-RENDER: beats listed · topics grouped with ranges · chunks clean-boundary · per-beat images exist · BEAT_IMG unique · no tick at intro/outro · text keywords · motion eased.
RENDER: W/H/FPS/SR set · VO 1.15 / BG 0.06 / duck 0.32 / gentle limiter · GAP 0.85s · incremental merge · intermediates deleted immediately.
POST-RENDER: duration matches · resolution correct · AAC 160k+ VO loud · no repetition at boundaries · unique images verified · upload + link + specs.

## Honest gaps (recorded, not hidden)

1. **Landscape 1920x1080** was this session's format — Monarch defaults
   1080x1920 vertical; both supported via make-video --width/--height.
   Long-form (9:39) chunked rendering pipeline itself is the next wave
   (chunks.py is its planner).
2. **gofile.io upload** is operator-side (upload stays HAAN-gated;
   sandbox egress is github/pypi only).
3. **Per-beat AI images at scale** (172 beats) need multi-turn budgeting
   (budget command) + PIL fallback generation — the PIL stickman generator
   is craft-layer, recorded here, built when the long-form wave opens.
