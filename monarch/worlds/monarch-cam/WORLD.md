# MONARCH CAM — WORLD CONTRACT

This file is the channel workflow contract. The other Markdown files in this folder supply
its identity, evidence, rules, sourcing, packaging, delivery and current assignment.

---

## 0. DOCUMENTED TRIGGER (NOT WIRED YET)

The intended natural-language activation phrase is:

```
monarch cam activate
```

**Integration status:** this addition is docs-only. The repo's root agent entrypoints and CLI
were intentionally left unchanged, so the phrase is not automatically routed to this file
yet. Until an additive router is explicitly approved, the operator must name/read
`monarch/worlds/monarch-cam/WORLD.md` to select this workflow. There is no shell command
`monarch cam`.

If the access key has not been verified for this session, follow the standard access rule in
`monarch/constitution/00_IDENTITY.md` first; refuse with Monarch's standard refusal message
and stop. This world never weakens the access law.

This is **not** the base `monarch activate` trigger. That trigger and its four-question intake
remain unchanged. When an approved router later recognizes this channel phrase, it may select
the known channel and skip only asking for channel/niche; it must preserve the base safety,
approval and WAIT gates.

---

## 1. BOOT SEQUENCE (when this world is explicitly selected)

1. Confirm access key under the existing Monarch law.
2. Read in order: `identity.md` → `analytics.md` → `audience.md` → `rules.md` →
   `sources.md` → `packaging.md` → `delivery.md`.
3. List `assignments/` and load the active brief. If none is active, ask the operator for one;
   **do not invent a topic**.
4. Since this is docs-only, say **WORLD CONTEXT LOADED — ROUTING NOT WIRED**. Only after a
   router is approved should the response say `MONARCH CAM — WORLD ACTIVE`.
5. Start Stage 1. No greeting, no generic intake questions for facts fixed by this world.
   Still ask for missing evidence that is genuinely required to proceed.

---

## 2. THE 13-STAGE PIPELINE (sequence is law)

Every stage produces the named artefact. A tool command can assist but does not prove that a
stage is complete. Never claim a tool did work it cannot do. Stage 1 uses operator/Studio
evidence; later stages use the assignment brief and actual source files.

| # | Stage | Required artefact | Tooling / honest limitation |
|---|---|---|---|
| 1 | ANALYSE CHANNEL DATA | `output/<slug>/01_channel_analysis.md` | Use current YouTube Studio evidence. `monarch learn ingest <csv_file>` imports Studio CSV/TSV performance rows; `monarch learn log` lists logged rows. `monarch vitals <render-dir>` is a per-video post-launch sheet, not a private channel-wide analytics fetch. |
| 2 | RESEARCH REAL FOOTAGE | `output/<slug>/02_footage_candidates.md` | `monarch search <query>` (YouTube), `monarch wsearch <query>`, `monarch rsearch <query>`, `monarch scrape <url>` can assist; tool availability/network may block them. Links are leads only. |
| 3 | TRACE ORIGINAL SOURCE | `output/<slug>/03_footage_ledger.md` with creator, source URL, filmed date, place, type | `monarch scrape <url>` / `monarch transcript <id>` may assist. Manually trace upstream to the original filmer/licensor; never infer rights from a repost. |
| 4 | VERIFY QUALITY | `output/<slug>/04_scene_scores.md` — 10 scores + mean; select only ≥8.5/10 | Score manually from the actual clip and crop. `monarch fit <line> --n N` checks script/timing fit, **not** footage quality. |
| 5 | VERIFY RIGHTS / PERMISSION | Ledger with written licence proof and exact attribution, or explicit `BLOCKED` | Human licensing action is required. No permission = not selectable. |
| 6 | SELECT ELITE SCENES | `output/<slug>/06_scene_selection.md` + storyline spine | `monarch gate-idea --title ... --hook ... --itch ... --visual ...` can gate the premise; a human confirms the selected source clips. |
| 7 | WRITE SCRIPT | `output/<slug>/screenplay.fountain` + numbered, timed scene board | `monarch maths --seconds 60`, `monarch screen-script`, `monarch script-fountain`, `monarch humanize`. Natural English, factual narration, exact clip linkage. |
| 8 | CREATE VOICE-OVER | `output/<slug>/vo.wav` (normalize/copy backend output into this deliverable) | `monarch voiceover --script-file ... --out ...` only with an approved real voice backend. Placeholder/mumble audio is never final. |
| 9 | EDIT | `output/<slug>/09_edl.md` — exact source in/out, sequence, captions and sound notes | `monarch video-storyboard` / `monarch make-video` produce **previz/animatic**, not an edit of real licensed clips. The current CLI has no general external-footage assembly path; use an actual editor and record its EDL. |
| 10 | MIX AUDIO | `output/<slug>/mix.wav` (VO/SFX/music plan and final mix) | `monarch sfx --kind ...` / `monarch mix --vo ... --duration 60 --out ...` may assist if the inputs fit. Check actual clip audio and finish/verify in an editor or DAW as needed. |
| 11 | RENDER | Final `output/<slug>/*.mp4`, real licensed footage, 9:16, 1080×1920, 30fps | **Current engine blocker:** `monarch render <dir>` renders the base `make-video` previz frames + audio; it does not assemble imported wildlife clips. Do not call a previz MP4 the final deliverable. Use a real footage-capable editor/export path or report Stage 11 blocked. |
| 12 | PACKAGE | `output/<slug>/12_package.md` with title, alternatives, copy and conversion path | `monarch package <render-dir> --shorts --title ...` generates a launch kit for a compatible render directory; inspect it and supplement tags, hashtags and platform-specific captions. |
| 13 | DELIVER | All 17 items in `delivery.md` + completed `output/<slug>/17_upload_checklist.md` | A human uploads to YouTube. The CLI command `monarch upload <file>` is a file/release transfer, **not** YouTube publishing. |

