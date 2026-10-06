---
name: premium-2d-motion-edit
description: >
  Use for Style B frame-rendered stickman films when a brief explicitly needs
  character animation, walk cycles, gestures, a consistent character, exact VO
  sync, frame-perfect timing, no AI drift, or zero generative drift. Style A remains the
  default for photoreal or illustrated scenes, many locations, speed, or cost.
---

# Skill: premium-2d-motion-edit — Style B frame renderer

This is a **new, additive Style B**. It does not replace, rewrite, or change
Style A, `make-short`, or any other existing skill. Read the companion
[engine reference](ENGINE_REFERENCE.md) before implementing a Style-B shot.

## Style router — choose before production

- **Style B** only when the brief explicitly asks for character animation,
  walk cycles or gestures, character consistency, exact VO sync, frame-perfect
  timing, or no generative drift.
- **Style A** when the brief asks for photoreal/illustrated scenes, many
  locations, fast/cheap production; **Style A is also the default** when no
  Style-B trigger appears.
- Style A's still-image generation, compile, camera moves, transitions,
  captions, prompts, and workflow are untouched. Do not silently migrate an
  existing Style-A project to Style B.
- Style B draws every 1080×1920 frame in code (Python + Pillow); no generated
  stills. It is appropriate when deterministic character animation and
  picture-to-voice timing matter more than cost or turnaround.

## Workflow

1. **Confirm the route and approvals.** Follow Monarch's existing intake,
   per-stage WAIT, rights, HAAN, and human-upload laws. A style choice is not
   approval to render, publish, or skip any gate.
2. **Freeze the timing contract before drawing.** Use measured VO lengths,
   a per-scene fit, exact frame boundaries, and the reference's 30 fps / 1110
   frame schedule. If target duration changes, re-fit each scene's `atempo`;
   never trim, cross-fade, or stretch the full mix to conceal a mismatch.
3. **Lock the art direction.** Use the reference's character palette, chapter
   accents, safe-area grid, one-cluster-per-scene rule, single tinted
   transition, and character sheet. No more than three on-screen colours:
   paper, ink, one chapter accent.
4. **Build animation from pure time functions.** Use the 3D body-space rig,
   perspective, depth ordering, joint clamps, biomechanical poses, foot-ground
   solve, and secondary motion in `ENGINE_REFERENCE.md`. Do not substitute a
   flat picture-plane rig or reuse a pose dictionary from another rig.
5. **Iterate with pixel evidence.** After every logical patch: assert the new
   token/value exists, re-render, inspect the image, then continue. Inspect a
   6×2 all-scene contact sheet and an 8-pose character strip; do not approve
   an unseen render.
6. **Measure the actual encoded output.** Run video, audio, contrast, safe-area,
   and cut-sync telemetry from the reference. Compare VO and bed as separate
   stems, never by measuring their summed mix. Fix failures and repeat the
   measurements on the delivered MP4.
7. **Package honestly.** Ship only artifacts that exist and have passed their
   checks. Record the MP4 SHA-256 prefix, before→after numbers, measured audit,
   character sheet, event ledger, QA contact sheet, and restore points for any
   rewritten source files. Never claim a gate passed from a plan or preview.

## Non-negotiable Style-B laws

- Premium is subtraction: one motion-graphic cluster per scene; no second
  cluster, spare decoration, or unexplained object.
- Character colours never change. Only chapter/world accents may change.
- Every frame has restrained motion; no still holds, quantized camera crop, or
  shake. Secondary animation and camera movement must be deterministic from
  absolute time so parallel shards meet bit-identically.
- Safe content bounds are **y=180…1500** on a 1080×1920 canvas. Platform
  chrome above and below is dead space.
- Every text/accent pair must meet **4.5:1** contrast; transitions tint the
  paper instead of flooding the frame. Avoid luma flashes and strobe-like cuts.
- Do not ship if any QA-gate item in `ENGINE_REFERENCE.md` fails. State
  `NOT MEASURED` when tooling or source stems are unavailable; never fabricate
  telemetry.

## Implementation boundary

This card is a production contract, not a claim that a new Style-B CLI or a
complete renderer has been added to Monarch. Use only files and commands that
exist in the active project. Monarch's existing `monarch/video/stickman_art.py`
and `art-anim` are a separate, simpler art path; do not represent them as
implementing the full 3D Style-B engine. Keep Style A operational and unchanged.
