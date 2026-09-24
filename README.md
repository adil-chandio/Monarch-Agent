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

Clone branch `arena/01a0c8a4-monarch-agent`, activate with your key, then:

```
monarch activate DoitMon@rch
```

Agent asks 4 things: channel/niche, 16:9 or 9:16, short or long, language.  
Then: YT forensic + keywords → 10 ideas + TOP 1 → wait → script → wait → video (haan) → QC → thumbs → metadata. **You upload.**

Full law: `BOOT.md` · `AGENT.md` · `docs/WORKFLOW.md`

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

