# Playbook Laws — L1–L16

Hard rules. Every law is fail-closed: break it → rewrite, never ship.

---

## L1  — VO takes: meaning-first pacing

Voiceover drives the cut, not the other way around.

- Punch words **land first**, then the picture hits.
- Breath = natural cut point. Never cut mid-breath for a scene change.
- First line must be an open loop (see S1).
- Never radio-fast. Conversational urgency beats announcer speed.
- Speaking WPS is measured from the channel voice, not assumed 2.2 forever.

**Gate:** if a scene changes mid-word → fail. Re-sync picture to VO.

---

## L2  — Voice-first mix: VO always leads

The voiceover track is the skeleton. Picture, SFX, and silence wrap around it.

- Picture never lags behind VO (visual must already be on screen when the word lands).
- Picture never spoils the line (do not show the twist before VO says it).
- SFX accent VO hits; they never compete.
- Silence is punctuation. Use it before the worst/best fact (see S3).

**Gate:** if a scene's visual reveals what VO hasn't said yet → fail.

---

## L3  — Picture rhythm: 2–3 second cuts

Scene changes are the heartbeat. Never hold a static frame longer than the rule.

- First render is already at 2–3 s density. No "we'll tighten in the edit."
- Match-cut to a punch word in VO.
- No static stickman talking-head for > 1.2 s without a change (zoom, swap, gesture).
- Open clip may be 2.0–3.0 s (pattern interrupt). Last clip may hold for payoff.
- Middle clips stay even at `clip_s` from the maths line.

**Gate:** count scene durations. Any hold > 3.5 s (body) or > 1.2 s (static head) → fail.

---

## L4  — 3D text: never in clip generation

On-screen text is an **editor** job, not a clip-model job.

- Clip prompts contain **zero** on-screen text, captions, labels, or baked-in words.
- Text overlays are added in CapCut / editor after clip generation.
- Max 6 words per overlay. One overlay per scene.
- The CapCut headline sits in the empty upper third reserved by the thumbnail formula.

**Gate:** if a clip prompt contains "text on screen", "caption", "label", or quote marks around a spoken line in a gen prompt → fail.

---

## L5  — Match-cut language is named

Every scene (except the last) specifies what the match-cut target is.

- Example: "Last half-second matches the first half-second of next clip on pose and facing direction."
- If the match-cut is unnamed, the editor cannot cut cleanly.

**Gate:** `monarch screen-script` enforces match-cut on all non-final scenes.

---

## L6  — Negative prompt is mandatory

Every clip/image generation block carries a negative prompt.

- See `monarch/visual/negatives.md` for the shared list.
- No copyrighted characters, no extra limbs, no text, no BGM, no style drift.

**Gate:** generation request without negative → auto-reject.

---

## L7  — Character lock is verbatim

One `CHARACTER LOCK` sentence, written verbatim into every animation prompt.

- Source: channel config `character_lock`.
- If missing → ask. Do not invent a mascot that fights the niche.
- Style reference = character sheet, never first frame.

**Gate:** prompt missing the lock sentence → fail.

---

## L8  — Prop palette is closed

Each scene declares props. "Nothing else appears."

- Props match the scene's visual anchor.
- No surprise objects. No random background clutter.

**Gate:** if a prompt adds objects not in the palette → fail.

---

## L9  — SFX map: one hit per cut

Premium SFX, not stock cartoon spam.

| Moment | Family | Rule |
|--------|--------|------|
| Open | sub-hit + short whoosh | 1 hit only |
| Title slam | mechanical / glass | 40–80 ms |
| Twist | reverse-whoosh or glitch | never twice in a row |
| Proof / number | tick or bass | sync to numeral |
| Death / fail | muted thud + silence | silence IS the effect |
| Joke | dry pop | no sitcom laugh |

**Gate:** same SFX family used on two consecutive cuts → fail.

---

## L10 — HAAN gate is hard

No bulk clip, VO, or render generation without explicit operator **haan**.

