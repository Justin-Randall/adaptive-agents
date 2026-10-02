# PL-20261002: Active Plan Conformance and Migration Framework

Plan: PL-20261002-active-plan-conformance-migration

Readiness: Needs Review: scope and migration contract require user approval

Test approach: add validator fixtures for conforming, old, unversioned, and partially migrated `ACTIVE.md` documents; verify precise failure diagnostics, model-repair target conformance, idempotent upgrade behavior, and preservation of project-owned content

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

## Architectural Decisions

| Decision | Choice | Rationale |
| --- | --- | --- |
| Migration authority | The responsible model performs semantic migration; the validator is the hard acceptance gate. | The model can preserve meaning while the validator provides deterministic conformance. |
| Document metadata | Do not add provenance or template bookkeeping to human-readable Markdown. | Avoid polluting documents and creating competing sources of truth. |
| Unknown history | Treat old or unversioned plans as migration inputs, not as permanently exempt documents. | Every active plan must eventually conform to the current contract. |
| Migration feedback | Validator failures must name the missing structural requirement. | The model needs actionable feedback for bounded repair iterations. |
| Historical content | Preserve closed records and project-owned customizations. | Upgrade must not rewrite history or erase intentional local structure. |

## Related Work

- [Canonical retrospective](https://github.com/Justin-Randall/adaptive-agents/blob/main/retrospectives/resolved/2026-10-02-active-plan-progress-checklist.md)
- [Canonical upgrade guidance](https://github.com/Justin-Randall/adaptive-agents/blob/main/skills/upgrade-project-layer/SKILL.md)
