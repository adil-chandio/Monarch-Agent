# Neuro-Psychology Playbook — N1–N5

The brain laws under every Monarch law. `laws.md` says **what** never ships;
this playbook says **why the brain lets it ship**. Every law is fail-closed:
break it → rewrite, never ship.

Pipeline mapping lives at the bottom — every N-law is wired into
`monarch/video/` (director → engine → audio → compositor), not left as theory.

---

## N1 — 0.1s thumb-stop: the Superior Colliculus reflex

Before "watching" exists, the midbrain triages. The **superior colliculus**
fires on sudden motion, high contrast and eye-like shapes in roughly a tenth
of a second; the **amygdala** tags it threat / food / mate before the viewer
has a single conscious thought. If frame one does not trip that reflex, the
swipe already happened.

- Frame one is judged in **0.1s** — contrast and silhouette, never detail.
- One focal shape against a cleaned background. Two focal points = zero.
- Motion on frame one beats beauty: a snap-zoom, a falling object, a face
  entering frame. Static beauty is scroll-invisible.
- Eye-like contrast (two bright dots in a dark mass) is the strongest
  primitive we own. Use it honestly — real curiosity, not clickbait.
- The thumbnail and clip one are the **same shot family**: the promise the
  thumb makes, frame one must keep or the amygdala flags a bait-and-switch
  and trust (and retention) dies.

**Gate:** if scene 1's visual has low contrast, two focal points, or no
motion in the first 0.1s → fail. `NEURO_DRIVER: N1 THUMB-STOP`.

---

## N2 — Demographic dopamine modulation

Dopamine is not one dial. The same reward fires differently across age
cohorts, so pace, color and payoff density are tuned per demographic:

| Cohort | Cut rate | Palette | Reward shape | Forbidden |
| --- | --- | --- | --- | --- |
| **Kids (<13)** | 1.5–2.0s | max-saturation primaries | instant, per-scene cause→effect, confetti-level wins | dread, irony, open dread-loops |
| **Gen Z (13–24)** | 2–3s | neon on dark, one accent | novelty + identity signals, micro-twists every 2 scenes, irony allowed | slow fades, lecture tone, "stock footage" genericity |
| **Adults (25+)** | 3–4s | restrained, cinematic | proof, status, closure — payoff must *mean* something | jump-cut chaos, confetti, hype-announcer VO |

- The maths line fixes clip length; the cohort fixes **how it feels** inside
  that length (engine palette, audio pressure, payoff density).
- Kids' wins must be *earned on screen* (the character visibly gets the
  thing) — unearned confetti trains abandonment.
- Adults' curiosity is status-driven: "insiders know" beats "you won't
  believe" (see `growth_formulas.md` T6 vs T1).

**Gate:** channel demographic unset or palette/pace contradicts the cohort
row above → fail. `NEURO_DRIVER: N2 DOPAMINE-{COHORT}`.

---

## N3 — Skinner variable-ratio: the unpredictable reward loop

B.F. Skinner's pigeons pecked hardest when reward was **random** — variable-
ratio reinforcement beats fixed schedules on every measures that matters
(rate, persistence, extinction-resistance). The feed is a Skinner box and
the scroll is the lever; our job is to make *staying* the pecking behavior.

- Open the loop in scene 1 and **never close it where you opened it** (L1/S1).
- Reward on a variable ratio: a real payoff every **2–4 scenes**, never on a
  fixed beat the viewer can predict — predictable = extinction.
- Each payoff must *promise a larger one* before it lands (the machine
  reloads itself). A payoff that closes everything is a logout button.
- Micro-teases: 1 spoken word of a future payoff ("…almost") is enough to
  reset the loop clock. Cheap, honest, effective.
- Never tease what the script cannot pay. One unpaid tease burns more trust
  than ten paid ones build (the click-debt law from T1).

**Gate:** two consecutive scenes with zero new loop tension, or a payoff
that opens nothing after it → fail. `NEURO_DRIVER: N3 VARIABLE-RATIO`.

---

## N4 — Cialdini reciprocity: the value-debt subscription mechanic

People repay what they receive. Give real value **first**, unprompted, and a
subscription stops being an ask and becomes **repayment of a felt debt**.

- Deliver a usable takeaway (the mechanism, the number, the method) *before*
  any subscribe language exists. No value → no debt → no sub.
- The subscribe moment is placed **immediately after a payoff lands**, when
  the debt feeling peaks — never in scene 1, never cold.
- Re-trigger mid-video: a second, smaller free takeaway around the 60–70%
  mark refreshes the debt for the back half.
- Frame the ask as the loop continuing, not as charity: "tomorrow's one is
  bigger — subs see it first" beats "please subscribe".
- Value must be *legible* — the viewer has to *feel* they received
  something. Buried value creates no debt.

**Gate:** subscribe CUA without a delivered payoff before it, or any CUA
before the first takeaway → fail. `NEURO_DRIVER: N4 VALUE-DEBT`.

---

## N5 — Psychoacoustics: 40Hz pressure + the 0.3s silence drop

The ear is a threat-detection organ. Low-frequency energy is *felt* (chest,
jaw) before it is heard; silence reads as danger and snaps attention harder
than any sound can.

- **40Hz sub-bass** sits under every hit and reveal — at 40Hz the listener
  *feels* pressure without noticing a sound. It must be felt, never heard as
  a tone; if it hums, it is too loud or too high.
- **0.3s total silence** immediately before the single most important fact
  of the video (L2: silence is punctuation). Everything stops — bed, SFX,
  VO breath — then the fact lands. Only once per video; twice is a trick.
- Risers into reveals, sub-drop out of them: the rise builds prediction,
  the drop pays it (N3's loop, in the audio domain).
- Heartbeat under dread, sonar under "searching" sequences, glitch on the
  twist, tape hiss on "evidence" — one SFX family per emotional beat, never
  two competing (L2).
- Mix law: VO always wins (L2). SFX duck to VO; the 40Hz bed rides under
  speech, never over it.

**Gate:** key fact lands without a preceding silence drop, or a 40Hz bed
audible as a tone over VO → fail. `NEURO_DRIVER: N5 SILENCE-STING`.

---

## Pipeline mapping — where each law is enforced

| Law | Director (`director.py`) | Engine (`engine.py`) | Audio (`audio.py`) | Compositor (`compositor.py`) |
| --- | --- | --- | --- | --- |
| N1 | scene 1 role = `thumb-stop`, single focal visual | one focal block + high-contrast palette | `hit` on frame one | open clip = snap zoom-in |
| N2 | cohort pace + payoff density plan | cohort palette + cut density badges | cohort SFX pressure | cut rate per cohort row |
| N3 | roles alternate tease/payoff on a seeded 2–4 ratio | `LOOP` badges on tease scenes | `sonar_ping` tease, `riser` into payoff | motion variety resets visual habituation |
| N4 | `value-debt` scene before payoff, CUA after it | `TAKEAWAY` pill render | `heartbeat` under the debt beat | hold on the takeaway pill |
| N5 | `silence-sting` on the key-fact scene | — | `bass_drop` 40Hz, 0.3s silence gap, `riser`, `glitch`, `forensic_tape` | drops land exactly on scene t_start |

Fail-closed: the director refuses to emit a storyboard that breaks a row
above. Same rule as every Monarch gate — break it → rewrite, never ship.
