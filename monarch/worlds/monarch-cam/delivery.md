# MONARCH CAM — DELIVERY

Stage 13. A complete production delivery contains all seventeen items below. If the built-in
external-footage edit/export path is unavailable, follow `WORLD.md` §4 and use a lawful alternate
editor/render route. A failed tool route is not a terminal `BLOCKED` outcome; pause only for a
required human approval/input, then resume. Never present a partial package or plan as a finished
video.

---

## THE 17 REQUIRED DELIVERABLES

| # | Deliverable | Artefact |
|---|---|---|
| 1 | Final **60-second 1080×1920 9:16 MP4** | `output/<slug>/*.mp4` (real footage; base previz is not this file) |
| 2 | Full **timecoded English narration script** | `output/<slug>/screenplay.fountain` + scene board |
| 3 | **Voice-over audio file** | `output/<slug>/vo.wav` |
| 4 | Final **VO / SFX / music mix** | `output/<slug>/mix.wav` |
| 5 | **Footage source, context, rights, and claim-risk ledger** | `output/<slug>/project_notes.md` (Stages 2–6 sections) + check log |
| 6 | **Edit decision list** with exact **verified** source timecodes | `output/<slug>/09_edl.md` — `TBD` rows are not a complete edit |
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

Item 17 is never left blank and never “assumed not needed.” State the answer and the reason.

Stages 1–6 research is kept in **one** `output/<slug>/project_notes.md` with per-stage sections —
not six separate reports. No clip score, shortlist, or review claim without actual visual
inspection (`NOT SCORED` otherwise), and no scene-specific script/VO/EDL for unseen footage.

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
ANALYSE CHANNEL CONTEXT
  → DISCOVER & LOG REAL FOOTAGE
  → TRACE SOURCE & CONTEXT
  → SCORE FOOTAGE QUALITY
  → QUICK CLAIM-RISK / RIGHTS SCREEN
  → SELECT ELITE SCENES
  → WRITE SCRIPT
  → CREATE VOICE-OVER
  → EDIT
  → MIX AUDIO
  → RENDER
  → PACKAGE
  → DELIVER & PRE-PUBLISH CHECK
```

Per-stage approval gates may pause the work for the operator's decision; they do not end the
assignment. A failed source, API, player, editor, or renderer route is temporary: follow
`WORLD.md` §4, try lawful alternatives, and continue. Mark an unviewable candidate `NOT SCORED`;
that does not make Stage 4 or the pipeline `BLOCKED`. If an essential operator-owned file,
permission, or decision is missing after alternatives are tried, ask for that specific input and
resume when supplied. Keep rights unknown honestly, never substitute unauthorized footage, and
never hand over planning artefacts as the final video.

---

## PRE-EXPORT REVIEW (run before final export — Stage 11 gate)

| # | Question | Fail action |
|---|---|---|
| 1 | Does the first frame show a strong, truthful, real moment without a misleading crop? | recut the open or reject the source |
| 2 | Does every clip earn its position? | cut the filler |
| 3 | Is any filler present? | cut it |
| 4 | Does the ending pay off the opening or leave a truthful next question? | revise the story; do not manufacture escalation |
| 5 | Is the title honestly delivered by the selected footage? | change the title, not the footage |
| 6 | Is the English natural and supported by the sources? | rewrite, then `monarch humanize` |
| 7 | Are captions readable on TV and phone? | increase size, reduce words |
| 8 | Is the edit TV-safe (readable at distance, sound-low)? | simplify the frame/mix |
| 9 | Are source chain, context, rights status, and quick claim-risk screen logged separately? | back to Stages 3–5; keep unknowns labeled |
| 10 | Are watermarks/source markers intact and represented honestly? | do not hide/crop them; trace the source, seek an appropriate master, or choose another clip |
| 11 | Does this Short make the viewer want the next Monarch Cam video? | fix the closing bridge |

Any failed check must be fixed or explicitly documented before export. No score, edit, credit,
voice-over, or “no match” result turns unverified rights into clearance.

Tool limitation: the current `monarch qc-render` syntax is `monarch qc-render <video.mp4>
<board.json>` and only checks a render against Monarch's scene board. `monarch render <dir>`
can render the base agent's own `make-video` previz frames and audio; it does **not** assemble
external wildlife clips. Do not use that previz MP4 as deliverable #1. Use an available, lawful
footage-capable editor/export route and run a separate human review; inability of the built-in
renderer is not a Stage 11 stop. If an available route fails, follow `WORLD.md` §4 and try another.
If operator-owned setup, permission, or a source file is truly required, ask for that specific
input and resume after the gate. Never present a previz or AI visuals as the finished video.

---

## UPLOAD CHECKLIST (item 16) — template

```
[ ] MP4 is 1080×1920, 30fps, about 60s, with checked loudness and sync
[ ] Title passes `monarch gate-title`; run `monarch slop-audit <channel-dir>` separately where render-history exists
[ ] Two A/B titles recorded
[ ] Description includes the next-video / playlist link
[ ] Tags + hashtags set
[ ] Pinned comment drafted and pointing at the connected long-form / playlist
[ ] Cover text applied, no arrows / no UI clutter
[ ] End-screen target chosen deliberately
[ ] Playlist assigned (exactly one)
[ ] For every clip: lead/source/context and rights evidence/status are recorded; unknown means UNKNOWN, not GRANTED
[ ] Quick claim-risk checks, exact tools/sources, date, and result recorded; a no-match result is not clearance
[ ] Attribution is present exactly as required where a licence/source requires it
[ ] Music/audio rights and source are recorded separately from visual-footage rights
[ ] YouTube Studio Copyright Checks run on the intended final draft; status, time, claimant/segment (if any), and remaining uncertainty recorded
[ ] Any Studio match/claim is reviewed and resolved or the human explicitly decides not to publish; no evasion edits or unsupported disputes
[ ] Synthetic/altered-content disclosure: YES / NO — reason:
[ ] No graphic harm, staged distress, false chronology/location, or misleading “attack” claim
[ ] Human performs the YouTube publish action (`monarch upload` is a file/release transfer, not YouTube publishing)
[ ] After publication: record available results via `monarch learn record ...` and `monarch memory save`; do not invent analytics that have not arrived
```

Studio Checks can take longer than a minute and are not final clearance. A no-match result does
not rule out a later or manual claim. The human uploader makes the final publish decision.

The last line closes the loop: real results get logged when available, so the next video is
better informed (see `monarch/skills/upload-day/SKILL.md`).
