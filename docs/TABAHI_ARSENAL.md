# 👑 TABAHI ARSENAL — THE HUNT HAUL (2026-09-28)

Operator order: hunt, study, forensic — **NO code this turn**. This is
the idea-mine haul: algorithm science, story DNA, thumbnail numbers,
sound laws, live-verified repos, strategy plays. Everything here is
RESEARCH; nothing becomes law/canon until the operator orders the
wave (HAAN gate). Sources probed live on 2026-09-28.

---

## A. ALGORITHM 2026 — THE NUMBERS (the game has changed)

**Shorts engine (fully decoupled from long-form since late 2025):**

| Signal | Number / Law |
|---|---|
| Swipe-away rate | THE master signal. Swipe-through <30% = distribution stops. >50% = strong |
| Velocity gate | ~70% "viewed vs swiped" unlocks the next test pool |
| Sweet-length band | **22–45 s** beats both extremes (retention thresholds: 65% for <30 s, 50% for 30–60 s) |
| First frame | **0.5 s** is the Shorts-critical window (long-form: first 30 s) |
| Loop rate | Genuine rewatches score; padded loops are detected (loop must be EARNED) |
| Shares | Strongest secondary signal ("viewer attaches identity") |
| Captions | Audio-pacing-aligned captions = **+15% AVD** in the 20–40 s band (170K posts, 1,100+ creators) |
| Watermarks | Platform watermarks (TikTok export) demoted pre-watch |
| Mass-produced spam | Tightened suppression — genuine repurposing OK, templated spam demoted |

**Long-form engine (May 2026 re-weighting):**

