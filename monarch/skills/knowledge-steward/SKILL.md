---
name: knowledge-steward
description: >
  Use for Monarch source verification, YouTube/platform guidance updates, evidence labeling,
  channel-learning records, skill/prompt changes, QA regressions, or analytics interpretation.
  The central manager invokes this cross-cutting skill; it maintains cited knowledge and tests,
  not a new creative pipeline or publishing authority.
---

# Knowledge Steward — cited learning and evaluation

This is a **new additive skill**. It does not replace or modify any existing skill, role card, the constitution, a channel world, Style A, or the Style-B contract. Start with [`monarch/knowledge/README.md`](../../knowledge/README.md) and consult only the relevant knowledge references.

## Trigger this skill when

- an agent uses a platform rule, research finding, neuroscience claim, metric interpretation or creator-growth heuristic;
- the team examines a public competitor, trend or third-party GitHub repository;
- channel analytics, retention curves, an A/B result or a production failure may change future advice;
- any skill, prompt, workflow, quality gate or persistent channel memory is proposed for revision.

## Workflow

1. **Name the question and scope.** Identify channel/world, format, audience, decision and required evidence. Keep the existing access, intake, user-choice, `WAIT`, rights, HAAN and human-publishing gates.
2. **Retrieve the source of truth.** Use current official docs for platform policy/features; primary/reviewed research for scientific claims; authorized first-party data for channel outcomes. Public competitor signals stay `OBSERVED_PUBLIC`.
3. **Label each claim.** Use the evidence classes in `monarch/knowledge/AGENT_OPERATING_STANDARD.md`. Record source URL, checked date, scope, limitation and confidence basis. Do not trust an unsupported search snippet or a README marketing promise.
4. **Separate evidence from creative hypotheses.** A hook formula or editing suggestion may be a useful hypothesis, not a ranking law. Never promise views, retention, viewer psychology or causal impact from an untested rule.
5. **Record authentic experience.** Use `monarch/knowledge/templates/experience_record.template.json`: freeze the prediction separately from the later observation, include source/time window/format, and label the result `supported`, `not_supported` or `inconclusive`. Never invent first-hand experience or private analytics.
6. **Evaluate changes.** Add or update cases in `monarch/knowledge/evals/golden_cases.json` and the evaluation catalog. Check positive, edge and regression cases. A model self-score is not proof; check artifact evidence and any deterministic repository tests.
7. **Report to the Manager.** Use the standard handoff: status, artifacts, evidence IDs, decisions, checks (passed/failed/not measured), uncertainty, blockers and next owner. Request an additive revision; do not silently rewrite another skill or alter Style A.

## Analytics handling

- Existing `monarch learn ingest`, `log` and `distill` are for aggregate performance records; describe their output as provisional patterns, not causal discoveries.
- For an authorized time-indexed retention export, the new offline `monarch learn retention ingest` and `monarch learn retention report` commands may be used. They do not fetch data, authenticate, validate permission or identify why a viewer left. If the curve is absent, state `NOT MEASURED`.
- Preserve a native A/B result exactly as Studio reports it. `inconclusive` or `performed same` is not a winner. Keep test result separate from any creative preference. `monarch learn experiment record/log` stores an operator-transcribed result; it does not fetch, execute or verify the test.
- Do not turn one video, a single view spike, CTR alone, or an uncontrolled before/after comparison into a universal channel law.

## Release / hold rules

- Hold unsupported factual claims, unclear rights, missing required artifacts, failed hard constraints and unrun mandatory checks.
- Treat a failed or unavailable tool honestly; plans and previews are not final deliverables.
- Style A stays the untouched default. Style B is Python + PIL and must follow `monarch/skills/premium-2d-motion-edit/SKILL.md` and its `ENGINE_REFERENCE.md`; this skill does not implement that renderer.
- QA may prevent the operator from needing to watch every complete export, but it never replaces the current approval ladder or certifies every subjective property.

## Output format

```text
KNOWLEDGE REVIEW — COMPLETE | BLOCKED | NEEDS REVIEW
Question / scope:
Evidence IDs and classes:
Verified findings:
Hypotheses / unknowns:
Files or metrics checked:
Regression cases updated / run:
Recommended additive change:
Risks / next owner:
```
