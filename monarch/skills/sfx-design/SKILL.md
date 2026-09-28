---
name: sfx-design
description: >
  Design and render the psychoacoustic SFX bed for a scene board: role-based
  cue mapping (hit/sonar_ping/bass_drop/heartbeat/riser/glitch), the N5
  riser→0.3s-silence→drop chain, SoLoud-style DSP filters and the limiter.
  Use when building M5_boards, or the operator asks for sound design/SFX.
---

# Skill: sfx-design — scene roles → psychoacoustic cue sheet

## When to use

- After the storyboard exists (roles are assigned by the director).
- Operator wants standalone SFX assets for the editor.

## Inputs

- A scene board (from `make-video` / `video-storyboard`) or a list of roles.

## Role → cue map (the law)

| Role | Kind | Filter | Note |
| --- | --- | --- | --- |
| hook | `hit` | none | frame-one snap (N1), 1 hit only |
| tease | `sonar_ping` | `tension_echo` | searching cue (N3) |
| payoff | `bass_drop` | `bass_boost` | 40Hz pressure (N5) |
| value-debt | `heartbeat` | none | dread under the takeaway (N4) |
| silence-sting | `riser` | none | cuts to 0.3s dead air after |
| payoff+cua | `hit` | none | closing snap |
| twist (special) | `glitch` | `cyber_glitch` | never twice in a row |

## Steps

1. Read the roles from the board:
   ```
   monarch video-storyboard --topic "$TOPIC" --json
   ```
2. Render one wav per scene at the board's duration (clamped by `--seconds`):
   ```
   monarch sfx --kind $KIND --filter $FILTER --seconds $DUR --out output/$SLUG/sfx/scene_$N.wav
   ```
   (`limiter` always runs last; add `--filter bass_boost` for phone speakers.)
3. Verify the N5 chain: exactly one sting scene, riser ends, 0.3s silence,
   then the payoff drop lands on the next scene's `t_start`.
4. Write the cue sheet (`scene | role | kind | filter | duration`) into the
   output dir next to `timeline.json`.

## Guardrails

- VO always wins (L2): beds duck under speech; sub-bass felt, not heard.
- No BGM, no cartoon packs, no sitcom laughter (`monarch/visual/sfx/map.md`).
- Unknown kind/filter = CLI FAIL — do not invent kinds.

## Handoff

Cue sheet + wavs → HAAN gate (`M5b_haan_video`) for any final render.
