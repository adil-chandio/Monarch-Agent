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
3. Ask the three Cam entry questions in simple Roman Urdu and **STOP / WAIT**:
   **topic** (kya banana hai?) · **ratio** (9:16 ya 16:9?) · **length** (kitne seconds/minutes?).
   The briefs in `assignments/` are **provisional** — a brief is not a chosen topic.
4. If the operator asks for ideas instead, give **10 ideas** and WAIT for the pick. Never choose
   the topic, ratio, or length for the operator.
5. After the answers, say **MONARCH CAM — WORLD ACTIVE** and start Stage 1 with the confirmed
   topic/ratio/length (or the operator-selected idea). No greeting, no generic intake questions
   for facts fixed by this world, and no stage work before the operator answers. Still ask for
   missing evidence that is genuinely required to proceed.
6. **Har stage ke baad RUKO:** short update do (easy Roman Urdu, max 5 bullets), phir agle stage
   ki ijaazat maango (`Aage barhoon?`) aur WAIT karo. Bina ijaazat agla stage, naya file, ya naya
   tool-run shuru mat karo. Koi bhi choice (topic, ratio, length, idea, scene, script, title,
   voice) khud mat pick karo — har cheez operator se poochho.

---

## 2. THE 13-STAGE PIPELINE (sequence is law)

Every stage produces the named artefact. A tool command can assist but does not prove that a
stage is complete. Never claim a tool did work it cannot do. The supplied channel snapshot is
context, not a mandatory refresh/import step. Use fresh Studio data only when the operator
supplies or asks for it; the footage search must not wait on analytics. Later stages use the
confirmed brief and actual source files.

**Stages 1–6 research lives in ONE file:** `output/<slug>/project_notes.md`, with one section per
stage (`## 1. …` through `## 6. …`). Do **not** create six separate reports. No clip score,
shortlist, or review claim without actual visual inspection — unwatched footage is `NOT SCORED`.

**Path law:** this is the **repo root** `output/<slug>/project_notes.md` — *not* `monarch/output/`.
Create the slug folder once and keep every stage's section inside that single file.

| # | Stage | Required artefact | Tooling / honest limitation |
|---|---|---|---|
| 1 | ANALYSE CHANNEL CONTEXT | `output/<slug>/project_notes.md` → `## 1. Channel context` | Start from the supplied channel snapshot and audience context. `monarch learn ingest <csv_file>` imports Studio CSV/TSV performance rows; `monarch learn log` lists logged rows. `monarch vitals <render-dir>` is a per-video post-launch sheet, not a private channel-wide analytics fetch. A fresh import is optional unless requested/relevant. |
| 2 | DISCOVER & LOG REAL FOOTAGE | `output/<slug>/project_notes.md` → `## 2. Footage candidates`: exact queries, lanes, counts actually reviewed, candidates, duplicates, and coverage limits | `monarch search <query>` (YouTube), `monarch wsearch <query>`, `monarch rsearch <query>`, `monarch scrape <url>` may assist where permitted; tools/network can fail. Public links are leads only. Do not bypass access controls or automate against a site whose terms prohibit it. |
| 3 | TRACE SOURCE & CONTEXT | `output/<slug>/project_notes.md` → `## 3. Source & context ledger`: lead/repost → upstream source → filmer/rightsholder chain, dates, place, context, and evidence | `monarch scrape <url>` / `monarch transcript <id>` may assist. Manually verify the original/context where possible; an earliest found post is not automatically the original. Never infer ownership from a repost. |
| 4 | SCORE FOOTAGE QUALITY | `output/<slug>/project_notes.md` → `## 4. Scene scores`: 10 evidence-backed scores + mean; shortlist only ≥8.5/10 with critical floors. Unwatched footage is `NOT SCORED`, never scored or shortlisted. | Score manually from the actual moment and intended crop. `monarch fit <line> --n N` checks script/timing fit, **not** footage quality. Keep rights/claim risk out of the creative score. If a clip is not viewable, write `NOT SCORED`, try another candidate from permitted sources, and only then ask once for an accessible upload/source. |
| 5 | QUICK CLAIM-RISK / RIGHTS SCREEN | `output/<slug>/project_notes.md` → `## 5. Rights / claim-risk screen`: candidate-card status and check log per `claim-risk.md`; record rights evidence separately | A quick public search can flag a known repost, restriction, or match; it cannot clear a clip or query all Content ID references. `NO MATCH FOUND` is not permission or claim-free status. |
| 6 | SELECT ELITE SCENES | `output/<slug>/project_notes.md` → `## 6. Scene selection` + evidence-backed storyline spine and explicit source/risk labels | `monarch gate-idea --title ... --hook ... --itch ... --visual ...` can gate the premise; a human confirms the selected source clips and their remaining uncertainty. |
| 7 | WRITE SCRIPT | `output/<slug>/screenplay.fountain` + numbered, timed scene board | `monarch maths --seconds 60`, `monarch screen-script`, `monarch script-fountain`, `monarch humanize`. Natural English, factual narration, exact clip linkage; no unsupported motive, chronology, or location. Scene-specific script comes only from visually inspected, selected footage — never from unseen clips. |
| 8 | CREATE VOICE-OVER | `output/<slug>/vo.wav` (normalize/copy backend output into this deliverable) | `monarch voiceover --script-file ... --out ...` only with an approved real voice backend. Placeholder/mumble audio is never final. |
| 9 | EDIT | `output/<slug>/09_edl.md` — exact source in/out, sequence, captions, and sound notes | `monarch video-storyboard` / `monarch make-video` produce **previz/animatic**, not an edit of external wildlife footage. The current CLI has no general external-footage assembly path; use an actual editor and record its EDL. Every row needs verified source timecodes from inspected footage; a `TBD` row is not a complete edit. |
| 10 | MIX AUDIO | `output/<slug>/mix.wav` (VO/SFX/music plan and final mix) | `monarch sfx --kind ...` / `monarch mix --vo ... --duration 60 --out ...` may assist if the inputs fit. Check original clip audio and finish/verify in an editor or DAW as needed. |
| 11 | RENDER | Final `output/<slug>/*.mp4`, real footage, target 9:16, 1080×1920, 30fps | **Built-in CLI limitation:** `monarch render <dir>` renders the base `make-video` previz frames + audio; it does not assemble imported wildlife clips. A CLI limitation blocks that route only: use a real footage-capable editor/export path (for example, an available FFmpeg/editor workflow), verify the MP4, and follow §4 fallbacks if it fails. Never call a previz the final deliverable or stop at `BLOCKED`. If asked, state the built-in limitation briefly, then continue via an alternative. |
| 12 | PACKAGE | `output/<slug>/12_package.md` with title, alternatives, copy, and conversion path | `monarch package <render-dir> --shorts --title ...` generates a launch kit for a compatible render directory; inspect it and supplement tags, hashtags, and platform-specific captions. |
| 13 | DELIVER & PRE-PUBLISH CHECK | All 17 items in `delivery.md` + completed `output/<slug>/17_upload_checklist.md` | A human handles YouTube Studio upload/checks and the final publish decision. The CLI command `monarch upload <file>` is a file/release transfer, **not** YouTube publishing. Studio checks can take time and are not final rights clearance. |

