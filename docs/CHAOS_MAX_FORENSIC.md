# 🔬 CHAOS MAX — FORENSIC AUDIT + UPGRADE ROADMAP (2026-09-28)

Microscope sweep ordered by the operator: every module, coverage
measured, probes run, no-kami hunt. This file is the verdict + the
road to CHAOS MONARCH MAX. Findings carry IDs (F*) and statuses
(FIXED / OPEN-shippable / BLOCKED-egress / PARKED-until-ordered).

---

## 1. WHAT MONARCH IS TODAY (measured, not remembered)

- **17,319 LOC** across `monarch/` + `tests/` (2,171 more in 31 test
  files; 430 tests, all green at sweep time).
- **44 CLI commands** (activate→hunt→script→make-video→render→audit→
  short-plan→upload → doctor/memory/learn/deep-forensic).
- **4 canons enforced**: PRODUCTION_LAW_V2 (G/L laws), RENDER_MEMORY
  (19 misses), MONARCH_V2_POSTMORTEM (R1–R6), VIRAL_SHORTS_V6 (M1–M14).
- **Coverage 84% total.** Video core ≥90%. Weak: `intel/*` 21–54%
  (egress-blocked network code), `cli.py` 67% (thin-path surface).
- **Live-proven chains**: make-video→render (drift ≤0.004 s),
  audit 0–100 scoring, upload rail (deliverables branch, sha256),
  chunk planner, concat bridge, 8 GENRES × 4 LENGTH_CLASSES.
- **6 vendored reference repos** (idea-mine only, never linked):
  AI-Youtube-Shorts-Generator, Stickman-Studio, Viral-Faceless-Shorts-
  Generator (piper + speechalign), claude-youtube, faceless-youtube-
  agents.

## 2. FINDINGS (the microscope's catch)

| ID | Finding | Severity | Status |
|----|---------|----------|--------|
| **F1** | **Our own compositor breached the V6 zoom law** — `_OPEN` 1.0→1.18, alternates 1.14/1.16, default `zoom_to=1.12`. Miss #6 ("pixelated zoom, never above 1.10") was ONE careless edit away from repeating *inside* our pipeline. | **P1 — own-code M6 repeat risk** | **FIXED** this wave: all Motions ≤1.08 + `Motion.__post_init__` clamp (a bad caller cannot build a pixelator anymore) + 4 pinning tests |
| **F2** | `pipeline.py` walrus typo `tipeline :=` — harmless but sloppy (L-class hygiene). | P3 | **FIXED** (renamed) |
| **F3** | **No CI.** Suite ran only in-sandbox; a bad push to main would go unnoticed by machines. | P1 process | **READY-BLOCKED**: workflow file verified (fresh-venv 430 passed, CI-parity) but the Arena GitHub App lacks the `workflows` scope — push rejected (probed). One-minute web add: `docs/CI_READY.md` |
| **F4** | **V6 craft layers planned but not rendered**: `shorts.py` plans TEXT_SYNCED cues, end-screen, progress bar, loop-end frame — but `render.py` burns none of them (scene captions only). Canon ≠ pixels yet. | P1 gap | OPEN — shippable (W-A1 below) |
| **F5** | **No word-level timing.** voiceover.py tracks sentence chunks, not words → karaoke underline law is unimplementable *as-is*. Whisper alignment BLOCKED (model weights egress). | P1 gap | OPEN — solvable WITHOUT whisper: mumble VO is self-synthesized, so word boundaries are computable at synth time (W-A2) |
| **F6** | `drawtext` filter absent from imageio-ffmpeg binary; Pillow not installed → overlays need a numpy/PIL compositor pass, not ffmpeg filters. | P2 constraint | Designed around (W-A1) |
| **F7** | Coverage holes: `cli.py` 67%, intel 21–54%. The untested paths are exactly the ones a fresh sandbox hits first (flag typos, rc codes). | P2 | OPEN — cheap wins (W-B4) |
| **F8** | `packaging/titles.py` scores LONG-form laws (18–60 chars); Shorts title law (22–35, ideal 24–27) lives only in `shorts.py`. Two laws, one surface — a long-form title could slip into a Short package. | P2 | OPEN — W-B2 router |
| **F9** | Egress truth confirmed again by probe: edge-tts (`speech.platform.bing.com`) BLOCKED, hf.co (piper voices) BLOCKED, all generic file hosts BLOCKED. Any roadmap item needing weights/endpoints is parked honestly. | constraint | Documented (§4) |
| **F10** | `intel/` ideas/reach modules are near-untestable in-sandbox (network) — their value depends on operator-run keys/endpoints outside the sandbox. | P3 | Honest park, tests mock the seams they can |

