# Monarch WORLDS — channel operating systems

**Created by Adil Chandio** | Boss Contact: `workadilchandio@gmail.com` | Access Key: `DoitMon@rch`

A **world** is one YouTube channel's complete operating system: its identity, its real
analytics, its audience, its creative law, its footage/rights standard, its packaging
system and its per-video assignments.

This is an **additive layer**. It does **not** replace, override or modify:

- `CLAUDE.md` / `BOOT.md` / `AGENT.md` — the normal Monarch wake-up
- `monarch/constitution/` — the ten law files
- `monarch/skills/` — the seven SKILL.md playbooks
- `monarch/agents/` — the five role cards
- `monarch/cli.py` — the 60 registered commands

```
monarch activate            → normal Monarch (4 intake questions, niche hunt)   [UNCHANGED]
monarch cam activate        → MONARCH CAM documented trigger                    [NOT WIRED]
<channel 2> activate        → channel 2 world                                    [PLANNED]
<channel 3> activate        → channel 3 world                                    [PLANNED]
```

When no world is activated, Monarch behaves exactly as before. A world is a mode, not a fork.

## Integration status — important

This turn added **Markdown workflow/reference files only**, as selected. `CLAUDE.md`, `BOOT.md`,
`AGENT.md`, the Python CLI and existing skills are unchanged. Consequently, the phrase
`monarch cam activate` is a **documented intent, not an automatically routed trigger** in the
current agent or CLI. A world folder by itself cannot make the agent read it. Until the
operator explicitly authorizes a small additive router in the agent entrypoint, load
`monarch/worlds/monarch-cam/WORLD.md` explicitly when asking the agent to use this workflow.

There is no CLI command `monarch cam`; do not present this natural-language phrase as a
working shell command.

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
  rules.md         — strict creative law + rights / reused-content law (fail-closed)
  sources.md       — footage sourcing, scene scoring, the footage ledger
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
