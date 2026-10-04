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
  `monarch/worlds/monarch-cam/WORLD.md`; use its active assignment and gates.
- `monarch activate 💀` or chooser selection **Monarch Activate 💀 / Monarch Activate** → use
  the original overall Monarch workflow and ask the four intake questions below.

These are natural-language agent routes. The terminal command `monarch activate <key>` is a
separate CLI access operation.

## Overall Monarch intake

After the overall workflow is selected, first ask **only** these four questions in one block,
then STOP and WAIT:

1. Channel — name / screenshot / description, or niche.
2. Ratio — 16:9 long or 9:16 short.
3. Length — short (~40–60s) or long (8–10 min).
4. Language.

Then research. Never default-niche hunt on an empty intake.
