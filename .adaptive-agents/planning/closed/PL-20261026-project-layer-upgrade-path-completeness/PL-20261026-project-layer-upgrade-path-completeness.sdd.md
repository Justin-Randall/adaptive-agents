# PL-20261026: Complete the 0.9.2 Project Layer Upgrade Path

- Status: Completed
- Work Unit: PL-20261026-project-layer-upgrade-path-completeness
- Origin: Direct follow-up to [PL-20261025-completion-review-memory-template](../PL-20261025-completion-review-memory-template/PL-20261025-completion-review-memory-template.sdd.md)

## Progress

- [x] Review the 0.9.2 template changes against the documented existing-layer upgrade route.
- [x] Include every 0.9.2 template change in the upgrade instructions and align the dogfood backlog-item template.
- [x] Add focused contract coverage for the backlog template, upgrade route, and dogfood/template parity; run Project Layer plus full repository validation.
- [x] Review final changes and record the completion review.

## Objective

Make the review-based upgrade route complete for all Project Layer template changes shipped in version 0.9.2, including completion review and epic child-status tracking.

## Specifications

### Problem Spec

Version 0.9.2 includes a new work-unit memory review section and new backlog-item lifecycle/epic Children guidance. The upgrade skill currently describes only the completion-review change, and the dogfood backlog-item template does not yet include the epic Children section. Existing Project Layers could therefore reach 0.9.2 without adopting all versioned content.

### Feature Specs

- Update the 0.9.2 upgrade instructions to enumerate the memory template, backlog-item template, planning skill, and end-work playbook changes.
- Explain how to reconcile existing epic/child status metadata from verified active and closed records through a user-approved focused patch; preserve source specifications and do not rewrite closed history.
- Bring the dogfood backlog-item template into parity with the distributable template, including `Status: Backlog` and the epic Children table contract.
- Confirm child-status terminology remains consistent across canonical planning conventions, copied planning guidance, closure steps, and the backlog template; verify whether the dogfood layer has existing epics requiring backfill.
- Add focused regression coverage for the 0.9.2 backlog template and upgrade route.

### Interface / Contract Specs

- Template version remains `0.9.2` for this additive correction to its documented upgrade path.
- Existing Project Layer upgrades retain the inspect, propose, approve, apply, and validate sequence.
- When lifecycle state cannot be established from records, the upgrade must ask rather than infer it.

## Applicable Guidance

- `skills/upgrade-project-layer/SKILL.md` — versioned review and apply workflow.
- `instructions/planning-conventions.md` — canonical child status vocabulary and synchronization rules.
- `.adaptive-agents/playbooks/end-work.md` — approval-gated closure workflow.

## Test Plan

Add focused contract checks that assert the 0.9.2 Project Layer template includes the backlog lifecycle and epic Children section, the upgrade guidance includes this material, and dogfood/distributable backlog templates match. Manually verify status terminology across canonical guidance and check for existing dogfood epics to migrate. Run the Project Layer regression suite, dogfood validator, full Git Bash health check, and `git diff --check`.

## User-Facing Surface

- Surface: Existing Project Layer upgrade guidance and generated backlog-item template.
- Runtime scenario: Not applicable; this updates planning guidance and templates.
- Endpoint or runtime: Not run.

## User-Facing Validation

- Agent proof: Complete for the upgrade-template contract; no application runtime is involved.
- Evidence: Project Layer regression suite passed 43/43. Full Git Bash health passed 257 checks with 0 failures and 0 warnings. The dogfood and distributable backlog templates match exactly, the upgrade route names all 0.9.2 surfaces, and no epic/child records exist in the dogfood backlog to migrate.
- User handoff: Completed with user approval on 2026-10-26.

## DRY Assessment

- Status: Required.
- Scope: Upgrade procedure references and dogfood/distributable backlog template copies.
- Decision: Keep repeated template content aligned where the two independent Project Layer surfaces need it; route canonical status semantics through `instructions/planning-conventions.md` rather than duplicating the full policy.
- Result: Reviewed. Canonical status definitions stay in planning conventions; copied Project Layer guidance routes to that source. The short status field and Children table are intentionally present in both independently used backlog templates. No extraction or duplication detector adds value for this documentation/template change.
- Intentional/deferred duplication: The dogfood and distributable templates must remain behaviorally aligned.

## Scope

- Complete the 0.9.2 existing-layer upgrade path and dogfood/template parity for backlog-item guidance.
- Add focused contract coverage and validate the resulting branch state.
- Do not alter unrelated user-specific guidance or rewrite historical closed planning records.

## Acceptance Criteria

- [x] The 0.9.2 upgrade route names every changed template/guidance surface.
- [x] Existing epic and child status migration is approval-gated, evidence-based, and preserves historical/source content.
- [x] Dogfood and distributable backlog-item templates contain the same lifecycle and epic Children contract.
- [x] Canonical and Project Layer child-status guidance is consistent, and any dogfood epic migration need is resolved from verified records.
- [x] Focused regression tests, Project Layer validation, and full repository health pass.
- [x] The completion review records evidence, quality/DRY assessment, and findings disposition.

## Decisions

- Keep version `0.9.2`; this is a correction to the upgrade documentation for the same additive template release.
- Do not rewrite the just-closed PL-20261025 packet; this follow-up receives a new work-unit identity.

## Verification

- Git Bash `scripts/test-project-layer.sh` — 43 passed, 0 failed.
- Git Bash `scripts/check-adaptive-agents.sh --verbose` — 257 passed, 0 failed, 0 warnings.
- Dogfood and distributable backlog templates — byte-equivalent content; confirmed no existing dogfood epic/child records require migration.
- `git diff --check` — passed.

## Completion Review

- Final changes reviewed for correctness, regressions, and scope: the missing backlog-template upgrade step and dogfood Children section were added; a regression check now covers the versioned template, upgrade route, and template-copy parity. A full-check failure from a missing active-memory link was corrected before the successful final run.
- Acceptance criteria verified and remaining gaps identified: all 0.9.2 surfaces are named in the approval-gated upgrade instructions. Existing epic/child state reconciliation is evidence-based; closed packets stay immutable. No dogfood epics exist to backfill. Project Layer tests passed 43/43 and full health passed 257/257 with no warnings.
- Engineering quality assessed for clarity, maintainability, discoverability, scope, and semantic duplication: canonical status semantics remain in `instructions/planning-conventions.md`; generated guidance routes there. The dogfood/distributable backlog templates intentionally match. Focused contract checks guard template and upgrade discoverability; no implementation abstraction or duplication tool is warranted.
- Findings fixed or dispositioned: the previously incomplete upgrade route and dogfood template parity gap are fixed. The separate user-specific guidance backlog item remains independently recorded with its directory-placement decision open.

## Supporting Documents

- [PL-20261026-project-layer-upgrade-path-completeness memory](PL-20261026-project-layer-upgrade-path-completeness.memory.md)
- [Prior completed plan](../PL-20261025-completion-review-memory-template/PL-20261025-completion-review-memory-template.sdd.md)
- [Prior completed memory](../PL-20261025-completion-review-memory-template/PL-20261025-completion-review-memory-template.memory.md)
