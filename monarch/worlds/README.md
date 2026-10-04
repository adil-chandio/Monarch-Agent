# Monarch WORLDS — channel operating systems

**Created by Adil Chandio** | Boss Contact: `workadilchandio@gmail.com` | Access Key: `DoitMon@rch`

A **world** is one YouTube channel's complete operating system: its identity, its real
analytics, its audience, its creative law, its footage/rights standard, its packaging
system and its per-video assignments.

This is an **additive layer**. A narrow prompt-level router in the root wake-up files selects
a world only when its explicit activation phrase is used. It does not replace the normal
Monarch flow or alter the underlying constitution, skills, role cards, or CLI:

- `CLAUDE.md` / `BOOT.md` / `AGENT.md` — include an additive explicit-world route; the regular
  `monarch activate` path remains unchanged
- `monarch/constitution/` — the ten law files, unchanged
- `monarch/skills/` — the seven SKILL.md playbooks, unchanged
- `monarch/agents/` — the five role cards, unchanged
- `monarch/cli.py` — the registered shell commands, unchanged

```
monarch activate            → normal Monarch (4 intake questions, niche hunt)   [UNCHANGED]
monarch cam activate        → MONARCH CAM world via additive prompt router        [WIRED]
<channel 2> activate        → channel 2 world                                    [PLANNED]
<channel 3> activate        → channel 3 world                                    [PLANNED]
```

When no world is activated, Monarch behaves exactly as before. A world is a mode, not a fork.

## Integration status — important

`monarch cam activate` is now an **explicit natural-language route** in `CLAUDE.md`, `BOOT.md`,
and `AGENT.md`. After the existing access-key check, that phrase loads
`monarch/worlds/monarch-cam/WORLD.md` and follows its pipeline. It skips only intake details fixed
by the world and active assignment; if no assignment exists, the agent asks for a brief.

The normal `monarch activate` flow still asks its original four questions and is unchanged.
The route does not bypass the constitution, human approval/WAIT gates, QC, or human YouTube
publishing. This is prompt-level routing, not Python runtime code, and there is no shell/CLI
command `monarch cam`. The entrypoint instructions must be present in the agent's loaded context
for the natural-language trigger to work.

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
