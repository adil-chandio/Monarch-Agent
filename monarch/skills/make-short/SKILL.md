---
name: make-short
description: >
  Take one topic end-to-end into a gated 9:16 short: maths line, Neuro-Playbook
  storyboard, Fountain screenplay, psychoacoustic SFX, Ken Burns previz animatic
  and the HAAN-gated stop before any final render. Use when the operator says
  "make a short on X", "is topic pe video banao", or approves a TOP 1 idea.
---

# Skill: make-short — topic → gated previz short

Monarch builds **previz animatics** (frames + SFX + timeline). The final
footage render is HAAN-gated and the upload is always human.

## When to use

- Topic approved (post `M2_ideas_plus_top1`) and target is short-form (9:16, 40–60s).
- Re-running an existing topic with a new `--seed` or `--cohort`.

## Inputs

- `TOPIC` (required) · `COHORT` kids|genz|adults (default genz) · `LENGTH` seconds (default 60)

## Steps

1. Fix the maths line first — it owns every word count:
   ```
   monarch maths --seconds $LENGTH
   ```
2. Generate the gated screenplay + Hollywood box card (director runs the real
   M3 gate internally; if it FAILs, fix the topic/length — never force it):
   ```
   monarch script --topic "$TOPIC" --cohort $COHORT --out output/$SLUG/screenplay.fountain --card
   ```
3. Show the operator the box card and the storyboard, then STOP for approval:
   ```
   monarch video-storyboard --topic "$TOPIC" --cohort $COHORT
   ```
   (WAIT law: `perfect | improve` — improve = new `--seed` or better topic phrasing.)
4. On approval, build the animatic (frames + sfx + timeline + manifest):
   ```
   monarch make-video --topic "$TOPIC" --out output/$SLUG --cohort $COHORT --seed $SEED
   ```
5. Verify the manifest honestly:
   - `scene_count` == the maths line's scene count
   - `total_s` within one clip of `LENGTH`
   - the `silence-sting` scene exists with `silence_before_s: 0.3`
6. Present `manifest.json` + `storyboard.txt` to the operator. Final render
   requires HAAN (`monarch haan haan --action render`) — same as always.

## Fail-closed

- Director `FAIL` = the playbook refused the board. Rewrite or re-seed — never ship.
- No HAAN, no render. No upload, ever, by the agent.

## Handoff

Log reality after upload: `monarch learn record ...` (see the `upload-day` skill),
then `monarch memory save`.