- `require_haan()` in `monarch/core/haan.py` is the single enforcement point.
- "ok", "yes", "han", "lock" are accepted synonyms.
- Anything else = permission denied.

**Gate:** any code path that bypasses `require_haan()` → bug.

---

## L11 — Approval ladder: never skip a stop

See `monarch/constitution/08_APPROVAL_LADDER.md`.

0. Intake → WAIT.
1. Forensic + TOP 1 → WAIT pick.
2. Script → WAIT perfect | improve.
3. Boards → WAIT video haan.
4. Generate + QC → WAIT perfect | reedit.
5. Thumbs → WAIT approve | redo.
6. Metadata → WAIT. Human uploads.

**Gate:** if agent outputs the next stage's deliverable without the previous stage's approval → fail.

---

## L12 — Audio-safe language

VO and clip prompts use audio-safe synonyms. See `monarch/visual/audio_safe.md`.

| Avoid | Use |
|-------|-----|
| hammer | mallet |
| nail | peg |
| explosion | concussive burst of light |
| gunshot | sharp clap of air |
| scream | sudden breath-cut |
| blood | dark splash |

**Gate:** `audio_safe()` function strips banned words before prompt emission.

---

## L13 — Render chain: VO → scenes → edit → SFX

The end-to-end render follows this exact order:

1. **VO generation** — voice identity locked, one take per scene, measured WPS.
2. **Scene clip generation** — one prompt per scene, negative prompt attached, character lock verbatim.
3. **Edit assembly** — 2–3 s cuts synced to VO, match-cuts applied, silence stings placed.
4. **SFX layer** — mapped per scene, no double-hits, silence used as punctuation.
5. **QC pass** — see L14–L16.

**Gate:** if any stage runs out of order → fail. VO must exist before clips are timed.

---

## L14 — QC selftest: 17 checks

Every deliverable passes all 17 checks before presentation to the operator.

| # | Check | Stage | Fail action |
|---|-------|-------|-------------|
| 1 | Research not skipped | All | Re-run forensic |
| 2 | Gates not hidden | All | Re-run gates explicitly |
| 3 | Ijazat asked (HAAN) | Render/VO | Ask before proceeding |
| 4 | No clone or Top-10 DNA | Title/thumb | Rewrite |
| 5 | Duration matches VO length | Script/render | Recompute maths |
| 6 | Word count exact per scene | Script | Rewrite to fit |
| 7 | Open loop in first 8 s | Script | Rewrite hook |
| 8 | Retention job on every beat | Script | Add retention job |
| 9 | Match-cut named (non-final) | Script | Add match-cut |
| 10 | No baked text in gen prompts | Render | Remove text from prompt |
| 11 | Character lock verbatim | Render | Insert lock sentence |
| 12 | Negative prompt attached | Render | Add negative |
| 13 | SFX no double-hit | Edit | Change SFX family |
| 14 | Silence sting before key fact | Edit | Insert silence |
| 15 | Postage-stamp readable thumb | Packaging | Redo thumb |
| 16 | Title + thumb = one sentence | Packaging | Rewrite either |
| 17 | Click debt paid in script | Packaging + Script | Add payoff to script |

**Gate:** any single fail → loop. Do not present to operator.

---

## L15 — QC render: ek command

After the render pipeline finishes, run one command to verify:

```bash
python -m monarch qc-render <video_path> <scene_board.json>
```

This validates:
- Scene count matches maths line.
- Total duration matches `total_s`.
- No scene exceeds max clip hold (L3).
- VO word count matches script word count (±1 tolerance).

If the command does not exist yet, the agent performs the checks manually against the scene board JSON and the rendered file metadata.

---

## L16 — QC self-improvement loop

Every QC fail becomes a lesson. See `monarch/core/lessons.py`.

1. Name the miss precisely.
2. Extract the rule that would have prevented it.
3. Next response applies that rule at 3× intensity.
4. That miss class must not repeat.

Lessons are appended to `monarch/self_improve/lessons.md` with a UTC timestamp.

**Gate:** if a previously logged miss class re-occurs → auto-fail with reference to the lesson.
