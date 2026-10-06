# Visual engine (skeleton)

```
voiceover/     VO spec, pacing, breath, punch words
scenes/        scene schema, board language
edit/          cut grammar, 2-3s open, retention pulses
sfx/           premium SFX map
stickman/      our figure system (not PDF clone)
render/        blocked until operator HAAN
```

## Additive rendering style router

- **Style A — image compile** remains the existing, untouched default: generated
  stills → compile → camera movement, transitions, captions → export.
- **Style B — frame renderer** is a separate skill. Use it only when a brief
  explicitly asks for character animation, walk cycles, gestures, a consistent
  character, exact VO sync, frame-perfect timing, no AI drift, or no generative
  drift.
- Photoreal/illustrated scenes, many locations, speed/cost, or an ambiguous
  brief stay on Style A. Style B must not silently rewrite an existing Style-A
  project.

Style-B production contract: [`premium-2d-motion-edit`](../skills/premium-2d-motion-edit/SKILL.md)
with its [technical reference](../skills/premium-2d-motion-edit/ENGINE_REFERENCE.md).
This adds a playbook; it does not claim the full frame-renderer implementation
or a new CLI command is already present.
