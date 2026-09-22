# Architecture — Structure Phase

## Loop (not yet implemented)

1. **Hunt** — viral surface of a niche (what is winning, why, who).
2. **Forensic** — microscope on winning videos: hook, retention map, psychology, title DNA, metaphor, payoff.
3. **DNA extract** — reusable patterns, not copy-paste.
4. **Elevate 5x** — same human itch, original angle, higher curiosity density.
5. **Structure** — beat sheet before any prose.
6. **Script** — viewer POV + pro writer POV dual review.
7. **Packaging OS** — competitor CTR forensic → titles → 5 thumbs → listing → draft upload. See `monarch/packaging/`.
8. **Gate** — 10/10 or rewrite. No “good enough.”
9. **Self-improve** — every miss becomes a 3x rule next run.
10. **Visual OS** — board stickman scenes to VO; edit grammar; SFX.
11. **HAAN gate** — ask before any full video / VO / render generation.

See `monarch/visual/`.

## Implemented (structure phase)

- Gates, maths, state machine, HAAN stop: `monarch/core/`, `monarch/schemas.py`.
- Packaging OS: `monarch/packaging/`.
- **M3_script on Fountain**: `.fountain` screenplay → gated numbered scene board.
  Parser: `monarch/core/fountain.py` · integration: `monarch/pipelines/fountain.py` ·
  law + commands: `docs/FOUNTAIN_M3.md`.
- **Playbook** (`monarch/playbook/`): growth formulas (T1–T8, H1–H8, S1–S6, K1–K5) + production laws (L1–L16).
- **QC selftest** (`monarch/core/self_qc.py`): 17-check system (L14), render chain verification (L15), self-improvement loop (L16).

## Non-goals (this phase)

- No live YouTube API calls yet (search is key-gated, cache-ready).
- No LLM orchestration yet.
- No sample scripts yet (test fixtures under `tests/fixtures/` only).
- No fake competitor data.

## Hard rules (constitution)

See `monarch/constitution/`.
