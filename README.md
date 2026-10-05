# Monarch

Faceless YouTube OS for **Arena Agent Mode**.  
**Created by Adil Chandio** | Contact: [workadilchandio@gmail.com](mailto:workadilchandio@gmail.com)

---

## 🔒 Security & Access Activation

Monarch Agent is protected with a private activation key. If anyone clones or runs Monarch without activation, access is denied with:

> *"Me Monarch Agent muje Adil chandio ne banaya ha to apko mujhe access run Karne ke Liye key chaiye Yahan chat me key dalen Aage key NAHI ha to apko mere boss se milegi unka contact Gmail: workadilchandio@gmail.com"*

### How to Unlock / Activate:
```bash
# 1. Via CLI activation command:
monarch activate DoitMon@rch

# 2. Or set environment variable:
export MONARCH_ACCESS_KEY="DoitMon@rch"

# 3. Or pass inline with any command:
monarch --key DoitMon@rch status
```

---

## Start

### Agent workflow (natural-language)

After the existing access check, say `monarch activate`. The agent first asks one question in
simple Roman Urdu and waits:

> Kaunsa workflow chalana hai?
>
> 1. **Monarch Cam** — wildlife channel ka workflow
> 2. **Monarch Activate 💀** — pehle wala overall Monarch Agent workflow

Choose **Monarch Cam** to load its channel world, or **Monarch Activate 💀** for the original
overall workflow. The overall workflow still begins with its four intake questions. Direct
shortcuts: `monarch cam activate` for Cam; `monarch activate 💀` for the overall workflow.
Do not start repository setup/dependency installation as part of this workflow choice.

### Cam entry — ask, then wait

After access is verified and Cam is selected, the agent asks three things in simple Roman Urdu
and waits: **topic · ratio · length**. The bear/door brief in
`monarch/worlds/monarch-cam/assignments/` is provisional — it is not a chosen topic. If you ask for ideas instead, you get **10 ideas** and the agent waits for
your pick. The agent never chooses topic, ratio, or length itself, and Stages 1–6 research lands
in one `output/<slug>/project_notes.md` (per-stage sections, not six separate reports).

### Laws that always apply

- Access key check first; the key is never repeated in any reply.
- Easy Roman Urdu (Urdu–English mix) replies only; milestone updates max 5 bullets; results chat
  mein bhi. Sirf final deliverables (script, captions, titles) English mein.
- **Per-stage permission:** har stage ke baad chhota update + `Aage barhoon?` → WAIT. Bina ijaazat
  next stage/file/tool nahi, aur khud se koi choice (topic, ratio, length, idea, scene, script,
  voice, title) pick nahi.
- **Cam skill integration:** use the existing stage-mapped skill/role cards in `WORLD.md` §2A
  just-in-time; `make-short` previz is not the final real-footage video.
- **COMPLETE THE WORK — NEVER REFUSE EDITING:** Keep moving through lawful alternatives to a
  QC-checked rendered MP4; never stop at a plan or `BLOCKED`. Required approvals, rights, safety,
  and publishing gates still apply.
- No big paragraphs, long dumps, tool logs, duplicate/scratch files, or separate licence-request files.
- No clip score, shortlist, or review claim without visual inspection (`NOT SCORED` if it cannot
  be viewed; try another permitted candidate, then ask once for an accessible upload/source).
  No scene-specific script/VO/EDL for unseen footage; EDL source times must be verified and `TBD`
  is never a complete edit.
- `RIGHTS UNKNOWN` is written honestly; analysis/planning may continue, but no clearance claim,
  and no vendor contact, licence request, or payment without explicit authorization.
- **“Aage barho” / “continue”** approves only the current creative gate — not missing intake,
  unchosen options, rights approval, vendor contact, or publication permission — and never sets
  `OPERATOR APPROVED WITH RISK NOTED` (named risk + explicit acknowledgement required).
- Ask only the current stage's question; destination URL, editor, VO, and disclosure are not
  Gate A questions, and a missing destination URL is not an early blocker.
