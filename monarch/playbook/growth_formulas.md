# Growth Formulas — agent memory

Every formula below is a **repeatable weapon**, not a suggestion.
Apply at full intensity. Fail = rewrite, never ship.

---

## Title formulas (T1–T8)

| ID | Name | Pattern | Psychology itch | Gate |
|----|------|---------|----------------|------|
| T1 | Curiosity gap | Cut the last word of the story. Leave the brain unable to close the loop. | Unfinished | Must be closed in first 8s of script |
| T2 | Number shock | One specific, wrong-feeling number dominates. "73 % of millionaires…" | Proof shock | Number must be sourced + spoken in VO |
| T3 | Forbidden peek | "They never show you this part of X" — only if X is real and the gap is real | Forbidden | Script must deliver the exact hidden part |
| T4 | Inverted belief | Challenge something the audience thinks is true. "Bears are not actually…" | Self-threat / Status | Script must prove the inversion with evidence |
| T5 | Identity mirror | "You have been doing X wrong your whole life" — second person, specific | Self-threat | Script must show the wrong way then the right way |
| T6 | Status secret | "Insiders know this one trick about X" — mechanism, not gossip | Status secret | Must explain the mechanism, not just tease |
| T7 | Scale WTF | Pair two things that should never share a frame. "A cockroach vs a nuclear reactor" | Incongruity | Visual anchor must be the scale joke |
| T8 | Time pressure | Genuine rarity or window. No fake countdowns. "Before X disappears" | FOMO | Must state *why* the window exists |

### Title generation rules

1. Generate **minimum 8 candidates** per idea.
2. Kill any that match `GENERIC_TITLE_BANS` in `schemas.py`.
3. Score via `monarch/packaging/titles.py:score_title()`.
4. Top title must pass `gate_title()` before packaging.
5. Every title must have a **click debt** the script pays.

---

## Thumbnail formulas (H1–H8)

| ID | Name | Composition | Postage rule |
|----|------|-------------|--------------|
| H1 | Emotion close | Giant face, one emotion, eyes visible, empty upper third | Face must fill > 40 % of frame |
| H2 | Scale joke | Character tiny, one object impossibly large | Object must be recognisable at 50 px |
| H3 | Before / after | Split left (problem) → right (twist), no text baked | Diagonal or vertical split, clear contrast |
| H4 | Object hero | Single object fills frame, character small and reacting | Object = 60 %+, character = 10 % |
| H5 | Genre range | Wide pose, empty top third for CapCut headline | Headline space = top 30 % minimum |
| H6 | Number dominant | One giant numeral, character dwarfed | Numeral must be > 50 % of frame height |
| H7 | Forbidden peek | Partial reveal — key element cropped or shadowed | Viewer must lean in; nothing given away |
| H8 | Incongruity frame | Two elements that break logic sharing one space | Each element must be identifiable at stamp size |

### Thumbnail generation rules

1. Always produce **5 variants** via `monarch/packaging/thumbs.py:five_variants()`.
2. Test at **postage stamp** size (roughly 120 × 68 px). If the idea is not obvious, kill it.
3. One idea per thumb. Stacking three itches = spam.
4. Accent colour = channel lock.
5. Text is added in CapCut, never baked into the image model.

---

## Script formulas (S1–S6)

| ID | Name | Where | Rule |
|----|------|-------|------|
| S1 | Open-loop hook | First 2–3 seconds | Sentence must be incomplete without watching. Pattern-interrupt picture. |
| S2 | Retention pulse | Every 15–20 seconds | New information, twist, proof, or tension. Never a dead beat. |
| S3 | Silence sting | Before worst/best fact | 0.5–1.0 s of silence, then the hit. Silence IS the effect. |
| S4 | Callback payoff | Final 3–5 seconds | Visual from second 2 returns. Debt is paid. Loop closes. |
| S5 | Escalation ladder | Middle beats | Each beat more intense or surprising than the last. No flat middles. |
| S6 | Viewer POV mirror | Throughout | "You" language. Viewer is the hero, not the narrator. |

### Script generation rules

1. Author as `.fountain` screenplay (see `docs/FOUNTAIN_M3.md`).
2. Gate via `monarch screen-script` — exact word count per scene, no padding.
3. Every beat has a `retention_job` field (why this second exists).
4. Match-cut language is named on every scene (except last).
5. If word count is short → **improve**, never pad with filler.

---

## Contract formulas (K1–K5)

The **click contract** is the promise made by title + thumbnail that the script must honour.

| ID | Name | Promise | Enforcement |
|----|------|---------|-------------|
| K1 | Debt created | Title opens a loop the viewer cannot close alone | Script must close it within first 20 % of runtime |
| K2 | FOMO locked | Thumbnail implies something hidden or rare | Script reveals it; if fake → auto-fail |
| K3 | Truth bond | No fake studies, no "experts say" without source | Disputed = say disputed. No invented data. |
| K4 | Niche voice | Language matches the audience, not a template dump | Channel lock determines vocabulary |
| K5 | Postage promise | Thumbnail is readable at stamp size | If not readable at ~120 px → redo |

### Contract enforcement

1. `gate_title()` checks K1 (banned patterns), K3 (length), K5 (thumb present).
2. Script gate checks K1 (payoff exists) and K3 (factual).
3. Packaging gate checks K4 (niche voice) and K2 (not a lie).
4. Any K-fail = loop. Do not output.
