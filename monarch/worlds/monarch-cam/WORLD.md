# MONARCH CAM — WORLD CONTRACT

This file is the channel workflow contract. The other Markdown files in this folder supply
its identity, audience/context, rules, sourcing, claim-risk process, packaging, delivery, and
current assignment.

---

## 0. WIRED ADDITIVE TRIGGER

The natural-language activation phrase is:

```
monarch cam activate
```

**Integration status:** this explicit phrase is routed by the additive activation rules in
`BOOT.md`, `AGENT.md`, and `CLAUDE.md`. It loads this world after the existing access check.
This is an agent instruction, **not** a shell or CLI command; there is no `monarch cam`
subcommand.

The existing access-key rule in `monarch/constitution/00_IDENTITY.md` applies before either
route. If the key is not verified, use Monarch's standard refusal message and stop. The Cam
route never bypasses the access law.

The generic `monarch activate` trigger first shows the workflow selector in
`monarch/constitution/09_INTAKE.md`. Choosing **Monarch Cam** loads this world; the explicit
`monarch cam activate` phrase is a direct shortcut. Choosing **Monarch Activate 💀** (or using
that explicit shortcut) enters the original overall workflow and its same four intake questions.

For Cam, skip only facts fixed by this world and the active assignment. The selector does not
replace any safety, evidence, human approval, QC, WAIT, or human-publishing gate.

---

## 1. BOOT SEQUENCE (when this world is explicitly selected)

1. Confirm access key under the existing Monarch law.
2. Read in order: `identity.md` → `analytics.md` → `audience.md` → `rules.md` →
   `sources.md` → `claim-risk.md` → `packaging.md` → `delivery.md`.
3. List `assignments/` and load the active brief. If none is active, ask the operator for one;
   **do not invent a topic**.
4. After the explicit trigger has passed the access check and this context is loaded, say
   **MONARCH CAM — WORLD ACTIVE**.
5. Start Stage 1. No greeting, no generic intake questions for facts fixed by this world.
   Use the active assignment for topic/length; if none exists, ask for a brief. Still ask for
   missing evidence that is genuinely required to proceed.

---

## 2. THE 13-STAGE PIPELINE (sequence is law)

Every stage produces the named artefact. A tool command can assist but does not prove that a
stage is complete. Never claim a tool did work it cannot do. The supplied channel snapshot is
context, not a mandatory refresh/import step. Use fresh Studio data only when the operator
supplies or asks for it; the footage search must not wait on analytics. Later stages use the
assignment brief and actual source files.

