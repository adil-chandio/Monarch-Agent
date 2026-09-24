# GPU voice & media upgrades — knowledge hooks (NEVER dependencies)

TABAAHI wave (2026-09-24) decision, extending the ruflo precedent: the GPU
tools below are **idea-mined and documented only**. They are never pip
installed, never vendored, never required. Monarch's stdlib pipeline runs
without them tonight; each hook below shows exactly where a GPU box plugs in.

## 1. Chatterbox (Resemble AI, MIT) — emotional TTS

- First open-source TTS with an **emotion exaggeration dial 0.0–2.0**
  (dread ≈ 1.3, forensic calm ≈ 0.4). 63% blind-test win vs ElevenLabs;
  6.5GB VRAM (5GB turbo); 5s zero-shot cloning.
- **Hook:** generate one 16-bit mono WAV per scene on your GPU box and drop
  them in a directory, then:
  `monarch make-video ... --voice-backend dir --wavs-dir /path/to/wavs`
  Contract: `scene_01.wav`, `scene_02.wav`, … (or `1.wav`), 16-bit mono,
  same rate as `--sr`. Monarch glues, times and QC's them unchanged.
- Prosody per scene already ships in the Fountain: `[[VO: [lower, slower] |
  beat: THE DROP]]` — those notes are what you dial Chatterbox with.

## 2. MMAudio (UIUC + Sony) — video → synchronized SFX

- Open-source generative SFX/ambience aligned to picture.
- **Hook:** Monarch's board already carries per-scene `sfx` roles
  (hit/riser/bass_drop/…) mixed through the bus. For richer beds, render
  MMAudio stems on a GPU box and place them with
  `monarch mix --vo vo_track.wav --duration N --board board.json`.
  A future `sfx` value may point at a wav path; the bus adds it at the
  scene's `t_start` unchanged.

## 3. DepthFlow / Wan2.2 / FramePack — image→video

- DepthFlow: 2.5D parallax shader with seamless loops (no watermark) — the
  quality bar for animating stills. Wan2.2 TI2V-5B: 720p@24 I2V (~9min/5s on
  a 4090). FramePack: 8GB VRAM + 32GB RAM long-video I2V. Wan2GP for
  GPU-poor boxes.
- **Hook:** Monarch ships `--animation parallax` (stdlib 2.5D: background
  plate crop-moves, foreground floats the other way) as the in-repo
  baseline. A GPU box renders DepthFlow clips per scene from the SAME
  `board.json` scene rows (visual prompts included) and the edit order,
  timings and VO skeleton stay identical.

## Why never dependencies

Sandbox reality (no GPU, bash egress limited to github/pypi) and the
constitution (fail-closed, stdlib-only core) both say the same thing:
Monarch must build, test and render its previz + audio pipeline with zero
external services. GPU tools are *upgrades you own*, not *requirements we
ship*. Every hook above degrades to the stdlib path automatically.

## 4. Batch-3/4 hunt additions (2026-09-24 forensic — hooks only)

- **EchoMimic V3 (antgroup, Apache-2.0)** — 1.3B params, unified
  multi-modal human animation; consumer-GPU class (V1 4.3k★ was AAAI-25;
  V2 CVPR-25; V3 AAAI-26). Hook: needs portrait + **audio clip** — Monarch
  already emits per-scene WAVs + vo_track.wav (the wav contract IS the
  feedstock). Faceless → optional talking-face on your GPU box.
- **video2x (k4yt3x, 21k★)** — super-resolution + frame interpolation.
  Hook: run final render through it on PC to kill softness/choppiness
  ("visual humanizer"); can also smooth the 2fps previz via RIFE.
- **LosslessCut (mifi, 43k★)** — stream-copy trimming, zero re-encode.
  Hook: lossless assembly stage for per-scene clips on your PC.
- **pyVideoTrans (jianchang512, 19k★)** — ASR → translate → AI dub →
  composite; 30+ engines incl. **edge-tts** (same TTS family as Monarch's
  `--voice-backend edge` — zero contract friction); speaker diarization.
  Hook: 1 finished video → Urdu/Hindi/English reach multipliers.
- **faster-whisper (tiny, int8, CPU)** — PROVEN IN PRODUCTION by the
  journal (v7): word-level timestamps from real audio; text garbled but
  timings true — take the part that works, discard the rest.
  Hook: next-step word-level VO QC beyond envelope speech-end.
- **OpenCut (64k★, MIT)** — rewrite roadmap: Editor API, Rust core,
  **MCP server for agents, headless mode + batch rendering**.
  Hook (future, when render stage is ordered): Monarch board.json →
  editor project → headless render = the MP4 bridge. Roadmap-as-shipped
  warning applies: classic track is what actually runs today.

All items: knowledge + optional PC hooks. Never pip deps, never required
(ruflo precedent, constitution 05/08).