- `monarch render` produces a **previz**, not the final MP4 from imported wildlife footage. The
  agent says this limitation first, in one short line, before any final-video promise.

Full law: `BOOT.md` · `AGENT.md` · `monarch/worlds/README.md`

### Terminal CLI

`monarch activate <key>` is a separate CLI command for unlocking the local agent; it does not
show the natural-language workflow selector. This selector applies when talking to the agent.

```
python -m monarch status
python -m monarch maths --seconds 60
```

## M3 script in Fountain

Write the script as a `.fountain` screenplay, gate it into numbered scenes:

```
monarch m3
monarch screen-script script.fountain --length short --board-out board.json
monarch script-fountain board.json --out approved.fountain
```

Words per clip come from the maths line, never from taste — no padding, no fake counts.
Full law: `docs/FOUNTAIN_M3.md`.

## Intel backends — YouTube transcripts, three paths

| Path | Needs | Use |
| --- | --- | --- |
| `YOUTUBE_API_KEY` | Data API key | search + stats |
| yt-dlp (Agent-Reach) | local tool | transcripts, zero-config |
| **youtube-transcript.io** | `YOUTUBE_TRANSCRIPT_IO_TOKEN` in `.env` | hosted transcripts — no local tooling |

```
monarch transcript <video-id-or-url>... [--json] [--save DIR]   # up to 50/call
monarch tchan <channel-id>...                                   # Plus plans
monarch keys                                                    # shows all backends
monarch doctor                                                  # health, incl. hosted API
```

`monarch scrape <yt-url> --transcript` now auto-falls back to the hosted API
when yt-dlp is missing. Rate limit (5 req / 10s) is honored via `Retry-After`.

## Deep forensic — niche → 15-20 viral videos → DNA → ideas → video 💀

The full competitor takedown (`skills/deep-forensic/SKILL.md`):

1. **Agent hunts** — 5-8 channels ke 2-4 biggest outliers (15-20 videos), page
   tools se. Har video: `transcript-ingest` se pipeline me.
2. **`monarch deep-forensic dossier.json`** — Monarch computes:
   - **script DNA**: words/30s (Zack band 65-95), hook OPEN/closed (N1),
     second-person density, proof density, sentence rhythm, CTA placement (N4),
     title formula T1-T8
   - **production DNA**: runtime, engagement (likes/views), outlier multiplier
   - **patterns**: top-vs-bottom median split, har claim pe N
   - **10 idea drafts** winning patterns se (gate zaroori)
3. **Gate → M2 → make-short** — jitna analysis bhi ho, bina gate pass kiye
   kuch ship nahi hota.


### Zero-token path — agent fetch + ingest

Network-restricted sandbox me bhi transcripts: **agent apne page-fetch tool
se** `https://www.youtube.com/watch?v=<id>` **kholta hai** (platform network
se metadata + `## Transcript` milta hai), text file save karta hai, aur:

```
monarch transcript-ingest fetch.txt --json --save transcripts/
```

fetch-page markdown / WebVTT / SRT / plain — sab auto-detect, same forensic
record (`scrape`-compatible), pipeline seedha aage chalta hai.

## Neuro Video — playbook → storyboard → previz

The **Neuro-Psychology Playbook** (`monarch/playbook/neuro_psychology.md`, laws N1–N5)
is now code. The director plans a gated storyboard, renders the Hollywood box card,
writes the Fountain screenplay, synthesizes the psychoacoustic SFX bed, and cuts a
Ken Burns previz animatic — all stdlib, all deterministic per `--seed`.

| Law | Where it fires |
| --- | --- |
| N1 · 0.1s thumb-stop reflex | scene 1 = `hook` role, snap zoom-in, `hit` SFX, one focal visual |
| N2 · demographic dopamine | `--cohort kids | genz | adults` drives palette + pace + payoff density |
| N3 · Skinner variable-ratio | seeded tease/payoff schedule every 2–4 scenes, `sonar_ping` + `riser` |
| N4 · Cialdini value-debt | free takeaway scene before the payoff peak, CUA after it |
| N5 · 40Hz + 0.3s silence drop | `silence-sting` scene: riser → 0.3s dead air → `bass_drop` payoff |