The command names above are registered in the current CLI, but a command may only assist one
part of a stage. Verify output against the artefact. Do not invent commands or claim external
footage, private analytics, licences, or platform checks were processed when they were not.

---

## 3. APPROVAL GATES — STOP AND WAIT AT EVERY STEP

The base Monarch WAIT law still applies. **Continue after approval; do not terminate the whole
workflow at a research list, idea, or script.** A wait gate is a human quality-control point,
not an excuse to abandon the assignment.

### Per-stage permission law (Cam)

- **Har stage ke baad ruko.** Short update in easy Roman Urdu (max 5 bullets), then ask
  permission for the next stage and WAIT. The named gates A–E below are mandatory quality gates,
  but the ask applies to **every** stage — Stage 1 se pehle bhi aur har stage ke baad bhi.
- **Never self-start:** do not begin Stage 1, open a search, write a file, or run a stage tool
  until the operator has answered the entry questions and approved that step.
- **Never self-pick:** topic, ratio, length, idea, scene, script line, VO voice, title, cover
  text — har choice operator ki hai. Agent sirf options + apni recommendation de sakta hai, pick
  nahi kar sakta.
- **Ask, then wait:** `Aage barhoon?` / `Ijaazat?` — aur operator ka jawab aane tak ruk jao.
  Unclear jawab par sirf wahi sawal dohrayo, khud aage mat barho.
- **Stopping to ask is not "ending the workflow":** research list/idea/script ke baad workflow
  khatam nahi karna — magar agle stage se pehle ijaazat lena lazmi hai.

Example asks (chhote, Roman Urdu):

```
Stage 1 ke baad:  "Channel context ready — footage search shuru karun?"
Stage 2 ke baad:  "X candidates mile — source/context trace karun?"
Stage 3 ke baad:  "Source/rights status yeh hai — scoring karun?"
Stage 4 ke baad:  "Scores yeh — claim-risk screen karun?"
Stage 5 ke baad:  "Labels yeh — Gate A ke liye selection dikhaun?"
Stage 7 ke baad:  "Script ready — VO banau?"
Stage 8 ke baad:  "VO ready — edit/EDL banau?"
```

### Reply language & length (Cam)

- Saari baat-cheet, updates aur sawal **easy Roman Urdu (Urdu–English mix)** mein — short aur
  saaf. Sirf final deliverables (narration script, captions, titles/copy) English mein.
- Milestone update = **max 5 bullets**; koi bara paragraph, long chat dump, ya tool log nahi.
- Results chat mein bhi do (sirf file bana kar chup mat ho jao), magar chhote mein.

- **Question discipline:** at each gate ask only what that stage's decision needs. Never batch
  destination URL, editor, VO, or disclosure questions into Gate A; a missing destination URL is
  not an early blocker.