| # | Stage | Required artefact | Tooling / honest limitation |
|---|---|---|---|
| 1 | ANALYSE CHANNEL CONTEXT | `output/<slug>/01_channel_analysis.md` | Start from the supplied channel snapshot and audience context. `monarch learn ingest <csv_file>` imports Studio CSV/TSV performance rows; `monarch learn log` lists logged rows. `monarch vitals <render-dir>` is a per-video post-launch sheet, not a private channel-wide analytics fetch. A fresh import is optional unless requested/relevant. |
| 2 | DISCOVER & LOG REAL FOOTAGE | `output/<slug>/02_footage_candidates.md` with exact queries, lanes, counts actually reviewed, candidates, duplicates, and coverage limits | `monarch search <query>` (YouTube), `monarch wsearch <query>`, `monarch rsearch <query>`, `monarch scrape <url>` may assist where permitted; tools/network can fail. Public links are leads only. Do not bypass access controls or automate against a site whose terms prohibit it. |
| 3 | TRACE SOURCE & CONTEXT | `output/<slug>/03_footage_ledger.md` with lead/repost → upstream source → filmer/rightsholder chain, dates, place, context, and evidence | `monarch scrape <url>` / `monarch transcript <id>` may assist. Manually verify the original/context where possible; an earliest found post is not automatically the original. Never infer ownership from a repost. |
| 4 | SCORE FOOTAGE QUALITY | `output/<slug>/04_scene_scores.md` — 10 evidence-backed scores + mean; shortlist only ≥8.5/10 with critical floors | Score manually from the actual moment and intended crop. `monarch fit <line> --n N` checks script/timing fit, **not** footage quality. Keep rights/claim risk out of the creative score. |
| 5 | QUICK CLAIM-RISK / RIGHTS SCREEN | Candidate-card status and check log per `claim-risk.md`; record rights evidence separately | A quick public search can flag a known repost, restriction, or match; it cannot clear a clip or query all Content ID references. `NO MATCH FOUND` is not permission or claim-free status. |
| 6 | SELECT ELITE SCENES | `output/<slug>/06_scene_selection.md` + evidence-backed storyline spine and explicit source/risk labels | `monarch gate-idea --title ... --hook ... --itch ... --visual ...` can gate the premise; a human confirms the selected source clips and their remaining uncertainty. |
| 7 | WRITE SCRIPT | `output/<slug>/screenplay.fountain` + numbered, timed scene board | `monarch maths --seconds 60`, `monarch screen-script`, `monarch script-fountain`, `monarch humanize`. Natural English, factual narration, exact clip linkage; no unsupported motive, chronology, or location. |
| 8 | CREATE VOICE-OVER | `output/<slug>/vo.wav` (normalize/copy backend output into this deliverable) | `monarch voiceover --script-file ... --out ...` only with an approved real voice backend. Placeholder/mumble audio is never final. |
| 9 | EDIT | `output/<slug>/09_edl.md` — exact source in/out, sequence, captions, and sound notes | `monarch video-storyboard` / `monarch make-video` produce **previz/animatic**, not an edit of external wildlife footage. The current CLI has no general external-footage assembly path; use an actual editor and record its EDL. |
| 10 | MIX AUDIO | `output/<slug>/mix.wav` (VO/SFX/music plan and final mix) | `monarch sfx --kind ...` / `monarch mix --vo ... --duration 60 --out ...` may assist if the inputs fit. Check original clip audio and finish/verify in an editor or DAW as needed. |
| 11 | RENDER | Final `output/<slug>/*.mp4`, real footage, target 9:16, 1080×1920, 30fps | **Current engine blocker:** `monarch render <dir>` renders the base `make-video` previz frames + audio; it does not assemble imported wildlife clips. Do not call a previz MP4 the final deliverable. Use a real footage-capable editor/export path or report Stage 11 blocked. |
| 12 | PACKAGE | `output/<slug>/12_package.md` with title, alternatives, copy, and conversion path | `monarch package <render-dir> --shorts --title ...` generates a launch kit for a compatible render directory; inspect it and supplement tags, hashtags, and platform-specific captions. |
| 13 | DELIVER & PRE-PUBLISH CHECK | All 17 items in `delivery.md` + completed `output/<slug>/17_upload_checklist.md` | A human handles YouTube Studio upload/checks and the final publish decision. The CLI command `monarch upload <file>` is a file/release transfer, **not** YouTube publishing. Studio checks can take time and are not final rights clearance. |

The command names above are registered in the current CLI, but a command may only assist one
part of a stage. Verify output against the artefact. Do not invent commands or claim external
footage, private analytics, licences, or platform checks were processed when they were not.

---

## 3. APPROVAL GATES — STOP AND WAIT HERE

The base Monarch WAIT law still applies. **Continue after approval; do not terminate the whole
workflow at a research list, idea, or script.** A wait gate is a human quality-control point,
not an excuse to abandon the assignment.

- **Gate A — after Stage 6:** show selected highest-scoring scenes, score evidence, source/context
  confidence, rights and claim-risk labels, unresolved questions, and storyline spine/title
  promise. Wait for `perfect | improve`. Do not script before approval.
- **Gate B — after Stage 7:** present the Fountain script + numbered timecoded board. Wait for
  `perfect | improve`. Do not produce final VO/edit from an unapproved script.
- **Gate C — after Stage 9:** present storyboard/EDL and VO recommendation. Wait for explicit
  `haan` before final production/export. The approval does not bypass the external-footage
  renderer limitation in Stage 11.
