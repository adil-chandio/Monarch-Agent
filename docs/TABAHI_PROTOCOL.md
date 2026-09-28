# 👑 MONARCH TABAAHI PROTOCOL — THE MAX PIPELINE V1 (2026-09-28)

The integrated structure the operator ordered: EVERY weapon from the
four hunt layers (TABAAHI_ARSENAL, CHAOS_LAYER, ABYSS_LAYER,
TOOFAN_LAYER) mapped into ONE workflow, perfectly, with nothing left
out. Each stage lists: Laws (source-traced), Gates, Outputs, and its
Wave assignment. Feasibility is honest (probed 2026-09-28): what
runs in-sandbox TODAY vs what waits (HAAN/egress).

Design constitution (unchanged): every measurable law is enforced by
code + test, never by memory; every upload passes the HAAN gate;
honest ran-vs-blocked reporting; tests green → commit → push → PR
comment per wave.

---

## THE PIPELINE (11 stages, one topic in → deliverable + learning out)

```
P0 IDEA HUNT ─→ P1 RESEARCH ─→ P2 SCRIPT (story DNA) ─→ P3 PACKAGING-FIRST
     ↑                                                     │
     │                                                     ▼
 P10 LEARN ←─ P9 POST-LAUNCH ←─ P8 UPLOAD RAIL ←─ P7 AUDIT ←─ P6 RENDER
                 ↑                                      ↑
                 └────── P4 VOICE ── P5 SOUND ── P6 ────┘
```

---

### P0 — IDEA HUNT (outlier-driven, not mood-driven)
**Laws:** outliers are videos beating their OWN channel's average
10–100x; 70% of views come from Homepage not Search; small-channel
outliers are signal, big-channel outliers are noise; format cloning
is worthless (1,100x spread) — extract the INSIGHT, add the
invisible layer (persona/taste). (CHAOS §3)
**Gates:** existing `gate-idea` + hunt pipeline. NEW scoring axes:
topic-gap calibration (TOOFAN §1 — is there a MEDIUM gap here, or
too large/too small?), curiosity-payload check (does the topic OPEN
a gap the payoff can exceed?).
**Outputs:** vetted topic + its calibrated gap statement (one
sentence: "they know X, they don't know Y").
**Feasibility:** hunt/search commands exist; scoring axes = W-B wave.

### P1 — RESEARCH (facts that survive)
**Laws:** SCRIPT FORENSICS canon (already wired); no unverifiable
claims in VO (L-law class); AI-disclosure preparedness — sources
logged so the disclosure line is honest. (ARSENAL §F6, CHAOS §2)
**Outputs:** fact sheet + WTF-detail shortlist (the comment-bait
minerals: "99% bamboo, 20cm tongue").
**Feasibility:** running code today (intel + ingest + ytt).

### P2 — SCRIPT (the story-DNA stage)
**Laws (all four layers converge here):**
1. **But/Therefore** between every beat pair — a beat only joined by
   "and then" is DEAD, cut or rewrite. (ARSENAL C1)
2. **Harmon mini-circle** on the arc: hook fuses YOU+NEED → GO →
   SEARCH/FIND body → **TAKE (the price = the PEAK)** → RETURN+CHANGE
   (payoff). (TOOFAN §2)
3. **Crazy progression**: compress, don't serialize (day 1 of 30 is
   banned — front-load the journey). (CHAOS §1)
4. **Subconscious loops WITH closed grammar**: every sentence
   complete (Render-Memory law), meanings left OPEN between beats.
   (ARSENAL C2 — reconciled)
5. **Micro-RPE pacing**: every 5–10s a new visual/question/angle;
   pacing shifts every 3–6s; exactly ONE scheduled PEAK. (TOOFAN §1,
   CHAOS §1, ABYSS B)
6. Shorts: condensed-INCOMPLETE plan via `long_to_short()` (60/25/12,
   #1 censored) — the Zeigarnik structure is itself the hook. (V6)
7. Escalation law: each segment must out-interest the previous; peak
   too early = death sentence on the script. (ARSENAL C4)
**Gates:** fountain/neuro gates + NEW `but-therefore lint`
(consecutive AND-THEN = P2), `peak-scheduled check`, `escalation
check`. Long-form: chunk planner (`plan_chunks`, ≤46 beats, no topic
split) stays mandatory for 9:39-class. (V2 R-law)
**Outputs:** beat board with connector tags, peak placement, loop
design, gap statement → SRT-ready VO text.
**Feasibility:** structure exists (story/fountain/genres); lints =
W-B wave.

### P3 — PACKAGING-FIRST (title/thumbnail BEFORE render — the 13ms
truth: most viewers decide from packaging, so packaging is designed
first and the video must MATCH it)
**Laws:**
1. Title: Shorts 22–35 (ideal 24–27) chars via `title_check()`;
   long-form 18–60 scorer; identity-attack curiosity grammar; emoji
   end only. (V6 M14, ARSENAL A)
