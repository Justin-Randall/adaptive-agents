# PL-20261002: Active Plan Conformance and Migration Framework

- Work Unit: PL-20261002-active-plan-conformance-migration
- Source: [Backlog item](../../backlog/PL-20261002-active-plan-migration-validation.md)
- Memory: [PL-20261002-active-plan-conformance-migration.memory.md](PL-20261002-active-plan-conformance-migration.memory.md)

## Progress

- [x] Plan activated from approved backlog item
- [x] User review of active-plan specification
- [x] Implement active-plan progress contract and canonical template updates
- [x] Implement validator diagnostics and model-directed migration guidance
- [x] Add and run focused regression fixtures
- [x] Run full Project Layer and repository validation
- [x] Verify behavior and validation
- [x] Close or defer remaining work

## Objective

Define and implement a reusable validator-first framework that brings any older, unversioned, or custom-format active plan into the current `ACTIVE.md` contract through model-directed semantic repair, without embedding provenance or bookkeeping metadata in human-readable documents.

## Problem Spec

Active plans may lack newly required structural sections such as a progress checklist, or may express equivalent progress information in a project-specific format. The validator cannot reliably determine which historical template produced an unversioned document, and should not attempt semantic interpretation. Treating nonconforming documents as permanently exempt weakens the contract, while requiring document-level version metadata pollutes the Markdown and creates another source of truth. The responsible model should interpret the existing plan, map its meaning to the current structure, and use validator feedback to complete the migration.

## Scope

In scope:

- Define the current structural contract for active-plan progress tracking.
- Define the migration boundary and repair loop for arbitrary legacy or project-specific `ACTIVE.md` formats.
- Update the canonical `ACTIVE.md` template and applicable planning or upgrade guidance.
- Make validation fail clearly when an active plan does not meet the current contract.
- Ensure validator failures identify actionable missing sections or invariants for model repair.
- Define model-directed migration behavior that maps existing intent, decisions, scope, identity, and evidence without silently changing substantive content.
- Add regression fixtures for current, old, unversioned, partially migrated, and conforming active plans.
- Verify migration is repeatable, validator-gated, and limited to the active plan being repaired.

Deferred:

- Automatic rewriting of all older Markdown outside the active-plan workflow.
- Document-level version headers, footers, sidecars, or other provenance bookkeeping.
- Guessing the historical template version of an unversioned document.
- Automatic migration of unrelated project-owned files or closed historical records.
- Silent changes to substantive scope, acceptance criteria, decisions, or evidence.

## Specifications

### Active-Plan Contract

- New active plans must contain a short top-level progress checklist near the metadata.
- The checklist tracks lifecycle stages and remains distinct from implementation tasks, acceptance criteria, and the detailed test plan.
- Plan-specific stages are allowed; inapplicable stages may be marked `N/A` or omitted.
- Completion of implementation does not imply completion of validation, delivery, or dogfooding.

### Migration Workflow

- Treat old, unversioned, and custom-format active plans as inputs to semantic migration.
- The responsible model preserves the plan's intent, decisions, scope, identity, and evidence while mapping them to the current structure.
- The validator provides deterministic, actionable failures and is the hard acceptance gate.
- Migration is bounded to the active plan under repair and must be repeatable without silently changing substantive content.

## Acceptance Criteria

- [x] The canonical active-plan template and applicable guidance define the progress checklist contract.
- [x] The Project Layer validator rejects active plans that fail the current contract with actionable diagnostics.
- [x] Upgrade guidance defines model-directed repair for legacy, unversioned, and custom-format active plans.
- [x] Regression fixtures cover current, old, unversioned, partially migrated, custom-format, and conforming active plans.
- [ ] Repeated migration/validation is idempotent and does not rewrite unrelated or closed records.
- Focused validation: `bash scripts/test-project-layer.sh` — 32 passed, 0 failures.
- Full validation: `bash scripts/check-adaptive-agents.sh` — 241 passed, 0 failures, 0 warnings.

## Closure

- Disposition: Deferred
- Deferred work: Add an executable repeat-migration idempotence check while preserving the current model-directed migration boundary.

## Decisions

| Decision | Choice | Rationale |
| --- | --- | --- |
| Migration authority | The responsible model performs semantic migration; the validator is the hard acceptance gate. | The model can preserve meaning while the validator provides deterministic conformance. |
| Document metadata | Do not add provenance or template bookkeeping to human-readable Markdown. | Avoid polluting documents and creating competing sources of truth. |
| Unknown history | Treat old or unversioned plans as migration inputs, not as permanently exempt documents. | Every active plan must eventually conform to the current contract. |
| Migration feedback | Validator failures must name the missing structural requirement. | The model needs actionable feedback for bounded repair iterations. |
| Historical content | Preserve existing evidence and project-owned structure within the active plan; do not migrate unrelated or closed records. | Upgrade must not rewrite history or erase intentional local structure. |

## Applicable Guidance

- [Manage planning](../../../skills/manage-planning/SKILL.md): activation, active context, testing, validation, and closure workflow.
- [Planning conventions](https://github.com/Justin-Randall/adaptive-agents/blob/main/instructions/planning-conventions.md): work-unit sizing, test planning, and DRY assessment requirements.
- [Testing instructions](https://github.com/Justin-Randall/adaptive-agents/blob/main/instructions/testing.instructions.md): focused failing tests before production changes and broadened validation after the slice passes.
- [Upgrade Project Layer skill](https://github.com/Justin-Randall/adaptive-agents/blob/main/skills/upgrade-project-layer/SKILL.md): version compatibility and migration ordering.
- [Manage retrospectives](../../../skills/manage-retrospectives/SKILL.md): resolution evidence for the originating retrospective.

## Test Plan

For each validator or migration-guidance slice, write the focused failing fixture or check first, run it to confirm the failure, make the smallest change, rerun the focused check, and broaden validation only after the slice passes.

- Validate conforming, old, unversioned, partially migrated, and custom-format active-plan fixtures with `bash scripts/test-project-layer.sh`.
- Verify missing progress structure produces actionable validator diagnostics rather than an indefinite compatibility exemption.
- Verify a migrated plan passes validation and a repeated migration attempt is idempotent.
- Verify unrelated active supporting files and closed records are unchanged.
- Run `bash .adaptive-agents/scripts/check-project-layer.sh` and `bash scripts/check-adaptive-agents.sh` after focused tests pass.

## DRY Assessment

- Validator and fixture changes touch canonical and dogfood Project Layer implementations, so a duplication review is required.
- A jscpd scan is not required before implementation because the initial change is expected to be test fixtures and narrowly aligned validators; reassess if shared validation logic is introduced.

## Related Work

- [Canonical retrospective](https://github.com/Justin-Randall/adaptive-agents/blob/main/retrospectives/resolved/2026-10-02-active-plan-progress-checklist.md)
- [Canonical upgrade guidance](https://github.com/Justin-Randall/adaptive-agents/blob/main/skills/upgrade-project-layer/SKILL.md)
