# PL-20261002: Active Plan Conformance and Migration Framework

Plan: PL-20261002-active-plan-conformance-migration

Readiness: Needs refinement: narrow the item to repeat-migration idempotence before activation

Test approach: add an executable repeat-migration check; verify byte-stable output, validator-gated conformance, and preservation of unrelated active support files and closed records

## Objective

Complete the deferred repeat-migration/idempotence proof for the existing validator-first active-plan migration workflow without introducing automatic semantic rewriting or provenance metadata.

## Problem Spec

The active-plan conformance and migration framework is implemented, but its deferred repeat-migration guarantee is not executablely verified. A follow-up must prove that a conforming migrated plan remains byte-stable and that repeated validation or migration does not rewrite unrelated active support files or closed records.

## Scope

In scope:

- Define an executable repeat-migration/idempotence check for the existing workflow.
- Verify a conforming migrated `ACTIVE.md` remains byte-stable on repeat processing.
- Verify repeated processing is validator-gated and limited to the active plan being repaired.
- Verify unrelated active support files and closed records remain unchanged.

Out of scope:

- Reworking the already-implemented progress contract, validator diagnostics, migration guidance, or legacy/custom fixtures.
- Automatic semantic rewriting of arbitrary Markdown.
- Document-level version headers, footers, sidecars, or other provenance bookkeeping.
- Automatic migration of unrelated project-owned files or closed historical records.

## Architectural Decisions

| Decision | Choice | Rationale |
| --- | --- | --- |
| Migration boundary | The follow-up proves repeat processing only; semantic repair remains model-directed. | Keep the executable check from becoming an automatic Markdown rewriter. |
| Idempotence evidence | Compare the active plan and protected neighboring records before and after repeat processing. | Demonstrate byte stability and preservation rather than infer it from a validator pass. |
| Historical content | Preserve closed records and project-owned customizations. | The check must fail if repeat processing changes unrelated history. |

## Related Work

- [Prior closed plan](https://github.com/Justin-Randall/adaptive-agents/blob/main/.adaptive-agents/planning/closed/PL-20261002-active-plan-conformance-migration/PL-20261002-active-plan-conformance-migration.sdd.md)
- [Canonical upgrade guidance](https://github.com/Justin-Randall/adaptive-agents/blob/main/skills/upgrade-project-layer/SKILL.md)