## 3. WHAT "MAX LEVEL" MEANS (measurable targets)

1. **Zero manual re-touch**: topic in → packaged deliverable link out,
   one command chain, no hand-editing between stages.
2. **Canon = pixels**: every law that can be *seen or heard* in the
   output is verified by the auditor from the OUTPUT file, not from
   intentions.
3. **Forecast beats hindsight**: pre-render retention/CTR forecast
   per variant; post-render audit trend tracked across renders
   (learning loop already has `memory/learn` bones).
4. **Long-form + Shorts from one topic tree** (content multiplier:
   1 research pass → 1 long + 3 Shorts + packaging kits).

## 4. CONSTRAINT MAP (egress-honest, probed 2026-09-28)

| Want | Verdict |
|------|---------|
| Pillow (overlays, stickman, thumbs) | ✅ pypi → installable NOW |
| CI on GitHub runners | 🟡 file ready (`docs/CI_READY.md`); needs operator web-add (App scope) |
| Word timing for mumble VO | ✅ pure math on our own synth |
| Chunked long-form render E2E | ✅ planner exists; wire render loop |
| piper/edge neural VO | ❌ weights/endpoints egress-blocked (hf.co, bing) |
| Whisper word-alignment | ❌ model download blocked |
| Image-gen API / YouTube Data API publish | ❌ blocked (only github/pypi egress) |
| gofile-class file host | ❌ blocked — deliverables-branch rail remains THE rail |

## 5. THE MAX-LEVEL ROADMAP (waves, awaiting operator HAAN)

### W-A — RENDER THE CANON (highest impact, all in-sandbox)
1. **Overlay compositor pass** (F4/F6): Pillow text engine — TEXT_SYNCED
   cues at y=320/1450 (never 750), 6 animations, 2–3 words, show 1.7 s
   fade 0.3 s, semi-transparent plate (0,0,0,160); end-screen mockup
   (last 7 s, right 40%, gold border, WATCH HERE); progress bar
   (bottom, gold); loop-end frame. Audit then verifies burned pixels.
2. **Word timing + karaoke** (F5): mumble synth emits per-word times
   (char-weighted, wps-calibrated) → karaoke underline captions REAL;
   also unlocks exact `beats_for_vo` inputs per beat.
3. **SRT + packaging kit emitter**: `.srt` + title (Shorts law router,
   F8) + description + pinned comment + first-frame thumbnail —
   `monarch package` one-shot.
4. **Chunked long-form E2E**: `plan_chunks` → per-chunk render →
   boundary whoosh+riser → incremental merge → single upload (R2 law,
   >90 MB split already fail-closed).

### W-B — THE SCIENCE LAYER
1. **Retention forecaster**: score hook (first-3s shock density), beat
   pacing variance, dead-air = 0 checks, loop math → AVD/CTR forecast
   per variant BEFORE render; A/B 3 variants, pick max.
2. **Trend memory**: audit scores per render into `learn` → `monarch
   stats` shows quality trajectory; regression = gate fail.
3. **SFX preset pack**: the parked 10 presets + mood-mapped beds
   (buildup already shipped; add dread/triumph/curiosity).
4. **Coverage close-out**: cli.py flag-matrix test (every command,
   --help + one happy path + one fail path → rc contract), intel mock
   seams.

### W-C — PARKED (blocked by egress; revisit on operator PC / egress change)
Neural VO (piper), whisper align, AI image gen in-pipeline, YouTube
publish API, mirror link host. Design stubs exist in vendor/ (idea-mine
only — never linked).

**Verdict:** the factory's BONES are max-grade (laws, gates, audit,
rail). The flesh that's missing is PIXELS (W-A1/2) and FORESIGHT
(W-B1/2). W-A is the tabahi-next-level move: it converts the V6 canon
from documentation into frames on screen. 💀
