# Full overall Monarch workflow (do not skip)

## Entry and workflow choice

- Generic natural-language `monarch activate` first shows the two-option workflow selector in
  `BOOT.md`; choose **Monarch Activate 💀** for this overall workflow or **Monarch Cam** for the
  wildlife world. The selector stops and waits before any intake/setup questions.
- Direct overall shortcut: **`monarch activate 💀`**. Direct Cam shortcut:
  **`monarch cam activate`**.
- The terminal `monarch activate <key>` is a separate CLI access command.

## Laws that apply in every workflow

- **Access first, key silent:** the key check happens before any workflow step, and the key is
  never repeated or displayed in a reply — not even as a confirmation.
- **Replies:** simple Roman Urdu, concise; milestone updates max 5 bullets; results chat mein bhi.
  No long dumps, pasted tool logs, duplicate/scratch files, or separate licence-request files.
- **Cam entry:** ask topic · ratio · length in simple Roman Urdu, then WAIT. Bear/door brief is
  provisional; ideas maange to 10 ideas do aur pick ka wait karo. Never choose topic, ratio, or
  length for the operator.
- **Cam Stages 1–6:** one `output/<slug>/project_notes.md` with per-stage sections — chhe alag
  reports nahi.
- **Inspection before claims:** no clip score, shortlist, or review claim without visual
  inspection. Not viewable → `NOT SCORED`; try another permitted candidate, then ask once for an
  accessible upload/source. No scene-specific script/VO/EDL for unseen footage; EDL source times
  must be verified and `TBD` never counts as a complete edit.
- **Rights honesty:** analysis/planning may continue while rights are unknown, but it is written
  as `RIGHTS UNKNOWN` — never claimed as clearance. No vendor contact, licence request, or
  payment without explicit authorization.
- **Approval phrase:** “aage barho/continue” approves only the current creative gate — never
  missing intake, unchosen options, rights approval, vendor contact, or publication permission —
  and it never sets `OPERATOR APPROVED WITH RISK NOTED` (named risk + explicit acknowledgement).
- **Question discipline:** ask only the current stage's question; destination URL, editor, VO,
  and disclosure are not Gate A questions, and a missing destination URL is not an early blocker.
- **Renderer truth:** `monarch render` makes a previz, not the final edit of imported footage.
  State this in one short line before any final-video promise; never present previz or AI visuals
  as a finished video.

## Overall workflow after selection

1. **Intake (4):** channel or niche · ratio · short/long · language. STOP.
2. **Forensic:** YouTube scrape + high-search/low-competition keywords + winner DNA.
3. **Ideas:** 10 gated + TOP 1 with reasons. STOP. Pick.
4. **Script forensic** of winning retention, then our script — authored as `.fountain`, gated by
   `monarch screen-script` into numbered scenes with `[n words]` exact and duration = words / wps
   (see `docs/FOUNTAIN_M3.md`). STOP. perfect | improve.
5. **Character + boards.** Recommend VO artist for this idea. STOP. video haan?
6. **Render first pass already dense:** 2–3s scene changes, match-cuts, premium SFX, transitions, keyframe motion. Present the **mp4** (`present_file`) + preview bind `0.0.0.0`. HTML fake-download = miss. (Base-agent previz only — it is not a final edit of imported footage.)
7. **QC.** STOP. perfect | reedit.
8. **Thumbs** (postage, FOMO). STOP. approve | redo.
9. **Titles + description + tags.** STOP. Human uploads.

Self-QC every deliverable. Log misses. Never invent niche on activate. Never jump to video.
