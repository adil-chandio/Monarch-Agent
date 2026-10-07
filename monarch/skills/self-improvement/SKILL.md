---
name: self-improvement
description: >
  Use when a Monarch operator corrects an answer or artifact, asks for an improve
  pass, flags robotic or AI-sounding writing, points out continuity or logic errors,
  or asks Monarch to persist a lesson from feedback or QA.
---

# Self-improvement — feedback to verified repair

This additive skill turns explicit operator feedback and real QA misses into an immediate, checked revision and—only when requested or warranted—a traceable reusable lesson. It is a repeatable agent workflow, not model-weight training, a background process, or a promise of zero defects.

## Authority and scope

- The operator's correction governs the current artifact. Re-read the exact words and the active brief; do not defend the miss, minimize it, or make the operator repeat information already given.
- Keep access, evidence, privacy, rights, current workflow state, `WAIT`, HAAN, M3, creative-review and human-publishing gates unchanged. Feedback is not permission to bypass a gate or invent an unsupported capability.
- Fix the work in the same authorized stage and same turn. If the correction exposes a real blocker, repair what is possible and state the precise remaining blocker; do not pretend it is solved.
- Scope a taste preference to the current operator, channel, deliverable and language unless it is explicitly approved as a wider rule. One subjective correction is not proof that every audience prefers the same style.
- Do not claim the model autonomously learned, changed its weights, or will be flawless. Claim persistence only after the relevant lesson/skill/test is actually saved and verified.

## Same-turn repair loop

1. **Capture the correction.** Identify the exact phrase, action, claim, timing, format or gate the operator rejected. Preserve the accepted parts of the brief and the user's intended replacement, when supplied.
2. **Name the root miss.** Classify it as voice/style, story/continuity, fact/rights, timing/math, format/tool, QA, or gate handling. Distinguish the visible symptom from the cause. Example: a timer ringing before setup is a cause-and-effect miss, not just a wording problem.
3. **Revise the actual artifact now.** Replace the affected text/scene/file; do not only promise to improve it next time. Do not create duplicate “v2/final-final” artifacts unless the workflow explicitly requires version history.
4. **Verify before reporting.** Run the exact deterministic checks the artifact requires, read the revised sequence end-to-end, confirm the file exists, and report failed, unrun and `NOT MEASURED` checks honestly. Subjective quality still returns to the operator's gate.
5. **Persist only the right lesson.** If the operator explicitly asks to make the correction durable, or a real QC failure meets L16, append a scoped rule through `monarch.core.lessons.record` to `monarch/self_improve/lessons.md`. For a reusable behavior, add/update a regression case and the relevant skill/bootstrap reference. Do this in the same task, then run the affected tests. Do not turn one user's taste into a universal rule.
6. **Close the loop visibly.** State what changed, which check passed, what remains blocked, where the durable rule lives, and the current approval gate. Stop there.

## Spoken script and narration preflight

Before showing a revised spoken script, read it as speech—not as a list of written slogans:

- Match the operator's requested language and register. Prefer idiomatic, easy-to-say phrasing, contractions and natural connective words; use the operator's own sample as a style anchor when they provide one.
- Read the full narration continuously across scene/beat boundaries. Production cuts are not automatic spoken pauses. If fixed word math makes the dialogue sound clipped, carry a sentence across adjacent beats while preserving the exact count; never pad or silently break M3 math.
- Build a recognizable mini-story: a concrete moment, the person's thought/feeling, a natural turn, an action, and a specific payoff. Avoid generic motivational filler, stacked commands, interchangeable slogans, repeated reassurance, and “AI-sounding” stock phrases when they do not arise from the scene.
- Keep the voice human without inventing lived experience. A fictional character or direct-to-viewer framing is fine; do not imply the model personally experienced the story.
- Do not present a practical suggestion as a scientifically proven method, guaranteed result, or measured audience preference without suitable evidence.
- When the operator gives a preferred phrase, preserve its meaning and conversational intent; do not mechanically copy it if grammar, safety or the beat math needs a small adaptation. Explain only a real constraint.

### Continuity and timing check

Make a simple action ledger for the scene sequence: **setup → action → consequence → payoff**. Check every named prop and event (timer, phone, notebook, door, sound, location, character) against the scene order and timeline.

- Introduce/set an object before referring to its running, ringing, opening, closing or result.
- A two-minute timer cannot ring inside a 42-second story unless an explicit time jump/compression is shown. If time has not elapsed, leave it visibly running or remove the ring; do not imply two minutes passed.
- Reconcile spoken-word cadence, scene durations, pauses and on-screen action with the requested runtime. Do not imply a real-time task finished or time elapsed when the edit cannot plausibly show it; use an explicit time jump/compression or show only plausible early progress.
- Make dialogue, visual direction, elapsed time and scene math agree. If a ratio, renderer or asset path is unsupported, keep that stage blocked instead of claiming a successful render.

## M3 / technical verification

For Fountain shorts, preserve the approved duration, `compute_math` scene count and exact words per clip. Do not expose the word-count constraint as awkward spoken phrasing. Run the actual M3 gate, for example:

```text
monarch screen-script <script.fountain> --length <seconds> --board-out <board.json>
```

The command must actually exist and be run in an authorized environment. If it cannot be run, use the existing `monarch.pipelines.fountain.build_script` API only if available, and report which path was used. A passing word-count gate does not prove natural delivery, factual accuracy, rights clearance, emotional impact or approval. If the revision changes the gated script, stop at the existing `perfect | improve` gate. If the already-approved artifact is unchanged, do not reopen its approval gate.

## Durable learning and regression

- Use the existing L16 recorder and timestamp/`3x rule` format in `monarch/core/lessons.py`; do not invent a CLI subcommand for this workflow.
- Record the specific miss and prevention rule, not private data, credentials, a full chat transcript, or unsupported theory. Keep operator-specific style preferences scoped and labelled.
- Add a golden/adversarial case when the failure is repeatable and testable (for example, “timer setup precedes timer effect” or “same-turn rewrite incorporates the operator's language feedback”). Do not claim a model evaluation ran unless it actually did.
- Apply an existing lesson as a preflight check on the next relevant task. Use L16's hygiene/3× policy before promoting a repeated signal into a general channel rule.
- A future session only benefits if it loads the changed skill/lesson. This skill does not schedule work, rewrite itself in the background, or automatically update model weights.

## Response after a correction

Keep the update concise and in the user's language. Acknowledge the concrete miss once, show the corrected deliverable in chat when requested, and state only the checks that actually passed. Ask for the next valid gate (`perfect | improve`, `Aage barhoon?`, or the channel's existing token) only when the active artifact/workflow still requires it; never reopen approval for an unchanged artifact already approved. Do not claim “flawless,” “zero defects,” or guaranteed virality.