```
monarch script --topic "the deep sea" --cohort genz --out screenplay.fountain --card
monarch video-storyboard --topic "the deep sea"            # the ASCII box card
monarch sfx --kind bass_drop --filter bass_boost --out drops.wav
monarch make-video --topic "the deep sea" --out output/deep-sea
```

`make-video` writes `screenplay.fountain`, `board.json`, `storyboard.txt`,
`sfx/*.wav`, `frames/frame_*.png`, `timeline.json` + `manifest.json`.
It is the **previz layer**: no footage generation, no upload — the HAAN gate
still owns the final render.

## TABAAHI wave — audio-first VO, humanizer, 2.5D parallax, mix bus 💀

Why videos felt robotic (VO cut mid-word, dead-air gaps, abrupt starts, no
SFX, still images) and the fix, as law: **L1 — the VO is the skeleton.**
Timing now comes from *measured speech*, not the scene maths.

- **`humanize`** — strips ~40 AI-tell patterns (delve/tapestry/game-changer,
  essay connectives, "not just X but Y" shapes, em-dash overuse, uniform
  rhythm), fixes inflated verbs *with grammar intact* (utilized→used,
  tapestry→story), flags lines that need a human rewrite. Fail-closed:
  reports signs/100w before → after.
- **`voiceover`** — sentence-boundary chunks (never mid-clause), 100ms
  lead-in, 250–500ms tail, 60ms crossfades, gap caps 0.5s/0.3s/0.15s, and
  QC that measures speech end from the waveform envelope (the TTS
  trailing-silence dead-air bug dies here). Backends: `edge` (real TTS on
  your PC), `dir` (per-scene wavs from Chatterbox/any GPU engine — see
  `docs/GPU_VOICE_UPGRADES.md`), `mumble` (offline placeholder), `auto`.
- **`make-video --animation parallax`** — 2.5D from stills: background
  plate crop-moves while the focal block + dialogue pill float the other
  way (DepthFlow idea, stdlib implementation).
- **`mix` / `--with-mix`** — the five-layer bus: VO on top, music bed
  sidechain-ducked under speech, per-scene SFX from the board, room tone
  killing digital silence, soft-limited master. Levels are measured and
  reported, never vibes.

```
monarch humanize "In today's world, let's delve into the tapestry of lies."
monarch voiceover --topic "the buried file" --backend auto --out output/vo
monarch make-video --topic "the buried file" --animation parallax \
                   --voice-backend auto --with-mix --seed 7
monarch mix --vo output/vo/vo_track.wav --duration 62 --board output/the-buried-file/board.json
```

Every scene's Fountain now carries a `[[VO: [prosody] | beat: ...]]`
direction line; payoff scenes land **partial** (info-tension) and the next
question re-hooks **before** the answer completes — carousel law, in code.

## CHAOS MONARCH — the loop that learns from the real world 💀

Four waves turned Monarch from a tool into an organism that measures itself:

- **Learn loop** — export YouTube Studio Advanced Mode to CSV, then:

  ```bash
  monarch learn ingest studio_export.csv --cohort "money niche v1"
  monarch learn distill        # records -> PerformanceRecord -> lessons
  monarch learn hygiene        # corroborate/stale/conflict audit of lessons
  ```

- **Truth layer** — deep-forensic now scores *freshness* with a half-life
  (default 105 days, `--half-life N`): `recency = 0.5^(age/HL)`, blended
  `0.7·engagement + 0.3·recency` into `fresh_rank`. No date = recency 1.0
  with an honest note — never a claim. Rows older than 2×HL land in
  `linkrot_risk_ids`; a `freshness:` line joins the DNA patterns and every
  idea carries its evidence note.

