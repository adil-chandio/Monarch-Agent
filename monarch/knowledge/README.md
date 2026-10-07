# Monarch shared knowledge, calibration & QA system

**Status:** additive knowledge layer · **Version:** 1 · **Source review date:** 2026-10-06

This folder is the shared, cited knowledge layer for Monarch's manager and specialists. It adds knowledge and evaluation rules; it does not replace the constitution, a selected channel world, an existing skill, a role card, an approval gate, or a renderer. No claim in this folder means a capability exists unless the capability map verifies it.

## When to load it

After workflow choice and intake, the manager loads this index and the applicable references below. Each specialist receives only the relevant playbook plus the job brief and evidence handoff. Do not load every reference into every task by default. The layer applies to both the overall workflow and channel worlds, but never bypasses a world's read order, intake, `WAIT`, rights, HAAN, QA, or human-publishing rules.

The central Manager/Executive Producer owns the run: assigns work, tracks status, returns evidence-based revision requests, and reconciles specialist outputs. Specialists report artifacts and blockers to the manager; they do not silently select the operator's topic, format, voice, title, or other gated choice. On explicit operator correction or a real QC miss, use the additive self-improvement skill to revise the active artifact in the same turn, verify it, and persist only scoped, traceable lessons. This is a prompt-level loop, not autonomous background learning. Independent QA reduces the need for the operator to watch every complete export, but does not waive any existing approval gate.

## Read map

| Need | Reference |
|---|---|
| Central cross-stage run owner and specialist routing | [`executive-producer` skill](../skills/executive-producer/SKILL.md) · [`Executive Producer role card`](../agents/executive_producer.md) |
| Same-turn artifact revision and traceable lessons after operator feedback/QC misses | [`self-improvement` skill](../skills/self-improvement/SKILL.md) · [`L16 lessons`](../self_improve/lessons.md) |
| Shared evidence labels, source hierarchy, handoff contract, freshness and uncertainty | [`AGENT_OPERATING_STANDARD.md`](AGENT_OPERATING_STANDARD.md) |
| Competencies, boundaries, outputs and handoffs for each role | [`ROLE_COMPETENCIES.md`](ROLE_COMPETENCIES.md) |
| YouTube recommendations, Analytics metrics, tests, trend windows and known Monarch gaps | [`YOUTUBE_PERFORMANCE.md`](YOUTUBE_PERFORMANCE.md) |
| Multimedia-learning, curiosity, neuroscience and loudness evidence with limits | [`LEARNING_DESIGN_AND_AUDIO.md`](LEARNING_DESIGN_AND_AUDIO.md) |
| What the current repository can and cannot actually do | [`CAPABILITY_MAP.md`](CAPABILITY_MAP.md) |
| Evaluation cases and fail/hold rules | [`EVALUATION_CATALOG.md`](EVALUATION_CATALOG.md) |
| Source register, dates and how each source is being used | [`SOURCES.md`](SOURCES.md) |
| Empty reusable channel profile | [`templates/channel_bible.template.json`](templates/channel_bible.template.json) |
| Empty claim/evidence record | [`templates/evidence_record.template.json`](templates/evidence_record.template.json) |
| Empty prediction → observation learning record | [`templates/experience_record.template.json`](templates/experience_record.template.json) |
| Run ownership, artifact status, checks, evidence and approval-gate ledger | [`templates/run_manifest.template.json`](templates/run_manifest.template.json) |
| Empty example schema for an operator-supplied retention curve | [`templates/retention_curve_record.template.json`](templates/retention_curve_record.template.json) |
| Empty example schema for an operator-transcribed native experiment result | [`templates/experiment_result.template.json`](templates/experiment_result.template.json) |
| Representative gold/adversarial agent cases | [`evals/golden_cases.json`](evals/golden_cases.json) |

## Precedence and truth rules

1. Security, access, rights, safety, operator constraints and existing approval laws remain binding.
2. The selected channel world governs that channel's audience, identity, sources, workflow and delivery.
3. Use an authoritative current platform source for platform policy/features; primary sources and peer-reviewed work for factual/scientific claims; authorized first-party Studio/Analytics data for that channel's outcomes.
4. Channel measurements are local evidence, not universal laws. Third-party creator advice, competitor observations, hook formulas and model suggestions are hypotheses unless independently supported.
5. If evidence or the actual tool is missing, label it `UNKNOWN`, `NOT VERIFIED`, `NOT MEASURED` or `BLOCKED`; do not fill the gap with a confident-sounding guess.

Older creative/neuro/packaging formulas in the repository remain available as creative heuristics. This overlay does **not** delete or rewrite them; it clarifies that those formulas are not proof of a causal algorithm effect, a brain-control method, or a guaranteed retention result. Never present a metaphor about dopamine, fear, curiosity or the nervous system as a measured biological fact without a suitable source.

## Knowledge vs skill vs experience

- **Knowledge** is sourced, scoped and dated information.
- **Skill** is a repeatable workflow with inputs, outputs, checks and stop conditions.
- **Experience** is a traceable history of real, authorized work: prediction, actual artifact, measured outcome, sample/context, reviewer decision and later correction.
- **Judgment** is the ability to separate those categories, communicate uncertainty and escalate risk.

A model must not claim human credentials, lived experience, private competitor data, or results it did not observe. The channel Bible and experience template hold approved channel context; mock examples must remain clearly labelled as examples.

## Hard style boundary

Style A remains the existing default and is untouched. Do not edit its files, prompts or steps. The new Style-B reference is the existing [`premium-2d-motion-edit` skill](../skills/premium-2d-motion-edit/SKILL.md) and [`ENGINE_REFERENCE.md`](../skills/premium-2d-motion-edit/ENGINE_REFERENCE.md); read those canonical files for its exact laws. Style B is Python + PIL frame drawing, not generated stills. This knowledge layer does not imply that a complete Style-B renderer or audio-mix CLI exists.

## Data and privacy

Authorized channel analytics and experience records stay in the ignored `.monarch/` session area by default. Do not put tokens, access keys, private viewer-level data, unlicensed source media, or private channel exports in tracked knowledge files. The optional retention-curve importer reads an operator-supplied export; it does not authenticate to YouTube or verify the export owner's permission.