- **“Aage barho” / “continue”** approves only the current creative gate — never missing intake,
  unchosen options, rights approval, vendor contact, or publication permission. It never sets
  `OPERATOR APPROVED WITH RISK NOTED`; that status requires the operator's explicit
  acknowledgement of a **named** risk.
- **Gate A requires inspection:** candidates presented at Gate A must have been visually watched.
  Unwatched footage is `NOT SCORED` — never scored, shortlisted, or described as reviewed.
- **Gate A — after Stage 6:** show selected highest-scoring scenes, score evidence, source/context
  confidence, rights and claim-risk labels, unresolved questions, and storyline spine/title
  promise. Wait for `perfect | improve`. Do not script before approval, and do not ask future-stage
  questions (destination URL/editor/VO/disclosure) here.
- **Gate B — after Stage 7:** present the Fountain script + numbered timecoded board. Wait for
  `perfect | improve`. Do not produce final VO/edit from an unapproved script.
- **Gate C — after Stage 9:** present storyboard/EDL and VO recommendation. Wait for explicit
  `haan` before final production/export. The approval does not make a previz a final export; use
  the real-footage fallback path in §4 for Stage 11.
- **Gate D — after the actual final export:** show QC results and preview. Wait for
  `perfect | reedit`; fix all failures before packaging.
- **Gate E — after cover/metadata package:** present the cover and full package. Wait for
  `approve | redo`. Then hand over to the human uploader. The human runs YouTube Studio Checks
  on the intended final draft and makes the publish decision; the agent never publishes.

Run the stages in order and stop at **every** stage for a short update + permission (per-stage
law above). A stop is one short Roman Urdu message with the result and one question — not a long
report. If source, risk evidence, or tooling is incomplete, follow §4 to try lawful alternatives
first; if required user-only input remains, report it honestly and request only the action needed
to decide or unblock it.

---

## 4. COMPLETE THE WORK — NEVER REFUSE EDITING

For every operator-approved, rights-compliant video brief, carry the work through discovery,
authorized footage acquisition, production, final render, and delivery. A failed search, download
method, CLI command, or built-in renderer blocks only that route—not the assignment. Record the
limitation, try another lawful available path, and keep progressing. `BLOCKED` is a temporary route
status, never the end of the workflow or the final deliverable. This contract overrides any
subordinate checklist wording (including `delivery.md`) that treats a failed tool route as a
terminal `BLOCKED` outcome. The required final deliverable is an actual playable, QC-checked
rendered MP4; a plan, research list, script, EDL, storyboard, or previz is supporting work only
and never counts as completion.

### Required seven-step production pipeline

1. **Find clips.** Search permitted sources, inspect actual candidates, and log source, context,
   duplicates, and evidence. Never claim an unseen clip was inspected.
2. **Download usable footage.** Obtain the original/clean file through permitted access and only
   for an authorized intended use. If a preview is all that is available, ask for the source file
   or choose another licensed/authorized clip. Never bypass DRM, access controls, or site terms;
   do not remove a watermark to disguise a source or infer permission from a public link. Keep
   unresolved rights as `RIGHTS UNKNOWN`. Vendor contact, licence requests, and payment need
   explicit operator authorization.
3. **Write the script.** Ground narration in selected, visually inspected footage and verified
   context; pass the required script/scene approval gate before generating VO.
4. **Create the voice-over.** Use the operator-approved voice choice and an available real
   backend, render an actual audio file, and QC the speech; placeholders are not final.
5. **Compile.** Assemble footage, VO, verified timecodes, captions, and sound in an actual
   editable timeline using a suitable available editor. An EDL or storyboard alone is not a
   compiled video.
6. **Next-level edit.** Refine story, pacing, cuts, truthful crop, transitions, captions, mix, and
   sound; preserve context and complete visual/audio QC.
7. **Render and deliver.** Export the finished edit as `output/<slug>/*.mp4`, confirm it opens and
   matches the brief, and present the actual file with `present_file`. The rendered video is the
   primary deliverable—not a plan. Do not publish it; YouTube publishing remains human-only.

### Fallback and gate law

- When a route fails, try a different permitted source/download method, an operator-provided
  accessible file, or another available footage-capable editor/assembly/render path. Use a local
  FFmpeg workflow, another installed editor, or code-based assembly when suitable and permitted.
- If a candidate is unviewable, mark that candidate `NOT SCORED`, exclude it from scene-specific
  work, and continue scouting; do not make script/VO/EDL claims from unseen footage.
- If rights, source terms, or animal safety forbid a clip, replace it or seek a real grant through
  operator-authorized channels—never evade those controls. If a required user-only permission,
  decision, file, or setup is missing, ask one narrow question and WAIT at that gate, then resume
  when resolved. This is a pause for required input, not an end-of-work `BLOCKED`.
- All access, stage-by-stage WAIT, creative approval, rights, factuality, safety, QC, and human
  publication gates remain in force. No gate authorizes invented work, clearance claims, or
  bypassing approval. Never claim completion until the actual rendered file exists and passes QC.

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