- **The Eye** — audit any make-video output dir:

  ```bash
  monarch audit output/videos/<slug>            # human report
  monarch audit output/videos/<slug> --csv studio.csv --json
  ```

  Anchored deterministic bands: hook 1–10, Zack pacing 65–95 words/30s,
  CTR <3 / 4–6 / 7–10%, AI-signs gate, voice QC, mix presence, optional
  dossier link-rot. Every finding = severity P0–P3 + evidence + the exact
  fix command + expected impact. Parked gaps (MP4 render) are REPORTED,
  never built — standing order #1.

- **Skill standard** — every SKILL.md is agentskills.io-certified by test
  (allowed frontmatter keys only, name/dir match ≤64, description ≤1024,
  body ≤500 lines). The validator fails the suite before a bad card ships.

**ART ENGINE — image banao, pose animate karo (2026-09-28):** `monarch/video/stickman_art.py`
- the operator's wish made real INSIDE the egress law: deterministic stickman
ART (Pillow) - head/torso/joints poses (idle/point/shock/wave/crown/walk/bow),
props (crown/magnifier), void+moon+stars - and POSE-TO-POSE animation
(joint-lerp frames -> mp4). Same persona bytes every render (brand law),
fail-closed, no text ever. CLI: `monarch art-scene --pose shock --prop crown`,
`monarch art-anim --poses idle,shock,crown`. AI photoreal gen stays parked
(egress); this is the in-sandbox art stage. Suite 487.

**W-B4 SHIPPED - PROTOCOL 100% WIRED (2026-09-28):** `monarch/video/vitals.py`
- engaged-class post-launch vitals (Studio numbers in -> band verdicts out:
CTR/swipe-gate/inflation/AVP/returning, honest [fill] placeholders, the
Aug-24-2026 engaged-vs-public laws printed) + the repurpose queue (1 long ->
Shorts skeleton: hook-remix, payoff-tease cut before the reveal, WTF-details,
loop-cut, ranking-teaser; 5-15 law, 22-45s band). CLI: `monarch vitals`,
`monarch repurpose`. TABAAHI PROTOCOL: ALL SIX WAVES DONE. Suite 477.

**W-B3 SHIPPED (2026-09-28):** `monarch/video/slop.py` + `kit.py` - the survival
layer + the launch kit. `monarch slop-audit CHANNEL`: assembly-line detector
(topic-stripped VO similarity), persona/disclosure/coverage tripwires, rc 2 on
P1. `monarch package DIR [--shorts --topics ...]`: title law + MANDATORY AI-
disclosure + no-bio-link + pinned comment tease + first-frame thumbnail +
honest checklist with measured LUFS. Suite 466.

**W-B1 SHIPPED (2026-09-28):** `monarch/video/forecast.py` - the pre-render
9-link chain gate (promise->click->first_3s->engaged->loops->peak->end->loop->
satisfaction; weak links NAMED, deliberately-bad plans fail with links listed)
+ But/Therefore beat lint (connectors or cue/driver inference) + curve
forecaster (healthy/hockey_stick/gradual_bleed/camel_humps/peak_too_early).
CLI: `monarch forecast DIR [--title --shorts --end-screen --loop --disclosure]`
- rc 2 names the broken link. Suite 455.

**W-A1/W-A2/W-B2 SHIPPED (2026-09-28):** canon = pixels now. `monarch/video/overlays.py`
- the V6 overlay layer burned into every render via libass (ZERO new deps):
karaoke word captions (word timing computed from our own synth), TEXT_SYNCED
cue band (y=320, 750 forever forbidden), end screen (last 7s, right 40%, gold
WATCH HERE), progress bar, loop tail. Sound law landed too: render loudnorm
targets -14 LUFS (live render measures -14.3), `measure_lufs` ebur128 meter,
audit LUFS finding; sonic logo (deterministic six-tone sting+resolve, never
ducked) via `--with-sonic`; end screen via `--v6-end-screen`. Suite 443.

