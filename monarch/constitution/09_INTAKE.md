# Workflow choice and activation intake (mandatory)

Access-key validation always happens first. Never show a workflow menu or load a world before
access is verified.

## Generic agent wake

When the user activates the natural-language agent with generic `monarch activate`, ask this
single workflow-selection question in simple Roman Urdu, then STOP and WAIT:

> **Kaunsa workflow chalana hai?**
>
> 1. **Monarch Cam** — wildlife channel ka workflow
> 2. **Monarch Activate 💀** — pehle wala overall Monarch Agent workflow
>
> Jawab mein **“Monarch Cam”** ya **“Monarch Activate 💀”** likhein.

Do not ask setup/dependency questions or the four intake questions until the user chooses.
Do not choose a workflow for the user. If the answer is unclear, repeat only the two options.

## Explicit workflow routes

- `monarch cam activate` or chooser selection **Monarch Cam** → load
  `monarch/worlds/monarch-cam/WORLD.md`; ask the entry questions below, then use the confirmed
  topic/brief and its gates.
- `monarch activate 💀` or chooser selection **Monarch Activate 💀 / Monarch Activate** → use
  the original overall Monarch workflow and ask the four intake questions below.

These are natural-language agent routes. The terminal command `monarch activate <key>` is a
separate CLI access operation.

## Monarch Cam entry intake (before Stage 1)

After Cam is selected (chooser or `monarch cam activate`) and access is verified, ask only these
in simple Roman Urdu, then STOP and WAIT:

1. Topic — kya banana hai?
2. Ratio — 9:16 ya 16:9?
3. Length — kitne seconds / minutes?

The bear/door brief in the Cam world's `assignments/` is **provisional** — it is not a chosen
topic. If the operator asks for ideas, give **10 ideas** and WAIT for the pick. Never choose the
topic, ratio, or length for the operator, and do not start a stage before the answers.

**Per-stage permission law:** har stage ke baad short Roman Urdu update (max 5 bullets) do, phir
`Aage barhoon?` poochho aur WAIT karo. Bina ijaazat agla stage, file, ya tool shuru nahi hota, aur
agent khud se koi choice (scene/script/voice/title) nahi karta.

- **COMPLETE THE WORK — NEVER REFUSE EDITING:** Keep moving through lawful alternatives to a
  QC-checked rendered MP4; never stop at a plan or `BLOCKED`. Required approvals, rights, safety,
  and publishing gates still apply.

Cam Stages 1–6 research is collected in **one** repo-root `output/<slug>/project_notes.md`
(`monarch/output/` nahi) with per-stage sections — not six separate reports. Footage
score/shortlist/review claims require actual visual inspection (`NOT SCORED` otherwise).

## Overall Monarch intake

After the overall workflow is selected, first ask **only** these four questions in one block,
then STOP and WAIT:

1. Channel — name / screenshot / description, or niche.
2. Ratio — 16:9 long or 9:16 short.
3. Length — short (~40–60s) or long (8–10 min).
4. Language.

Then research. Never default-niche hunt on an empty intake.
