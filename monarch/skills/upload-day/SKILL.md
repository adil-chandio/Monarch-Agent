---
name: upload-day
description: >
  Final QC chain, HAAN-gated render handoff, human upload checklist, then
  closing the loop: log real metrics with learn record, distill signals into
  lessons, and save session memory for the next handoff. Use when the video
  is rendered/approved and it's upload time, or a session is ending.
---

# Skill: upload-day — QC → human upload → learn → memory

## When to use

- Final render ready (or previz approved for render).
- Any session end (memory save is mandatory — the Phase-8 lesson).

## Steps

1. Run the full QC chain and show both results:
   ```
   monarch qc notes.json --stage packaging
   monarch qc-render final.mp4 board.json
   ```
   Any miss = stop and fix. QC is fail-closed.
2. Final render needs the operator's HAAN, explicitly:
   ```
   monarch haan haan --action render
   ```
3. Present the mp4. **The human uploads.** Recommend a VO artist for the
   topic before any speech generation. Privacy default `private`.
4. After 48–72h, log reality (APV = avg % viewed from YT Studio):
   ```
   monarch learn record --topic "$TOPIC" --views $V --avg-pct $P \
           --cohort $COHORT --length $SECONDS --subs $S
   ```
5. Distill what the channel is learning (needs ≥ 3 logged videos):
   ```
   monarch learn log
   monarch learn distill --apply
   ```
   Signals enter `monarch/self_improve/lessons.md` under the 3x rule —
   provisional until repeated. Never promote one video to a law.
6. Close the session with memory (the handoff bridge):
   ```
   monarch memory save --state P3_listing --topic "$TOPIC" \
           --pending "upload confirmation" --notes "final at output/$SLUG"
   ```

## Guardrails

- No agent upload, ever (`DONE_human_upload` is the state; the human acts).
- Numbers come from YT Studio, not estimates — bad data poisons the loop.
- `memory save` before the session dies. Non-negotiable.

## Handoff

Next session starts with: `monarch memory restore` — and keeps walking.