The command names above are registered in the current CLI, but a command may only assist one
part of a stage. Verify output against the artefact. Do not invent commands or claim external
footage, private analytics or licensing were processed when they were not.

---

## 3. APPROVAL GATES — STOP AND WAIT HERE

The base Monarch WAIT law still applies. **Continue after approval; do not terminate the whole
workflow at a research list, idea or script.** A wait gate is a human quality control point,
not an excuse to abandon the assignment.

- **Gate A — after Stage 6:** show selected rights-cleared scenes, scores, storyline spine
  and title promise. Wait for `perfect | improve`. Do not script before approval.
- **Gate B — after Stage 7:** present the Fountain script + numbered timecoded board. Wait for
  `perfect | improve`. Do not produce final VO/edit from an unapproved script.
- **Gate C — after Stage 9:** present storyboard/EDL and VO recommendation. Wait for explicit
  `haan` before final production/export. The approval does not bypass the external-footage
  renderer limitation in Stage 11.
- **Gate D — after the actual final export:** show QC results and preview. Wait for
  `perfect | reedit`; fix all failures before packaging.
- **Gate E — after cover/metadata package:** present the cover and full package. Wait for
  `approve | redo`. Then hand over to the human uploader. The agent never publishes.

Between approval gates, run the stages in order without stopping for a decorative update.
If a rights or tooling block prevents a stage, report it honestly and request only the action
needed to unblock it.

---

## 4. NO-STOP-AT / BLOCKED LAW

```
DO NOT END THE WORKFLOW AT IDEAS.
DO NOT END THE WORKFLOW AT LINKS.
DO NOT END THE WORKFLOW AT A SCRIPT.
DO NOT END THE WORKFLOW AT A RESEARCH LIST.
```

Research links must become traced source candidates; candidates must become scored and
rights-cleared selections; approved scripts must progress through VO/edit/mix/export/package.
But never pretend an unavailable tool or human licence has completed its stage.

A blocked stage is reported plainly, for example:

```
BLOCKED — Stage 5 (rights)
Scene:   S03 — <source lead>
Reason:  written permission is not on file; licensing is a human action
Need:    obtain licence with proof, or drop this scene
Effect:  S03 cannot enter selection; continue only if enough other elite licensed scenes remain
```

Stage 11 currently has a known external-footage assembly limitation. If the operator has not
provided an editor/export path capable of using licensed clips, state `BLOCKED — Stage 11`; do
not use AI wildlife visuals or a base-agent previz render as a substitute.

---

## 5. WHAT THIS WORLD CHANGES VS NORMAL MONARCH

| Thing | `monarch activate` (base, unchanged) | Monarch Cam world |
|---|---|---|
| Niche/channel | asked in intake | fixed — wildlife, two pillars |
| Language | asked in intake | English (US/UK) |
| Ratio | asked in intake | 9:16, 1080×1920, 30fps |
| Length | asked in intake | assignment decides (this brief: 60s Short) |
| Analytics | researched per task | operator-supplied snapshot + current Studio refresh; not automatically fetched |
| Title/brand law | base gates | base gates **plus** `identity.md` / `packaging.md` |
| Footage | base previz pipeline | real footage only; source ledger + written rights required |
| Export | base previz renderer | needs an external licensed-footage edit/export path; current CLI cannot assemble it |

Access protection, base constitution, script approval, HAAN, QC, packaging approval and human
upload remain in force. A world may add gates, never weaken them.

---

## 6. RETURN TO BASE MODE

No persistent world-mode switch was implemented (docs-only scope). For unrelated work, use
the existing normal `monarch activate` path. Select Monarch Cam only when the operator
explicitly names this world/loads this contract. Do **not** use `monarch lock` to switch
worlds: that locks the whole agent. A future router can add per-task selection without
changing the normal intake.
