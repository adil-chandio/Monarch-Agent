# MONARCH CAM — DELIVERY

Stage 13. All seventeen items ship together. A partial delivery is not a delivery.

---

## THE 17 REQUIRED DELIVERABLES

| # | Deliverable | Artefact |
|---|---|---|
| 1 | Final **60-second 1080x1920 9:16 MP4** | `output/<slug>/*.mp4` |
| 2 | Full **timecoded English narration script** | `output/<slug>/screenplay.fountain` + scene board |
| 3 | **Voice-over audio file** | `output/<slug>/vo.wav` |
| 4 | Final **VO / SFX / music mix** | `output/<slug>/mix.wav` |
| 5 | **Footage-source and rights ledger** | `output/<slug>/03_footage_ledger.md` |
| 6 | **Edit decision list** with exact timestamps | `output/<slug>/09_edl.md` |
| 7 | **YouTube Shorts title** | in `12_package.md` |
| 8 | **Two A/B title alternatives** | in `12_package.md` |
| 9 | **Description** | in `12_package.md` |
| 10 | **Hashtags** | in `12_package.md` |
| 11 | **Tags** | in `12_package.md` |
| 12 | **Pinned comment** | in `12_package.md` |
| 13 | **Cover-text recommendation** | in `12_package.md` |
| 14 | **TikTok caption** | in `12_package.md` |
| 15 | **Instagram Reels caption** | in `12_package.md` |
| 16 | **Upload checklist** | `output/<slug>/17_upload_checklist.md` |
| 17 | **Synthetic / altered-content disclosure** — explicit yes or no, with the reason | in `17_upload_checklist.md` |

Item 17 is never left blank and never "assumed not needed". State the answer and the reason.

---

## THE NO-STOP-AT CHAIN

```
DO NOT STOP AT IDEAS.
DO NOT STOP AT LINKS.
DO NOT STOP AT A SCRIPT.
DO NOT STOP AT A RESEARCH LIST.
```

Complete the workflow in this exact order:

```
ANALYSE CHANNEL DATA
  → RESEARCH REAL FOOTAGE
  → TRACE ORIGINAL SOURCE
  → VERIFY QUALITY
  → VERIFY RIGHTS / PERMISSION
  → SELECT ELITE SCENES
  → WRITE SCRIPT
  → CREATE VOICE-OVER
  → EDIT
  → MIX AUDIO
  → RENDER
  → PACKAGE
  → DELIVER
```

The only legitimate stop mid-chain is a declared `BLOCKED` stage (`WORLD.md` §4) — reported
loudly, with what is needed to unblock it, never papered over with substitute footage.

---

## PRE-EXPORT REVIEW (run before final export — Stage 11 gate)

| # | Question | Fail action |
|---|---|---|
| 1 | Is the first frame strong enough to stop a thumb? | recut the open |
| 2 | Does every clip earn its position? | cut the filler |
| 3 | Is any filler present? | cut it |
| 4 | Is the ending bigger than the opening? | re-order or re-source |
| 5 | Is the title honestly delivered? | change the title, not the footage |
| 6 | Is the English natural? | rewrite, then `monarch humanize` |
| 7 | Are the captions readable on TV and phone? | increase size, reduce words |
| 8 | Is the edit TV-safe (readable at distance, sound-low)? | simplify the frame |
| 9 | Are sources / licences logged? | back to Stage 5 |
| 10 | Are there any visible source watermarks? | drop the clip — never crop a watermark out |
| 11 | Does this Short make the viewer want the next Monarch Cam video? | fix the closing bridge |

Any "no" → **fix before export.**

Tool limitation: the current `monarch qc-render` syntax is `monarch qc-render <video.mp4>
<board.json>` and only checks a render against Monarch's scene board. `monarch render <dir>`
can render the base agent's own `make-video` previz frames and audio; it does **not** assemble
external licensed wildlife clips. Do not use that previz MP4 as deliverable #1. For this world,
verify the final licensed-footage edit in the actual editing/export tool and run a separate
human review; Stage 11 is blocked until such an export path exists.

---

## UPLOAD CHECKLIST (item 16) — template

```
[ ] MP4 is 1080x1920, 30fps, ~60s, correct loudness
[ ] Title passes `monarch gate-title`; run `monarch slop-audit <channel-dir>` separately where render-history exists
[ ] Two A/B titles recorded
[ ] Description includes the next-video / playlist link
[ ] Tags + hashtags set
[ ] Pinned comment drafted and pointing at the connected long-form / playlist
[ ] Cover text applied, no arrows / no UI clutter
[ ] End screen target chosen deliberately
[ ] Playlist assigned (exactly one)
[ ] Footage ledger complete, every clip GRANTED with proof on file
[ ] Attribution present exactly as required
[ ] Synthetic/altered-content disclosure: YES / NO — reason:
[ ] Not age-restricted, no graphic harm, no misleading "attack" claim
[ ] Human performs the YouTube upload (`monarch upload` is a file/release transfer, not YouTube publishing)
[ ] After upload: monarch learn record ... then monarch memory save
```

The last line closes the loop: reality gets logged, so the next video is better informed
(see `monarch/skills/upload-day/SKILL.md`).
