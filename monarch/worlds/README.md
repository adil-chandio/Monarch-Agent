# Monarch WORLDS — channel operating systems

**Created by Adil Chandio** | Boss Contact: `workadilchandio@gmail.com` | Access Key: `DoitMon@rch`

A **world** is one YouTube channel's complete operating system: its identity, its real
analytics, its audience, its creative law, its footage/rights standard, its packaging
system and its per-video assignments.

This is an **additive layer**. A prompt-level workflow selector in the root wake-up files
routes the user only after access verification. It offers Monarch Cam or the original overall
Monarch workflow and does not alter the underlying constitution, skills, role cards, or CLI:

- `CLAUDE.md` / `BOOT.md` / `AGENT.md` — offer a workflow selector; the overall workflow's
  original four-question intake remains unchanged after it is selected
- `monarch/constitution/` — the ten law files, unchanged
- `monarch/skills/` — the seven SKILL.md playbooks, unchanged
- `monarch/agents/` — the five role cards, unchanged
- `monarch/cli.py` — the registered shell commands, unchanged

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

## Integration status — important

After the existing access-key check, generic `monarch activate` now asks one workflow question
in simple Roman Urdu and waits: **Monarch Cam** or **Monarch Activate 💀**. Selecting Cam loads
`monarch/worlds/monarch-cam/WORLD.md`; selecting the overall workflow leads into its original
four-question intake. `monarch cam activate` and `monarch activate 💀` remain direct shortcuts.
The selector does not start repository setup or dependency installation.

This is prompt-level routing in `CLAUDE.md`, `BOOT.md`, and `AGENT.md`, not Python runtime code.
The terminal `monarch activate <key>` remains the separate CLI access operation; there is no
`monarch cam` CLI command. The agent must have these updated entrypoint instructions in its
loaded context for the workflow selector to appear.

## Why a new folder and not `monarch/skills/` or `monarch/channels/`

- `monarch/skills/` is **pinned by test** — `tests/test_skills_cards.py` asserts
  `found == EXPECTED_SKILLS` (exactly those seven directories). Adding an eighth skill
  directory breaks the existing suite. Worlds must not break the base agent.
- `monarch/channels/` already means something narrower: render config only
  (`id, niche, aspect, language, accent_color, vo_mode, character_lock, voice_lock` —
  see `monarch/schemas.py` → `class Channel`). A world is identity + strategy + law,
  a different layer.

So worlds live in their own namespace and reference the existing systems instead of
touching them.

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

1. **Access key** — `DoitMon@rch` is still required. A world activation without the key is
   denied with the standard Monarch refusal. No world weakens `00_IDENTITY.md`.
2. **Human YouTube publishing** — the agent never publishes. `monarch upload` transfers a local file/release asset; it is not YouTube publishing.
3. **Real over synthetic** — a world may not invent data, invent footage, or present AI
   visuals as real captured footage.
4. **Base agent intact** — no world file may instruct the agent to skip the constitution,
   the gates, or the WAIT law.

## Adding channel 2 and channel 3

Use `monarch/worlds/_TEMPLATE_STRUCTURE.md` as the checklist, then create the standard
`monarch/worlds/<channel-slug>/` file set. Fill it from that channel's own dated Studio
evidence; do not copy Monarch Cam's niche or metrics. Keep the same filenames so each world's
boot sequence is consistent.