2. Promise-congruence: title+thumb set the EXPECTATION the payoff
   must EXCEED (RPE law). A mismatch is a negative prediction error
   = neural dissatisfaction + bait-and-switch demotion (−30%).
   (TOOFAN §1, ARSENAL D, CHAOS §2)
3. First-frame = thumbnail (Shorts): design the SHOCK frame as the
   packaging twin. Numbers: contrast ≥7:1 (+38%), expressive face
   +33% (tight crop chin-to-brow ≥40% = 7.6% peak), 0–3 words,
   ≤2 elements, left-face/right-text, NO watermarks, bait = death.
   (ARSENAL D)
4. A/B discipline: 3 variants (safe/bold/wildcard), one variable at
   a time, watch-time share wins — Shorts-first thumbnail testing.
   (ARSENAL D)
5. **Gaze intent on the thumbnail**: connection mode (eyes to
   camera) vs pointer mode (eyes at the payoff object) — chosen,
   never random. (ABYSS C)
6. AI-disclosure line drafted for the description (survival shield,
   3-strike ladder). (CHAOS §2)
**Gates:** `gate-title` + `title_check` + NEW `congruence gate`
(expectation-vs-payoff plan recorded before VO).
**Outputs:** title, thumbnail/first-frame spec, description draft,
pinned-comment draft, disclosure line.
**Feasibility:** gates exist; thumbnail scoring heuristics = W-B.

### P4 — VOICE (audio-first, the human-class bar)
**Laws:** sentence chunks + lead-in/tail + crossfade (wired);
VO-lint (no `—`/`...`, complete sentences) wired; duration MEASURED
never assumed (`beats_for_vo`: video = VO + 0.5 + 0.2) wired;
calm-doctor tone, second person, reverb accents (V6); bitrate floor
72k, target 160k (V2). NEW from hunts: commentary/VO ≥30% of
runtime (survival tripwire); word-level timing emitted at synth
time (karaoke enabler — F5 solution); persona consistency (same
voice character across videos = the "named narrator" anti-slop
armor). (ARSENAL B, CHAOS §2, forensic F5)
**Outputs:** VO wav + word-timing json + measured duration + VO QC
report.
**Feasibility:** mumble synth pipeline live; word timing + ≥30%
check = W-A2/W-B.

### P5 — SOUND (the mix + the unclaimed cortex)
**Laws (wired):** five-layer bus, duck ≤0.32, limiter, warm beds,
buildup mood (no 0.7s kicks — 1.4s heartbeat proven), SFX ≤1 per
cue, per-channel peak ≤0.85, crescendo at edges. NEW laws from
hunts:
1. **LUFS law**: master −14 LUFS integrated (speech −16..−14), true
   peak ≤ −1 dBTP, short-term swings ≤ +6 LU; `loudnorm`/`ebur128`
   verified present in our ffmpeg binary → render-side normalize +
   `lufs_ok` audit field. (ARSENAL B — PROBED FEASIBLE)
2. **Sonic logo**: deterministic numpy signature — intro sting
   (primacy) + outro resolve (recency), sample-identical EVERY
   render (mere exposure → familiarity → trust; 6-tone +16% study).
   Dual-cortex brand: stickman (visual) + logo (auditory). (TOOFAN §3)
