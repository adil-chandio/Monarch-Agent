# Future channel world template

Use this as a **checklist** when channel 2 or 3 is ready. Do not copy channel 1's wildlife
facts, analytics, voice, brand or legal rules into another world.

## Before creating the folder

Collect from the operator:

- exact channel/display name, handle, URL and preferred activation phrase
- current format(s), language(s), audience and channel promise
- dated Studio export/screenshots for channel and video analytics
- at least 3–6 comparable historical winners/losers and their actual metrics
- real brand assets/colours/fonts and existing brand conflicts
- channel-specific content pillars, exclusions, safety and rights requirements
- first specific assignment (kept separate from permanent channel law)

Mark every number and claim as one of: **operator-reported**, **Studio-exported**,
**independently checked**, or **unknown**. Put the source and date next to it. Never
fabricate a "verified" metric from a prompt.

## Folder shape

```
monarch/worlds/<channel-slug>/
  README.md
  WORLD.md
  identity.md
  analytics.md
  audience.md
  rules.md
  sources.md
  packaging.md
  delivery.md
  assignments/
    README.md
    <one-file-per-current-task>.md
```

Use lowercase ASCII hyphenated slugs. Keep permanent channel strategy out of assignments;
keep temporary video instructions out of the permanent identity/rules files.

## World files to create

- `README.md` — display name, documented trigger, status (wired vs docs-only), file reading
  order, one-paragraph brief.
- `WORLD.md` — activation contract, boot sequence, actual workflow stages, truthful
  tools/limitations, and approval gates. Do not claim a natural-language trigger is wired unless
  the root agent entrypoint has an approved router.
- `identity.md` — brand promise, pillars, anti-identity, brand system.
- `analytics.md` — dated evidence, diagnoses, benchmarks and **the lesson each proves**.
- `audience.md` — segments linked to evidence and actionable creative implications.
- `rules.md` — language, creative, safety, factuality, rights, synthetic-content law.
- `sources.md` — research protocol, source-tracing standard, scorecard and ledger template.
- `packaging.md` — title/thumbnail/description/metadata and conversion paths.
- `delivery.md` — exact deliverables, review checklist, upload/feedback loop.
- `assignments/` — the current per-video brief, candidate leads and exact intended outcome.

## Activation routing is an explicit integration decision

A folder of Markdown files does not make an activation phrase executable. Until the operator
approves an additive router in the relevant entrypoint (for example `CLAUDE.md`), the world
is documentation only and must be loaded explicitly. If the operator requires the base
agent's files to remain byte-for-byte unchanged, keep the world docs-only and state this
limitation plainly — do not sneak a router into a different folder and claim it is active.

## The global Monarch laws still apply

Every world inherits the constitution, HAAN/approval gates, human-only YouTube publishing, and
fail-closed behaviour. No activation-key gate applies. A niche-specific world may add restrictions,
never weaken the base laws.
