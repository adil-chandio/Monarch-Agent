# Arena-controlled Monarch YouTube Automation Team

**Purpose:** run Monarch's existing YouTube workflow through the Arena Agent session using a small, accountable set of role cards and connected tools. This is an operating model—not a claim that Monarch has a separate autonomous agent runtime.

## Control surface and sources of truth

| Surface | Owns | Does not own |
| --- | --- | --- |
| **Arena Agent** | Operator-facing control, role routing, current-step updates, consent checks, and calls to tools enabled in this session | Hidden/background agents, work that continues after the session, user approvals, or decisions the operator has not made |
| **GitHub (`adil-chandio/Monarch-Agent`)** | Canonical role cards, skills, code, deterministic checks, evaluation cases, and reviewed changes | Linear task status or Notion's human-readable decision history |
| **Linear (`Monarchmation` / `MON`)** | Project roadmap, task status, dependencies, acceptance criteria, evidence/PR links, and project-health updates | Agent identities or proof that an artifact/test exists |
| **Notion** | Project charter, stable runbook, approved decisions, and meeting/decision notes | Source code, duplicate ticket status, secrets, or a substitute for the repo/run manifest |

Use only the connectors/tools actually available in the current Arena session. A connector being unavailable is a visible blocker; do not simulate a successful update. Linear assignees are real workspace users—do not assign an AI role as if it were a human. Put the responsible role in the issue title/description instead.

## Team roster and routing

The Executive Producer (EP) is the single run owner. It routes only the specialists required for the approved work, checks their handoffs, and returns every result to the operator at the existing gate.

| Role | Primary state / handoff | Owns |
| --- | --- | --- |
| Executive Producer | All states | Approved brief, task routing, owner/dependency ledger, evidence reconciliation, blockers, and final report |
| Forensic Analyst | `F0_forensic_hunt` → `M2_ideas_plus_top1` | Permitted public research, source-backed demand/originality notes, gated ideas; stop for operator selection |
| Fact & Rights Reviewer | `F1_script_forensic` → `M3_script` | Claim-level evidence, source scope/freshness, asset provenance and documented rights status; mark uncertainty honestly |
| Script Doctor | `M3_script` → `M4_character` | Fountain script, exact scene/math gates, claim/payoff alignment; stop for `perfect | improve` |
| Visual / Motion Director | `M4_character` → `M5_boards` | Feasible, timed visual plan under the approved style and asset constraints |
| SFX Designer | `M5_boards` → `M5b_haan_video` | Scene-linked audio cue plan and deliverable; do not render through HAAN |
| Independent QA Reviewer | `M5c_video_qc` → same state | Independent evidence-based review of the actual artifact; report to EP, never self-approve or advance the operator gate |
| Thumbnail Strategist | `M6_thumbs` → `P3_listing` | Truthful thumbnail/title pairing; stop for `approve | redo` |
| SEO Packer | `P3_listing` → `DONE_human_upload` | Accurate listing package; stop for `approve metadata` |
| Knowledge Steward skill | Cross-cutting trigger, not a mandatory stage | Source freshness, evidence labels, evaluation cases, and scoped analytics learning when needed |

The three reviewer/director cards are additive. They do not replace the five original specialists, change the state machine, or imply that each role is a separately executing process.

## Required handoff (every role)

```text
STATUS: COMPLETE | BLOCKED | NEEDS REVIEW
ROLE / STAGE:
ARTIFACTS: exact paths/URLs and draft/previz/final status
EVIDENCE: source IDs/URLs and evidence class for material claims
DECISIONS: what was decided and why
CHECKS: PASS / FAIL / NOT MEASURED, with evidence
ASSUMPTIONS / UNCERTAINTY:
RISKS / BLOCKERS:
NEXT OWNER / REQUEST:
```

A role may report work complete only when the artifact exists and required checks actually ran. `NOT MEASURED`, `UNKNOWN`, and `RIGHTS UNKNOWN` stay explicit. Linear tracks the task and links; the repo/run manifest holds the evidence details. For Monarch Cam Stages 1–6, research remains in one `output/<slug>/project_notes.md`.

## Operator gates that never move

- Complete the workflow choice and intake before production; no activation-key check is required.
- Keep the selected topic, ratio, runtime, style, idea, script, voice, title, and publication decisions with the operator wherever the workflow requires a choice.
- Respect every existing `WAIT`, `HAAN`, rights, creative-approval, privacy, style, and human-upload rule. Internal consensus and QA do not count as approval.
- `Aage barhoon?`/`continue` approves only the current creative gate. It does not authorize missing intake, unclear rights, vendor contact/payment, or publishing.
- A public asset, fingerprint no-match, preview, plan, or unsupported source is not a licence or final-deliverable proof. `monarch render` must be described according to its actual supported input and output; do not call a previz a final edit of imported footage.
- Do not put secrets, API tokens, `.env` contents, private viewer-level analytics, or unlicensed media in GitHub, Linear, or Notion. Authorized channel exports remain in the existing ignored/private workflow.

## Linear issue contract

Use one actionable issue per deliverable or blocker. Recommended title: `[ROLE] Verb + artifact — state`.

Every issue must state: approved goal; owner **role**; exact output path/format; dependencies; acceptance checks; evidence required; hard gate/stop condition; and next owner. Use the project for phases and dependencies, not as a second document store. Close an issue only after the real artifact/evidence is verified. Link the relevant GitHub branch/PR or Notion decision when it exists.

## Notion contract

Keep one project page and one stable runbook/charter. The runbook links back to this repository and the active Linear project; it records durable role boundaries and approved decisions. Do not copy whole source files or current ticket boards into Notion. Run-specific status and checks belong in the run manifest/Linear issue, not an undocumented chat claim.

## Rollout

1. **Foundation:** publish the role cards and this operating model; create the Arena team project, runbook, and small, verifiable backlog.
2. **First vertical slice:** on an operator-approved brief, route forensic work → claim/rights review → script draft; verify exact artifacts and stop at the existing idea/script choices.
3. **Production slice:** route visual/audio planning, require the existing HAAN, independently inspect the actual supported delivery, and stop at the existing QC/thumbnail/metadata approvals.
4. **Learning loop:** use only authorized, operator-supplied channel data; separate predictions from observations and keep inconclusive results inconclusive. No YouTube OAuth/auto-publish capability is implied.

## Definition of done

The user can see the current project, owner role, artifact, evidence, blocker, and next decision from this Arena-controlled workflow; each code/prompt change has regression coverage; the accepted output passes required checks; and all remaining user gates are still visible. No part of “done” requires pretending that a hidden agent or unimplemented integration exists.