3. Audio drives story (Beast's own lever) — mood map per genre
   already wired; keep escalation-aligned music intensity.
**Outputs:** mixed master (LUFS-tagged) + sonic-logo stems.
**Feasibility:** mix bus live; LUFS = W-B (probed ready); sonic
logo = W-A/W-B (pure synth, no deps).

### P6 — VISUALS + RENDER (canon becomes pixels)
**Laws (wired):** 1080×1920@30, zoom clamp ≤1.08 (Motion.__post_init__,
forensic F1), safe zones 384–1536 / subject 500–1400, one-focal
images, no-text prompts, image count == beats, 2.8–3.3s beats,
boundary whoosh+riser on chunk merges, drift ≤ small ms, captions
burned, progress + karaoke preparation. NEW:
1. **TEXT_SYNCED burn** (y 320/1450 never 750, 6 animations ≤2
   repeat, 2–3 words, show 1.7s/fade 0.3s) — plan exists in
   shorts.py; the render pass is W-A1.
2. **Karaoke captions** from P4 word timing (+15% AVD evidence).
   (ARSENAL A — W-A2)
3. **End-screen engineering**: last 7s, right 40%, gold, WATCH HERE;
   loop end-frame == start-frame; NO end signal, cut on the last
   word; abrupt payoff (peak-end + curve doctrine). (ABYSS B,
   ARSENAL C3 — W-A1)
4. **Gaze direction per beat**: hook frames eyes→camera,
   explanation frames eyes→object. (ABYSS C — W-A1 stickman poses)
5. **Von Restorff guard**: black void stays EMPTY around the
   stickman — isolation = memorability. (TOOFAN §4)
6. Stickman = the channel's face: consistent character every render,
   signature opening pose (face-bias counter-strategy). (CHAOS §4)
7. 22–45s band check on Shorts timing (33.25s default ✓); loop must
   be EARNED (genuine-rewatch structure, not padded). (ARSENAL A)
**Outputs:** render mp4 + timeline.json (now also motion/gaze fields)
+ first-frame PNG (the thumbnail twin).
**Feasibility:** core live; overlay/karaoke/end-screen/gaze fields =
W-A1/A2 waves (drawtext absent, PIL/numpy route chosen).

### P7 — AUDIT (the Eye — from the FILE, not intentions)
**Laws (wired):** measured `_wav_stats`, VO-gate windows, duplicate
frames, tick edges, bitrate floor, 0–100 score. NEW checks (wave
W-B unless noted):
1. **Chain check (the 9 links)**: promise→click→0.5s-gate→engaged→
   loops→PEAK→END→loop→satisfaction — each link verified from plan +
   file; one weak link = named fix. (ABYSS D)
2. **Curve-shape forecast**: classify Hockey Stick / Gradual Bleed /
   Camel Humps risk from beat data pre-render. (ARSENAL C3)
3. **LUFS measured** (post-P5: `lufs_ok` ±band) + true peak. (W-B,
   probed)
4. **Slop-audit** (doctor): template-distance across last N renders,
   persona presence, disclosure line, cadence sanity, ≥30% commentary.
   (CHAOS §2)
5. Zoom clamp audit (already test-pinned F1); text-position audit
   (never y=750) once burn lands.
**Outputs:** priority-ordered fix report (P1/P2) — FAIL blocks upload.
**Feasibility:** audit skeleton live; chain/curve/slop = W-B.

### P8 — UPLOAD RAIL (the HAAN-gated gofile step)
**Laws (wired):** explicit operator order only; deliverables branch,
sha256 in the commit message, tip-diet, >90MB fail-closed → chunk
splits first; link + checksum to operator. Additions: the upload
bundle now carries the PACKAGING KIT (title/description/pinned/
disclosure/srt/thumbnail) so launch is one paste. (V6 M13; ARSENAL F)
**Outputs:** raw link + sha256 + kit folder.

### P9 — POST-LAUNCH (the side most factories ignore)
**Laws:**
1. Engaged-vs-public split discipline: compare engaged-to-engaged;
   sponsor/perf reports quote ENGAGED views; "views up / RPM down"
   after Aug-24-2026 = definition, not growth. (ABYSS A)
2. Vitals that matter: swipe-through (>50% strong / <30% dead),
   viewed-vs-swiped ~70% gate, engaged rate, AVP, RETURNING-viewers
   ratio (the satisfaction proxy). (ARSENAL A, ABYSS A, TOOFAN §4)
3. Auto-dub playbook (free reach): enable → 2–4 weeks → read
   per-country/audio-language analytics → custom tracks + translated
   metadata for winners (Hindi first) — post-upload, zero pipeline
   cost. (ARSENAL F)
4. Session chaining: parts/callbacks/playlists hand the viewer to
   the next video (session contribution ↑). (TOOFAN §4)
5. A/B reads feed P0 (Shorts-first thumbnail testing). (ARSENAL D)
6. Repurposing: 1 long → 5–15 captioned Shorts, cadence 1–2 long +
   15–30 Shorts/mo — variation in TOPIC, consistency in GRAMMAR
   (anti-slop balance). (ARSENAL F, TOOFAN §4)
**Outputs:** performance sheet (engaged-class numbers only) →
learning entries.

### P10 — LEARN (the flywheel)
**Laws (wired bones):** memory/learn/lessons systems; never-again
canon. Additions (W-B): audit-trend tracking (regression = gate
fail), outlier re-scan feeding P0, sonar of format changes (hooks
that fatigued), sonic-logo/palette never drift (consistency law).
**Outputs:** updated lessons + next-topic shortlist.

---

## WEAPONS-COVERAGE MATRIX (nothing left out — sweep proof)

| # | Weapon (source) | Stage | Wave | Status |
|---|---|---|---|---|
| 1 | Swipe gates 30/50/70% (ARS-A) | P9 vitals + P6 band | W-B | planned |
| 2 | 22–45s band (ARS-A) | P6 | W-B check | band ✓ by design |
| 3 | 0.5s first frame (ARS-A, OUT-A) | P3/P6 | W-A1 | planned |
| 4 | Captions +15% AVD / karaoke (ARS-A) | P4/P6 | **W-A2** | planned |
| 5 | Watermark ban (ARS-A) | P3/P6 | law | standing |
| 6 | LUFS −14/−1dBTP + loudnorm/ebur128 (ARS-B) | P5/P7 | **W-B** | probed ready |
| 7 | But/Therefore lint (ARS-C1) | P2 | **W-B** | planned |
| 8 | Subconscious loop, grammar closed (ARS-C2) | P2 | law | standing |
| 9 | Curve sickness taxonomy (ARS-C3) | P7 | W-B | planned |
| 10 | No-end-signal / cut on last word (ARS-C3) | P6 | W-A1 | planned |
| 11 | Midway bait, escalation, reset 5–10s, pacing 3–6s (ARS-C4) | P2 | W-B | planned |
| 12 | Thumbnail numbers table (ARS-D) | P3 | W-B scoring | planned |
| 13 | A/B 3-variant protocol (ARS-D) | P3/P9 | ops | standing |
| 14 | Clipping heuristics (ARS-E) | P0/P9 | W-B idea | parked-idea |
| 15 | Karaoke concept repo (ARS-E) | P6 | W-A2 | merged w/ #4 |
| 16 | Queue/schedule concepts (ARS-E) | P9 | ops | parked-idea |
| 17 | 1→5-15 repurposing + cadence (ARS-F) | P9 | ops | standing |
| 18 | Auto-dub 27-lang playbook (ARS-F) | P9 | ops | standing |
| 19 | Shorts funnel → long money (ARS-F) | P9 | strategy | standing |
| 20 | Series/universe formats (ARS-F) | P2/P9 | strategy | standing |
| 21 | Hype surface (ARS-F) | P9 | ops note | standing |
| 22 | AI disclosure (ARS-F6, CHAOS-2) | P3/P8 | W-B kit | planned |
| 23 | Beast 3 gods CTR/AVD/AVP (CH-1) | P7/P9 | law | standing |
| 24 | First-minute doctrine + lighting insight (CH-1) | P2/P6 | W-A1 | planned |
| 25 | Crazy progression (CH-1) | P2 | W-B lint | planned |
| 26 | 3-min re-engagement / mid-bait (CH-1) | P2 | W-B | planned |
| 27 | Abrupt payoff ending (CH-1) | P6 | W-A1 | planned |
| 28 | Wow factor / innovate / audio-story (CH-1) | P2/P5 | doctrine | standing |
| 29 | Brand-deal integration (CH-1) | P3 | far-future | parked |
| 30 | Slop tripwires <30%, 5×20%, cadence (CH-2) | P7 doctor | **W-B** | planned |
| 31 | 3-strike disclosure shield (CH-2) | P3/P8 | kit | w/ #22 |
| 32 | Anti-slop armor mapping (CH-2) | ALL | standing | live |
| 33 | Outlier method 10–100x, homepage 70% (CH-3) | P0 | W-B | planned |
| 34 | 1,100x invisible-layer doctrine (CH-3) | ALL | doctrine | standing |
| 35 | Stickman = the face (CH-4) | P6 brand | W-A1 pose | planned |
| 36 | Engaged/public split 1.67x (AB-A) | P9 | W-B report | planned |
| 37 | Peak-end: one PEAK + engineered END (AB-B) | P2/P6 | W-A1/W-B | planned |
| 38 | Gaze physics camera/object (AB-C) | P3/P6 | W-A1 | planned |
| 39 | 9-link chain check (AB-D) | P7 | **W-B1 core** | planned |
| 40 | RPE: medium-gap hook + payoff EXCEEDS (TF-1) | P0/P2/P7 | W-B | planned |
| 41 | Micro-RPE beats (TF-1) | P2 | W-B | w/ #11 |
| 42 | Harmon circle mapping (TF-2) | P2 | W-B lint | planned |
| 43 | Sonic logo numpy (TF-3) | P5 | **W-A/W-B** | planned |
| 44 | Von Restorff void guard (TF-4) | P6 | audit | w/ #35 |
| 45 | Returning-viewers vital (TF-4) | P9 | W-B | planned |
| 46 | Session chaining (TF-4) | P9 | kit | planned |
| 47 | Format mere-exposure, topic-variant (TF-4) | P2/P9 | doctrine | standing |
| 48 | Zoom ≤1.08 clamp (forensic F1) | P6 | **DONE** | shipped 8d117e6 |
| 49 | CI ready-to-enable (forensic F3) | meta | operator web-add | ready |
| 50 | Upload rail + HAAN + sha256 (existing) | P8 | **DONE** | live |

Standing chassis (already shipped, in service): 8 GENRES × 4 LENGTHS,
budgets, chunk planner + concat bridge, five-layer mix + buildup,
crescendo edges, audit 0–100, doctor/memory/learn, V6 planner set,
deliverables rail. Every hunt item above is additive to it — nothing
replaces the wired core.

---

## WAVE EXECUTION ORDER (acceptance criteria per wave)

> **STATUS 2026-09-28: W-A1 ✅ DONE, W-A2 ✅ DONE, W-B1 ✅ DONE, W-B2 ✅ DONE** (shipped in one push).
> Live evidence: `v6 layer burned (karaoke words + progress bar + loop tail +
> end screen)`; render measures **-14.3 LUFS** (target -14, in band); sonic
> logo sting@0.0 + resolve@end in the master (never ducked); audit 94/100.
> Modules: `monarch/video/overlays.py` (ASS/libass route, ZERO new deps),
> `audio.sonic_logo/sonic_resolve`, `mix(sonic=)`, `render.loudnorm +
> measure_lufs`, `pipeline` v6.ass+v6_plan.json emitters, audit LUFS finding,
> CLI `--with-sonic --v6-end-screen`. Tests +13 (443 total).

- **W-A1 — RENDER THE CANON (pixels):** overlay pass (TEXT_SYNCED
  burn, end-screen, progress bar, no-end-signal cut, loop frame,
  gaze-pose fields in board) → tests: position laws, animation laws,
  end-screen geometry, first-frame export. DONE = V6 planned-layers
  all visible in a rendered file.
- **W-A2 — WORD TIMING + KARAOKE:** synth-time word map → karaoke
  burn + SRT export → tests: monotonic times, coverage, sync
  tolerance. DONE = captions land on spoken words in a live render.
- **W-B1 — CHAIN CHECK + CURVE FORECAST:** ✅ **DONE** —
  `monarch/video/forecast.py`: the 9-link gate names every weak link
  (bad plan fails with SEVEN links named + hockey_stick curve in
  tests), But/Therefore lint (explicit connectors OR cue/driver
  inference - the engine's own N4 VALUE-DEBT marker counts), curve
  verdicts (healthy/hockey_stick/gradual_bleed/camel_humps/
  peak_too_early), CLI `monarch forecast DIR [--title --shorts
  --end-screen --loop --disclosure]` with rc 2 + the broken link
  printed. Live: probe board = CHAIN 9/9 + healthy, cleared for
  render. Tests +12 (455 total).
- **W-B2 — SOUND SCIENCE:** LUFS measure/normalize (`lufs_ok`),
  true-peak check, sonic-logo synth + placement laws. DONE = master
  tagged −14±1 LUFS on a live render + logo audible in every render.
- **W-B3 — SURVIVAL + PACKAGING KIT:** slop-audit (template-distance,
  persona, disclosure, cadence, ≥30%) + one-shot kit emitter
  (title/desc/pinned/srt/thumb/disclosure). DONE = doctor flags a
  synthetic template-cluster + kit completes an upload bundle.
- **W-B4 — PERFORMANCE/VITALS:** engaged-class reporting template +
  returning-viewers vital + repurposing queue skeleton. DONE =
  post-launch sheet generated from a real upload's metadata shape.
- **W-C — PARKED (egress):** neural VO, whisper align, image-gen,
  publish API, mirror host. Unchanged verdicts.

Sequencing rule: each wave = tests green → commit → push → PR
comment; no wave starts on a red suite; W-A1 first unless the
operator reorders. 💀👑
