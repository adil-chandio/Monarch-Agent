# Agent operating standard — evidence, handoffs and calibration

**Applies to:** Manager and every specialist · **Version:** 1 · **Reviewed:** 2026-10-06

## Evidence classes

Every material statement that may affect topic selection, a factual script, a legal/rightsholder decision, packaging or a learning update must be identified as one of these:

| Label | Meaning | Minimum record |
|---|---|---|
| `OFFICIAL_PLATFORM` | Current first-party platform documentation, policy, feature or API contract | Official URL, checked date, exact scope and relevant passage |
| `PEER_REVIEWED` | Peer-reviewed research or a recognized technical standard | Citation, date, task/population/context, relevant result and limitation |
| `CHANNEL_MEASURED` | First-party data from the channel, supplied or accessed with authorization | Channel/video, metric definition, time window, format/traffic scope, data source and sample size if available |
| `OBSERVED_PUBLIC` | Publicly visible competitor/source evidence | URL, observed date, what was visible and what remains private/unknown |
| `HYPOTHESIS` | Proposed creative or performance mechanism not proven for this channel | What to test, why, metric, audience/format and falsifying result |
| `UNKNOWN` | Not established, inaccessible or not measured | What is missing and the next safe verification step |

Do not convert `HYPOTHESIS` or `OBSERVED_PUBLIC` into `CHANNEL_MEASURED`. A search snippet, model-generated citation, file name, planned output, or self-reported score is not proof that a source was read or a test passed.

## Source hierarchy is domain-specific

- **Platform rules and feature behavior:** current official documentation wins over creator folklore or an old cached guide.
- **Scientific or medical claims:** primary peer-reviewed evidence or a recognized review/standard; record study limitations. Do not turn a finding from one task into a universal viewer-control technique.
- **Channel performance:** authorized channel analytics and native experiment outcomes; compare like format, objective, time window and traffic context where possible.
- **Public competitors:** use only visible evidence. Public views, titles and thumbnails do not reveal their private CTR, retention curve, audience satisfaction or causal strategy.
- **GitHub:** README and marketing claims describe a project; they do not prove quality or suitability. Before copying code, check source, tests, current maintenance, dependencies and license. This pass does not add third-party code.

## Freshness protocol

- Re-open official YouTube policy, API, eligibility or feature documentation when it materially affects a current task. Record the check date; do not rely on memory for volatile rules.
- Trend observations must include the platform, audience/geography/language when known, and the measurement window. A recent trend card is not durable market demand.
- Re-check the rights and license scope of each external asset for the intended use. A match/no-match tool result is not permission.
- Preserve publication date and scope for scientific work; stable theory does not justify stale policy claims.
- For channel learnings, store the observation window and format. Promote a repeated, well-supported pattern cautiously; retain contradictory and inconclusive cases.

## Standard specialist handoff

Every handoff to the Manager uses this shape (in prose or structured output):

```text
STATUS: COMPLETE | BLOCKED | NEEDS REVIEW
ROLE / STAGE:
ARTIFACTS: exact paths or URLs, and which are final vs draft
EVIDENCE: source IDs/URLs and evidence class for material claims
DECISIONS: what was decided and why
CHECKS: passed / failed / not measured, with evidence
ASSUMPTIONS & UNCERTAINTY:
RISKS / BLOCKERS:
NEXT OWNER / REQUEST:
```

A claim of completion requires the artifact to exist and the required checks to have run on that artifact. `NOT MEASURED` is never a pass. Never report a render, visual inspection, test, license clearance, API query or experiment that did not actually happen.

## Confidence and escalation

Use `high / medium / low` only to summarize evidence coverage, and give the reason; this is not a calibrated probability. Escalate or hold when a high-impact factual claim is unresolved, rights are unknown, a platform feature's eligibility is unclear, sources conflict, a required tool is unavailable, or a mandatory QA item fails. Do not ask the operator to watch every full export: independent technical checks and frame/contact-sheet review should provide the evidence, with only genuine judgment calls or failures escalated under the existing approval rules.

## Experience record contract

For learning, keep the **prediction** separate from the **observation**. Record the planned change, expected direction/metric and basis before release; later record the actual source, measurement window, observed metrics, experiment status, sample limitations and whether the result is `supported`, `not_supported` or `inconclusive`. A single view spike or a before/after comparison is not automatically causal. Only persist approved channel-specific lessons; do not rewrite a global law from one video.

Use [`templates/evidence_record.template.json`](templates/evidence_record.template.json) and [`templates/experience_record.template.json`](templates/experience_record.template.json) as the field contract. The template is not a claim that the current app automatically creates or validates every field.
