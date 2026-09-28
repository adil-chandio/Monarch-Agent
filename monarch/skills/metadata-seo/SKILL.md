---
name: metadata-seo
description: >
  Close the listing: 8+ title candidates from the T1-T8 formulas, generic-ban
  kill, gate-title PASS, click-debt cross-check against the script board,
  description with value-debt line, audience-language tags. Use at P3_listing
  or when the operator asks for title/description/tags.
---

# Skill: metadata-seo — title, description, tags (gated)

## When to use

- Thumbnail approved; listing time (`P3_listing`).
- Retitling after `learn` signals say the packaging underperformed.

## Inputs

- `TOPIC`, the script board (`board.json`), the forensic notes from `forensic-hunt`.

## Steps

1. Draft **≥ 8 candidates** from `monarch/playbook/growth_formulas.md`
   (T1–T8). Kill anything matching `GENERIC_TITLE_BANS`
   (`monarch/schemas.py`) on sight.
2. Cross-check the winner's click debt against the board: the promised payoff
   must be **literally spoken** in a scene's `vo_line`. Not there? New title.
3. Gate it:
   ```
   monarch gate-title --title "$TITLE" --thumb "$THUMB_BRIEF"
   ```
   (≤ 70 chars, no banned patterns, payoff present, thumb exists.)
4. Description (in this order): hook line → proof line (the strongest number
   from the board) → 2–3 line summary → value-debt line (N4: the subscribe
   ask rides a delivered payoff, never cold).
5. Tags: 8–15 from the audience's own words (Reddit/X mining in F0), not
   jargon. Include the niche + the specific entities of this video.
6. Run packaging QC before presenting:
   ```
   monarch qc notes.json --stage packaging
   ```
7. Present and **STOP** (`P3_listing`): `approve metadata`.

## Guardrails

- Privacy stays `private`. Upload is human, always.
- No tag/title claims the video does not deliver (trust law, N4).

## Handoff

Approved → `DONE_human_upload`. After upload, use the `upload-day` skill.