- **Gate D — after the actual final export:** show QC results and preview. Wait for
  `perfect | reedit`; fix all failures before packaging.
- **Gate E — after cover/metadata package:** present the cover and full package. Wait for
  `approve | redo`. Then hand over to the human uploader. The human runs YouTube Studio Checks
  on the intended final draft and makes the publish decision; the agent never publishes.

Between approval gates, run the stages in order without stopping for a decorative update.
If source, risk evidence, or tooling is incomplete, report it honestly and request only the
action needed to decide or unblock it.

---

## 4. NO-STOP-AT / BLOCKED LAW

```
DO NOT END THE WORKFLOW AT IDEAS.
DO NOT END THE WORKFLOW AT LINKS.
DO NOT END THE WORKFLOW AT A SCRIPT.
DO NOT END THE WORKFLOW AT A RESEARCH LIST.
```

Research links must become deduplicated, source/context-checked candidates; candidates must
become genuinely elite, scored selections with honest rights/claim-risk labels; approved scripts
must progress through VO/edit/mix/export/package. An unverified rights status must remain
visible—it is not renamed “clear.” An explicit no-reuse restriction is a stop for that use
unless a suitable grant exists; a quick-screen match is a review alert, not an automatic
rejection. If rights are unknown or a final Studio claim appears, request a human decision:
choose another source, seek permission, remove/replace the claimed segment, accept the platform
claim impact where available, or do not publish. Do not give legal assurance.

Report a source/context block plainly, for example:

```
BLOCKED — Stage 3 (source/context)
Scene:   S03 — <source lead>
Reason:  source chain or material story claim cannot be verified
Need:    locate the filmer/credible reporting, rewrite to what is verified, or drop the scene
Effect:  do not use S03 as factual proof; continue scouting if needed
```

A rights/claim review can instead be recorded without blocking discovery:

```
REVIEW REQUIRED — Stage 5 (rights / claim risk)
Scene:   S03 — <source lead>
Status:  RIGHTS UNKNOWN; NO MATCH FOUND IN CHECKED SOURCES
Limit:   this is not permission or a guarantee against a later claim
Need:    operator chooses another source, seeks permission, or explicitly records a risk decision
```

Stage 11 currently has a known external-footage assembly limitation. If no editor/export path
capable of using the actual source files is available, state `BLOCKED — Stage 11`; do not use
AI wildlife visuals or a base-agent previz render as a substitute.

---

## 5. WHAT THIS WORLD CHANGES VS NORMAL MONARCH

| Thing | Monarch Activate 💀 — overall workflow | Monarch Cam world |
|---|---|---|
| Activation | selected from the `monarch activate` menu or invoked directly | selected from the menu or invoked with `monarch cam activate` |
| Niche/channel | asked in intake | fixed — wildlife, two pillars |
| Language | asked in intake | English (US/UK) final narration |
| Ratio | asked in intake | target 9:16, 1080×1920, 30fps when source/tooling support it |
| Length | asked in intake | assignment decides (this brief: 60s Short) |
| Analytics | researched per task | supplied snapshot/audience as context; refresh only when supplied or asked for; never blocks footage search |
| Title/brand law | base gates | base gates **plus** `identity.md` / `packaging.md` |
| Footage | base previz pipeline | real footage; search log, source/context ledger, separate rights/claim-risk screen |
| Export | base previz renderer | needs a real external-footage edit/export path; current CLI cannot assemble it |

Access protection, base constitution, script approval, HAAN, QC, packaging approval, human
YouTube upload, and WAIT gates remain in force. A world may add gates, never weaken them.

---

## 6. RETURN TO BASE MODE

World selection is per activation request; it does not permanently switch the agent's runtime
state. For unrelated work, use `monarch activate` and choose **Monarch Activate 💀**, or use
`monarch activate 💀` as the direct overall-workflow shortcut. Select Monarch Cam from the same
menu or use `monarch cam activate` directly. Do **not** use `monarch lock` to switch worlds:
that locks the whole agent. The overall four-question intake remains unchanged after selection.
