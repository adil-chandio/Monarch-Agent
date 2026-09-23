---
name: forensic-hunt
description: >
  Turn a niche into 10 gated ideas plus a TOP 1 with forensic reasons: upstream
  tool health, YouTube outliers, Reddit/X audience language, Exa semantic web,
  then gate every idea. Use when entering F0_forensic_hunt / M2_ideas_plus_top1,
  or when the operator says "ideas nikalo", "hunt this niche", or gives a new channel.
---

# Skill: forensic-hunt — niche → 10 ideas + TOP 1 (gated)

## When to use

- New channel/intake done (`I0_intake` answered) and it's hunt time.
- Existing channel wants a fresh idea batch.

## Inputs

- `NICHE` (required) — e.g. "history mysteries", "deep sea facts".

## Steps

1. Health-check upstream tools and say what's missing out loud:
   ```
   monarch doctor
   ```
2. Mine the niche across platforms (missing tools = skip honestly, never fake):
   ```
   monarch hunt "$NICHE"
   monarch search "$NICHE"
   monarch rsearch "why is $NICHE so scary"
   monarch xsearch "$NICHE"
   monarch wsearch "least known $NICHE facts with evidence"
   ```
3. Dissect the best outlier for structure + gap:
   ```
   monarch scrape "$OUTLIER_URL" --transcript
   ```
4. Draft **10 ideas** as Idea records (title / hook / itch / visual anchor).
   Gate each one — a FAIL idea is dead, fix it or drop it:
   ```
   monarch gate-idea --title "$T" --hook "$H" --itch "$I" --visual "$V"
   ```
5. Rank with 3 numeric reasons each (outlier multiplier, search-vs-competition,
   freshness). Nominate TOP 1.
6. Present all 10 + TOP 1 and **STOP** (`M2_ideas_plus_top1`):
   `pick number or haan on TOP 1`.

## Guardrails

- `factual: true` or the idea dies. No clone_of. Click debt named per title
  (T1–T8 in `monarch/playbook/growth_formulas.md`).
- Psychology itch must be named (`monarch/packaging/psychology.md`).

## Handoff

Approved TOP 1 → the `make-short` skill (or full ladder via Script Doctor, M3).
