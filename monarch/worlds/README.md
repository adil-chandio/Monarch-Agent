# Monarch WORLDS — channel operating systems

A **world** is one YouTube channel's complete operating system: identity, analytics, audience,
creative law, footage/rights standard, packaging, and per-video assignments.

This is an **additive layer**. A prompt-level workflow selector in the root wake-up files
routes the user directly; there is no activation-key gate. It offers Monarch Cam or the original overall
Monarch workflow without rewriting the constitution, the seven original skills, or the five
state-bound specialist role cards. Separate additive layers now provide Style B, a cross-stage
Manager, cited knowledge/evaluation, same-turn feedback correction, and offline retention-curve import:

- `CLAUDE.md` / `BOOT.md` / `AGENT.md` — offer a workflow selector; the overall workflow's
  original four-question intake remains unchanged after it is selected
- `monarch/constitution/` — the ten law files, unchanged
- `monarch/skills/` — seven original cards remain unchanged; `premium-2d-motion-edit`,
  `executive-producer`, `knowledge-steward`, and `self-improvement` are additive
- `monarch/agents/` — five state-bound specialist cards remain unchanged; the new
  Executive Producer card coordinates across states without replacing them
- `monarch/knowledge/` — cited evidence rules, capability limits, templates and evaluation cases
- `monarch/cli.py` — the workflow selector itself adds no command; retention import and
  operator-transcribed experiment logging are separate, additive learning commands

```
monarch activate            → ask workflow selector; wait for choice                [WIRED]
Monarch Cam                → load Cam world and active assignment                   [WIRED]
Monarch Activate 💀        → original overall workflow (four questions)             [WIRED]
monarch cam activate       → direct shortcut to Monarch Cam                         [WIRED]
monarch activate 💀       → direct shortcut to overall workflow                     [WIRED]
<channel 2> activate       → channel 2 world                                        [PLANNED]
<channel 3> activate       → channel 3 world                                        [PLANNED]
```

On generic `monarch activate`, the agent waits for the workflow choice before starting work. The overall workflow itself is unchanged after selection. A world is a mode, not a fork.

For a channel world, the entry intake comes before Stage 1: the agent asks **topic · ratio ·
length** in simple Roman Urdu and waits for the answers. A provisional brief in `assignments/`
is not a chosen topic, and the agent never picks topic/ratio/length for the operator. Stages 1–6
research for a video lands in **one** `output/<slug>/project_notes.md` with per-stage sections,
not six separate reports.

## Integration status — important

The generic `monarch activate` workflow selector runs directly; no activation-key check applies.
It asks one workflow question in simple Roman Urdu and waits: **Monarch Cam** or **Monarch Activate 💀**.
The terminal activation-key command has been removed; these are prompt-level routes only.
The selector does not start repository setup or dependency installation.

## Why a world is separate from skills and channels

- `monarch/skills/` contains reusable workflow cards. The seven original cards stay
  unchanged; `premium-2d-motion-edit`, `executive-producer`, `knowledge-steward`, and
  `self-improvement` are additive cards. Registry tests pin the intentional set so
  accidental additions or removals are caught.
- `monarch/channels/` already means something narrower: render config only
  (`id, niche, aspect, language, accent_color, vo_mode, character_lock, voice_lock` —
  see `monarch/schemas.py` → `class Channel`). A world is identity + strategy + law,
  a different layer.

Worlds live in their own namespace; reusable skills and channel worlds remain separate
layers.

## World layout (standard for all 3 channels)

```
monarch/worlds/<channel-slug>/
  README.md        — what this channel is, one screen
  WORLD.md         — ACTIVATION CONTRACT: trigger, boot sequence, 13-stage pipeline, gates
  identity.md      — brand promise, pillars, anti-identity
  analytics.md     — dated, source-labelled channel snapshot + historical winners + lessons
  audience.md      — who actually watches, and what that changes creatively
  rules.md         — creative, factuality, safety, source, rights, and reused-content rules
  sources.md       — footage discovery, source tracing, scene scoring, and the asset ledger
  claim-risk.md    — optional specialist screen for platform claims and external-media risks
  packaging.md     — titles, cover text, description, tags, pinned comment, conversion paths
  delivery.md      — the exact 17-item deliverable list + the no-stop-at chain
  assignments/     — per-video task briefs (one file per video; channel files stay stable)
```

Only `WORLD.md` is the contract. Everything else is a reference the contract points at.
Per-video work goes in `assignments/` so the channel files never churn.

## The unbreakable laws that apply to every world

1. **No activation lock** — workflow routes are available directly. Every world still obeys the
   shared constitution, rights rules, approval gates, and human-only publishing law.
2. **Human YouTube publishing** — the agent never publishes. `monarch upload` transfers a local file/release asset; it is not YouTube publishing.
3. **Real over synthetic** — a world may not invent data, invent footage, or present AI
   visuals as real captured footage.
4. **Base agent intact** — no world file may instruct the agent to skip the constitution,
   the gates, or the WAIT law.
5. **Approval phrase scope** — “aage barho/continue” approves only the current creative gate,
   never missing intake, unchosen options, rights approval, vendor contact, or publication
   permission, and never a risk-approved status. `OPERATOR APPROVED WITH RISK NOTED` requires the
   operator's explicit acknowledgement of a **named** risk.
6. **Inspection before claims** — no clip score, shortlist, or review claim without visual
   inspection (`NOT SCORED` when not viewable); no scene-specific script/VO/EDL for unseen
   footage; EDL source times must be verified and `TBD` is not a complete edit.
7. **Renderer truth** — `monarch render` makes a previz, not a final edit of imported footage.
   State this in one short line before any final-video promise, and never present previz or AI
   visuals as the finished video.
8. **Rights honesty** — analysis/planning may continue while rights are unknown, but the status
   is written as `RIGHTS UNKNOWN`; no clearance claim and no vendor contact, licence request, or
   payment without explicit authorization.
9. **Per-stage permission** — every stage ke baad short Roman Urdu update + `Aage barhoon?` +
   WAIT. Bina ijaazat agla stage/file/tool nahi, aur agent khud se koi choice (topic, ratio,
   length, idea, scene, script, voice, title) nahi karta. Stopping to ask is not abandoning the
   workflow.
10. **Discussion language** — easy Roman Urdu (Urdu–English mix), short; max 5 bullets per
   update. Sirf final deliverables (script, captions, titles) English mein.

## Adding channel 2 and channel 3

Use `monarch/worlds/_TEMPLATE_STRUCTURE.md` as the checklist, then create the standard
`monarch/worlds/<channel-slug>/` file set. Fill it from that channel's own dated Studio
evidence; do not copy Monarch Cam's niche or metrics. Keep the same filenames so each world's
boot sequence is consistent.
