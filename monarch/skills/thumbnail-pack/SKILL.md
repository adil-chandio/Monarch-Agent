---
name: thumbnail-pack
description: >
  Produce 2-3 gated thumbnail briefs that win the 0.1s thumb-stop reflex
  (N1): one focal point, grayscale-readable contrast, eye-like element,
  empty upper third for the editor headline, gate-title PASS. Use at
  M6_thumbs or when the operator asks for thumbnails/packaging.
---

# Skill: thumbnail-pack — N1 thumb-stop briefs (gated)

## When to use

- Video/animatic approved; packaging time (`M6_thumbs`).
- Rethinking an underperforming video's packaging (with `learn` data).

## Inputs

- `TOPIC` and the approved title (or title candidates from `metadata-seo`).

## Steps

1. Pull the scene-1 visual family — thumb and frame one must match (N1):
   ```
   monarch video-storyboard --topic "$TOPIC" --json
   ```
   (`scenes[0].visual` + `retention_role: hook`)
2. Write 2–3 briefs. Each must pass the checklist:
   - exactly **one focal point** (two = zero)
   - contrast readable **in grayscale**
   - an eye-like element (two bright dots in a dark mass) used honestly
   - motion implied (snap-zoom / entering object), not static beauty
   - **empty upper third** reserved for the editor headline (L4 pairing)
   - the emotion carries the title's click debt — no bait-and-switch
3. Generate the images OUTSIDE clip prompts (L4: text/labels are editor jobs,
   never baked into generation prompts).
4. Gate the title+thumb pairing:
   ```
   monarch gate-title --title "$TITLE" --thumb "$BRIEF"
   ```
5. Present the briefs and **STOP** (`M6_thumbs`): `approve | redo`.

## Guardrails

- No baked text in any generation prompt (L4 — hard fail).
- Contrast first, meaning second, detail never.

## Handoff

Approved brief → `metadata-seo` (P3_listing).
