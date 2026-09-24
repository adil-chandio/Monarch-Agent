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

## 5. LivePortrait (KlingAIResearch/Kuaishou, MIT) — portrait animation hook (2026-09-24)

Live-check kiya gaya: `KlingAIResearch/LivePortrait` (19.1k stars, active,
**MIT license** — commercial OK). Static portrait + DRIVING VIDEO → animated
talking head (lip-sync, stitching, eye retarget); animals mode bhi
(`inference_animals.py`). Speed ~12.8ms/frame RTX 4090 par. Weights repo me
NAHI hain (pretrained_weights khali — HuggingFace se download hota hai);
stack = torch + onnxruntime-gpu + insightface + ffmpeg-python.

**Monarch ke liye verdict: HAAN, lekin sirf avatar-upgrade hook ke tor par.**
Faceless stickman pipeline (current product) ko iski zaroorat NAHI. Yeh tab
kaam aata hai jab operator FACE-channel test kare:

- **EchoMimic V3 (§4) vs LivePortrait:** EchoMimic AUDIO-driven hai —
  Monarch ke wav-contract (per-scene WAVs / vo_track) se seedha jorta hai.
  LivePortrait VIDEO-driven hai — bridge yeh hai ke operator apni ek
  webcam/webcam-style driving take record kare, phir avatar usko puppet
  karta hai (identity preservation better, speed real-time-class).
- **Wav-contract mapping (agar kabhi use ho):** vo_track.wav wahi rehta hai;
  LivePortrait ko chahiye ek source portrait + driving video. Driver ke
  bagair audio→keypoint adapter (EchoMimic-class) pehle aayega.
- **Standing order (#2) unchanged:** sandbox/GPU tools kabhi dependency
  nahi — yeh entry sirf operator-PC recipe hai. In-repo Monarch previz/QC
  par iska zero asar; audit iski report NAHI karta (yeh parked upgrade
  path hai, gap nahi).
- **License note:** MIT = Monarch ke zero-dependency + operator-ownership
  laws ke sath khara. Weights ka apna license HF par check ho (repo MIT,
  base-model weights alag terms ho sakte hain).

## 6. Concat (jub0t/Concat) — parked render stage ka strongest candidate (2026-09-24)

Live-check: OSS **CapCut replacement** — Rust engine + GPU compositor,
100% local (no watermark/account/upload), AGPL-3.0 (+ LICENSE-EXCEPTIONS.md
— operator-PC par alag tool ke tor par use ke liye theek; Monarch me
kabhi link/merge NAHI), v0.2.4 **beta**, 3.5k stars, push aaj bhi.
Auto-captions (local Whisper), TTS + voice cloning, bg removal, keyframes,
170+ effects, multi-track, 4K H.264/HEVC/AV1 export.

**Sab se bara point: JSON-RPC + gRPC + MCP API + CLI — "AI agents can cut
video with it."** Recipes JSONL lines me: `project.create` → `media.import`
→ `edit.apply {op: addClip, trackId, start}` → `project.get` → export.

**Monarch mapping (operator-PC recipe — in-repo code NAHI banega):**
- Monarch already emits: `board.json`, `timeline.json` (t_start/t_end),
  `captions.srt`, `vo/vo_track.wav`, `sfx/*.wav`, previz frames.
- Concat side: har scene ka frame/clip import → `addClip` at OUR
  timeline.json times → srt/captions layer → VO track banao → export.
- Yani Monarch ka "board = truth" contract waisa hi rehta hai; Concat sirf
  CAMERA-OPERATOR hai jo us board ko MP4 me udelta hai.

**Caveats (L12 honesty):**
1. Beta software — export ke baad hamare L13 ffprobe checks
   (duration ±0.5s, streams, resolution, codecs) phir bhi zaroori;
   G14 ka sabak kisi engine par bhi lagoo hota hai.
2. G7/L3 VO-gate laws engine-agnostic hain: final MP4 par speech-band +
   multi-window proof phir bhi chalao — engine badlo, VERIFICATION nahi.
3. AGPL: yeh Monarch ka dependency KABHI nahi (zero-dependency law #1) —
   operator ke PC par alag program, API se baat.

**Status: §4 EchoMimic (VO) + §6 Concat (render) = pura operator-PC
production stack ka naqsha. In-repo Monarch ab bhi previz/QC/truth-layer
hai — render parked hai jab tak aap khud order na karo.**