**RESEARCH MASTER — complete inventory (2026-09-28):** `docs/RESEARCH_MASTER.md`
- ALL 130 findings from the 4 hunt layers in one file (incl. fine-print addendum: 1280x720/90%-custom/contrast evidence base, auto-dub 232+ langs & +13.48%, Beast integrity laws + The Goal, channel-level review posture, dopamine quantization 3-5Hz/10-20 spikes, RPE-vs-startle circuits, the no-slot-machine ethics law, universe-level peak-end, computer-agent gaze evidence, freebuff rejected-verdict): every number, repo,
  law and concept (algorithm gates, LUFS, story DNA, thumbnails, Beast
  leak, survival tripwires, outliers, engaged views, peak-end, gaze,
  RPE, Harmon circle, sonic branding, quickfires). Nothing left out.

**TABAAHI PROTOCOL — THE MAX PIPELINE (2026-09-28):** `docs/TABAHI_PROTOCOL.md`
- the integrated grand structure: ALL 4 hunt layers fused into one 11-stage
workflow (P0 Idea Hunt -> P10 Learn), 50-item weapons-coverage matrix
(nothing left out), per-stage laws/gates/outputs, and the W-A/W-B wave
execution order with acceptance criteria.

**TOOFAN LAYER deep hunt #4 (2026-09-28):** `docs/TOOFAN_LAYER.md` - the brain's
actual code: dopamine = prediction error (surprise, not reward;
calibrated MEDIUM curiosity gaps peak, payoffs must EXCEED promise),
Dan Harmon's 8-step story circle mapped to shorts, sonic-logo science
(+16% willingness-to-pay; numpy synth = our native tongue), Von
Restorff/returning-viewers/session-chaining quickfires.

**ABYSS LAYER deep hunt #3 (2026-09-28):** `docs/ABYSS_LAYER.md` - engaged-vs-public
view split (Aug 24 2026: earnings/YPP run on ENGAGED views only, public
overstated ~1.67x), the Peak-End doctrine (Kahneman -> the engineering spec
for the 2026 #1 satisfaction signal), gaze physics (eyes direct viewer
attention), and the 9-link convergence chain (the forecaster's spec).

**CHAOS LAYER deep hunt (2026-09-28):** `docs/CHAOS_LAYER.md` - Arsenal addendum #2:
the leaked MrBeast playbook laws, the SURVIVAL layer (inauthentic-content
enforcement tripwires + Monarch anti-slop armor), the 1,100x cloning-trap
study, and the stickman face-bias counter-strategy. Research-only, awaiting HAAN.

**TABAAHI ARSENAL hunt (2026-09-28):** `docs/TABAHI_ARSENAL.md` - research-only
haul: 2026 algorithm numbers (swipe gates, 22-45s band, AI-disclosure law),
LUFS -14/-1dBTP standard (loudnorm/ebur128 confirmed in our ffmpeg binary),
But/Therefore story DNA, retention-curve sickness metaphors, thumbnail CTR
numbers, live-verified repos, auto-dub free-reach play. Awaiting HAAN to
graduate into canon.

**Forensic audit + CHAOS MAX roadmap (2026-09-28):** `docs/CHAOS_MAX_FORENSIC.md`
- full microscope sweep: findings F1-F10 (own-compositor zoom-law breach
  FIXED with Motion clamp, tipeline typo tipeline typo FIXED, CI file READY-
  to-enable via web (docs/CI_READY.md; App token lacks workflows scope)), coverage 84% mapped, egress-honest
  constraint table, W-A/W-B/W-C upgrade waves.

**V6 viral Shorts canon (1.2B-views session):** `docs/VIRAL_SHORTS_V6.md` +
`monarch/video/shorts.py` — the 14-miss laws executable: no-text prompt
builder (Urdu-leak guard), VO-driven beat timing (never cut VO: VO+0.7),
TEXT_SYNCED planner (y 320/1450 never 750, 6 animations ≤2 repeats,
2-3 words), title 24-27 chars, link-in-bio banned (end-screen last 7s),
condensed-incomplete long_to_short (60/25/12 Zeigarnik split), buildup
music mood (4-layer FOMO, never hard kicks).

**Upload (the gofile step, legal-egress edition):** `monarch upload FILE` —
finished render goes to the repo's `deliverables` branch (asset commit + sha256
+ tip-diet; history link lives forever). gofile/Release-assets are TLS-blocked
in-sandbox; the operator's browser follows the raw link fine. HAAN-gated.