| Signal | Weight |
|---|---|
| Viewer satisfaction (surveys, returns, likes/shares) | **Very High — now #1, above raw watch time** |
| CTR (vs channel's own average; 4–8% normal, 10%+ excellent, <2% critical) | High |
| AVD/AVP (70%+ retention = priority distribution; hold 50%+ at midpoint) | High |
| Session contribution (end-session videos penalized) | Medium-High ↑ |
| New-viewer attraction | Medium (new 2026) |
| Upload consistency | Medium |
| **AI disclosure** | **Low-Medium but DANGEROUS: undisclosed AI content = suppression when detected** |
| Tags | Very low (dead) |

Monarch mapping: our audit already scores VO gate/drift/bitrate — the
MISSING measurable laws here are (1) **LUFS targeting** (§B), (2)
**22–45s band check** on shorts timing (plan already lands at 33s ✓),
(3) **AI-disclosure line in packaging** (one flag, zero cost), (4)
curve-shape diagnosis (§C3).

## B. SOUND LAW — THE LUFS STANDARD (our biggest audio gap)

YouTube normalizes playback to **-14 LUFS integrated / -1 dBTP true
peak** (loud → turned down; quiet → stays quiet). Our mix bus speaks
dBFS peaks (≤0.85, limiter 0.82) — that is a PEAK dialect, not a
LOUDNESS dialect. The pros' spec:

| Param | Target |
|---|---|
| Integrated loudness | **-14 LUFS** (dialogue-heavy: -16..-14) |
| True peak | **≤ -1 dBTP** (safety: -2..-1.5) |
| Short-term vs integrated | ≤ +6 LU swings |
| Format | 48 kHz / 24-bit master; AAC ≥ 160–320 kbps delivery |
| Verify | "Stats for nerds" Volume/Normalized readout |

**Feasibility probe (run this turn):** the imageio-ffmpeg 7.0.2
binary HAS `loudnorm` (EBU R128 normalization) AND `ebur128`
(scanner) filters → a real LUFS meter + normalizer is POSSIBLE
in-sandbox with zero new dependencies. Also spotted: `drawbox`
exists in the binary (progress-bar / plate alternative to PIL).
→ Candidate wave: measure integrated LUFS post-mix, tag `lufs_ok`,
P1 if outside -16..-12; normalize to -14 in the render chain.
(Awaiting HAAN — this turn is research-only.)

## C. STORY DNA — the new metaphors for the script layer

**C1. But/Therefore (South Park rule, Trey Parker & Matt Stone, NYU
lecture):** between EVERY two beats you must be able to say **BUT**
(conflict) or **THEREFORE** (consequence). If only "and then" fits,
the beat is dead — cut or rewrite. Chained: "X. BUT Y. THEREFORE Z.
BUT W..." = unstoppable momentum. Pixar Story Spine ("Because of
that... Until finally") is the same family. → Monarch fit: story.py
beats could carry a `connector` field (but/therefore/AND-THEN-DEAD);
a lint that flags consecutive AND-THEN beats is a pure win — the
"Camel Humps" cure below starts at the script.

**C2. Subconscious loop (MrBeast/Netflix):** never fully CLOSE an
idea before a cut — end beats on unresolved tension ("...but what
happened next was insane"). **Reconciliation with our canon:** the
Render-Memory law (complete sentences only, no `—`/`...`) bans
BROKEN TEXT, not OPEN STRUCTURE — the loop line is a complete
sentence whose MEANING stays unresolved. Both laws coexist: grammar
closed, loop open.

**C3. Retention-curve diagnostics (name the sickness):**
- **Hockey Stick** (100→10% in 5 s): hook lied; first frame didn't
  match the promise.
- **Gradual Bleed**: boring middle; fix = cut speed, b-roll, music
  changes, re-stimulation every few seconds.
- **Camel Humps**: skippable parts; open loops inconsistent — the
  viewer fast-forwards. (This is the But/Therefore failure showing
  up in the graph.)
Zones: Hook Drop (0-3 s; losing 10-20% normal, 40% = dead) / Slope
(pattern interrupts every 5-8 s) / Resurrection (end: NEVER signal
the end — no "in conclusion", cut on the last word, no fade-out for
loop integrity).
Monarch fit: our per-beat timeline could export a PREDICTED curve;
audit classifies which sickness the plan has BEFORE render.

**C4. The rest of the kit:** midway curiosity bait (the halfway
drop-off is universal — plant a re-hook at 50%), reverse-thumbnail
expectation (delay the payoff), escalation law (each segment must
out-interest the last; peak-too-early = retention death), reset
attention every 5-10 s (new visual/question/angle), pacing shift
every 3-6 s.

## D. THUMBNAIL / FIRST-FRAME SCIENCE (ranked by lift — real numbers)

| Factor | Lift | Notes |
|---|---|---|
| High contrast (≥7:1) | **+38%** (6.5% vs 4.7% CTR) | strongest single variable; win-rate 85% in A/Bs |
| Expressive face | **+33%** (6.4% vs 4.8%); some studies 20-30% | tight crop chin-to-brow ≥40% of frame = 7.6% PEAK CTR vs 4.3% full-body |
| Differentiated color (vs competitor feed, dark navy/charcoal bg) | +30% | stand OUT from feed, not "prettiest" |
| Text 0-3 words | +15% (also: <4 words = +30% clicks) | must be legible at 168 px sidebar; 70% of views are mobile |
| 3+ visual elements | **-23% CTR** | clutter kills (matches V6 M3!) |
| Placement | left-aligned face + right text | L→R scan pattern |
| Arrows/circles | moderate | 1-2 max |
| Bait-and-switch | **up to -30% demotion** | satisfaction-weighted discovery punishes trickery |

A/B protocol: 3 variants (safe / bold / wildcard), one variable at a
time, 7 days or 2,500 impressions, **watch-time share wins — not raw
CTR**; YouTube's built-in "Test & Compare" confirms. AI workflow:
score 5-10 variants against heuristics (contrast/face/text/emotion/
curiosity) BEFORE publishing → predict, then confirm. (This is
exactly the W-B1 forecaster idea — now with heuristic numbers.)
First frame of a Short IS the thumbnail (V6 M-canon ✓ — these
numbers give the auditor measurable checks).

## E. REPOS — LIVE-VERIFIED (idea-mine only; NEVER dependencies)

| Repo | ★ / upd | What to mine |
|---|---|---|
| Anil-matcha/AI-Youtube-Shorts-Generator | 5,158 / live | ALREADY VENDORED ✓ |
| Dark2C/Viral-Faceless-Shorts-Generator | 112 / 9-25 | ALREADY VENDORED ✓ (piper + speechalign refs) |
| zackmawaldi/YouTube-shorts-generator | 379 / 9-22 | reddit→edit→**auto-UPLOAD** pipeline shape; the upload-automation pattern (ours is HAAN-gated by law) |
| leamsigc/ShortsGenerator | 353 / 9-27 | local-first shorts automation; stage decomposition worth a read |
| SaarD00/AI-Youtube-Shorts-Generator | 229 / 9-28 | "infinite content, zero manual editing" faceless factory; scheduling/queue concepts |
| Shaarav4795/ClippedAI | 211 / 9-27 | OpusClip-alternative clipping heuristics (long→shorts moment-picking) |
| KrishPatel1404/reddit-story-video-gen | 19 / 8-07 | RSCG story-format pipeline (small but same DNA) |
| stanyanman/VAbk-Studio | 0 / 6-20 | books→**word-synced karaoke-caption** videos — exact W-A2 concept match |
| ruashots/ComfyUI-OpenH3-IR | 25 / 8-23 | **Context-IR brief schema** for MiniMax H3 video-gen: @-named media refs, @speaks() exact-dialogue lock, Director-as-direction-object, declared error-code taxonomy — the FREE schema for our parked gen layer (finding #131) |
| (tools, not repos) Reap / Vozo | SaaS | 1 long → 5-15 captioned shorts + 80-100-language dubbing + scheduling via CLI/API/MCP — the *distribution layer* pattern |

Verdict: none of these replace Monarch (ours is the only one with
LAW GATES + audit + in-sandbox HAAN rail); the mine-able ideas are
clipping heuristics (ClippedAI), karaoke sync (VAbk), and
queue/schedule concepts (SaarD00, zackmawaldi).

## F. STRATEGY PLAYS (channel-level tabahi)

1. **Repurposing math (highest leverage):** 1 long → **5-15
   captioned Shorts** + dubbed tracks = be-everywhere without
   triggering mass-production suppression. Cadence benchmark:
   1-2 long + 15-30 Shorts/month.
2. **Auto-dubbing is FREE reach now:** rolled out to all eligible
   creators (early 2026), **27 languages**, Gemini-powered. Play:
   enable free auto-dub → 2-4 weeks → read analytics by
   country/audio-language → replace winning languages with custom
   tracks + **translated title/description** (auto-dub can't do
   metadata; custom = foreign SEO unlock; delete auto-dub before
   custom upload). 1-2 languages first (Spanish, PT-BR, **Hindi**,
   German, French). Reported 3x growth cases; one channel-multi-
   track is the 2026 default. Zero extra render work for Monarch —
   it happens on YouTube's side post-upload.
3. **Shorts = top-of-funnel, long-form = money** (RPM higher): a
   case study: Shorts-first growth → engaged views +41.8%, revenue
   +64.1%, long-form captured most revenue.
4. **Series/universe formats get algorithmic reward** (vidiq 2026);
   Monarch's GENRES could graduate into named series with recurring
   hook grammar (brand DNA).
5. **Hype** expanded to channels <500k subs (2026) — early-mover
   boost surface for small channels.
6. **AI disclosure line** in every description = suppression-proof.

## G. WAVE MAPPING (what the hunt feeds — awaiting HAAN, no code now)

| Hunt item | Feeds wave | New measurable laws it would add |
|---|---|---|
| LUFS + loudnorm/ebur128 present | W-B (audio law) | `lufs_ok` (-16..-12), true peak ≤ -1 dBTP, P1 outside |
| But/Therefore lint | W-B (script science) | consecutive AND-THEN beats = P2; connector field |
| Curve-shape diagnostics | W-B1 forecaster | predicted curve + sickness classification |
| Thumbnail numbers (contrast ≥7:1, tight-crop face, ≤3 words) | W-A1 overlay + audit | contrast/element-count checks on first frame |
| AI-disclosure line | packaging emitter | one description line, zero cost |
| 22-45s band | already ✓ (33.25s) | add explicit band check to shorts audit |
| Karaoke concept (VAbk) | W-A2 | word-synced captions = the +15% AVD lever |
| Clipping heuristics (ClippedAI) | long→shorts multiplier | moment-picking scorer |
| Auto-dub strategy | ops playbook (docs) | post-upload, no pipeline change |

## H. HONEST CONFLICTS / NOTES

- **Subconscious-loop vs complete-sentences:** reconciled in C2 —
  grammar closed, loop open. No canon change needed; it's a
  STRUCTURE law, not a TEXT law.
- Auto-dub rollout dates vary by source (Feb vs Apr 2026); treat as
  "early 2026, all eligible creators, 27 languages".
- Thumbnail numbers come from creator-side studies (vidiq/1of10/
  CTRpilot aggregations), not YouTube-official — directionally
  solid, magnitudes vary.
- Sweep found NO new egress unlocks: hf.co/bing/etc stay blocked;
  LUFS/ebur128/drawbox are LOCAL (this is why they matter).

**Bottom line:** the arsenal's sharpest new blades = **LUFS law
(feasible today), But/Therefore beat lint, curve-shape forecaster,
thumbnail-contrast numbers, auto-dub free reach, AI-disclosure
shield.** Say the word and they graduate from research to canon.
💀👑📈
