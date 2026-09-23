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