**Monarch V2 post-mortem (Every-Bear session):** `docs/MONARCH_V2_POSTMORTEM.md` +
`monarch/video/chunks.py` — chunk planner that NEVER splits a topic across render
chunks (the repetition bug), gap 0.85s + whoosh/riser at every boundary; audio
bitrate verified post-render (never the 32k robotic class); `sfx_crescendo`
(1.8s smooth FOMO sweep) replaces harsh intro/outro ticks (mix auto-swaps);
audit flags duplicate frames (unique image per beat law).

**Render memory (Einstein-session laws):** `docs/RENDER_MEMORY.md` — 19 paid
misses, L16 auto-fail. Wired in code: complete-sentence composer (no mid-sentence
clips, no duplicate seam words), VO lint (no `—`/`...`/digits), VAD + boundary
silence + gap-budget QC, broadcast polish chain (biquad EQ + saturation, peak
band 0.72–0.82), warm BGM mood (`--genre tutorial/educational/product/listicle`
→ Am–F–C–G pads, frame-1 audible, one CTA build; tension engine for mystery),
measured audit (mix peak, intro RMS, duration drift).

**Render (in-sandbox, operator order 2026-09-24):** `monarch render DIR`
turns a make-video dir into `*_v1_render.mp4` — 2-input concat+audio build
(G7/L2), burned scene captions + `captions.srt` (G11), versioned name (G16),
duration drift checked vs the audio track ±0.5s (L13). Upload stays human-gated (HAAN).

**Never-again guards** (PRODUCTION_LAW_V2 wired into code, not just canon):
`monarch doctor` (L1/G2 env check, fail-closed), `monarch budget --frames N --clips M`
(G3/L10 batch planner), leading-silence trim + 0.3s onset gate (G8/L4), mix VO-gate
with multi-window drop proof (G7/L3), fountain re-count validation (G4/G9),
`captions.srt` + `timeline.json` shipped by every VO build (G10/G11/G14), audit
cross-verifies duration sources and reads both board shapes (G5/G14).

Docs: `docs/RENDER_LAWS.md`, `docs/PRODUCTION_LAW_V2.md` (16 registered
failures G1–G16 + 15 iron laws + delivery checklist — `monarch laws
[--part laws|failures|checklist]` prints them anywhere), `docs/CONTENT_PLAYBOOK.md`, `docs/MASTER_PLAN.md`.

## Skills, memory & the learning loop

Ruflo-inspired (ideas mined, never the harness — stdlib law holds):

- **`monarch/skills/`** — six executable playbooks in the open `SKILL.md`
  format (`make-short`, `forensic-hunt`, `sfx-design`, `thumbnail-pack`,
  `metadata-seo`, `upload-day`). Every command they mention is tested to be
  real. A fresh session reads these and works — no handoff essays.
- **`monarch memory save / restore`** — the cross-session handoff bridge
  (`.monarch/memory.json`): M-state, channel DNA, pending approvals, notes,
  lessons digest, performance digest. Fail-closed on corrupt/foreign files.
- **`monarch learn record / log / distill [--apply]`** — the L16 loop closed
  with reality: log APV/views per upload, median-split top vs bottom, and
  distill provisional retention signals into `self_improve/lessons.md`
  under the 3x rule. One video never becomes a law.
- **`monarch/agents/`** — five specialist role cards (Forensic Analyst,
  Script Doctor, SFX Designer, Thumbnail Strategist, SEO Packer), each bound
  to a real M-state with guardrails and handoffs.

```
monarch memory save --state M3_script --topic "the deep sea" --pending "approve board"
monarch memory restore
monarch learn record --topic "the deep sea" --views 42000 --avg-pct 71 --cohort genz
monarch learn distill --apply
```

