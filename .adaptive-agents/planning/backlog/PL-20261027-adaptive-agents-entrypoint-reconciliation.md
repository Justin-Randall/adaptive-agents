# Backlog: Reconcile Adaptive Agents AGENTS.md and INDEX.md

Plan: PL-20261027-adaptive-agents-entrypoint-reconciliation

Status: Backlog

Readiness: Needs Review: determine the canonical authority/routing split before changing bootstrap or integration behavior.

Test approach: Verify the chosen entrypoint contract across the repository discovery protocol, native harness integrations, bootstrap artifacts, validators, and fresh unrelated-project dogfood; preserve backward compatibility or document the migration.

## Objective

Clarify and, where necessary, simplify the relationship between the Adaptive Agents repository's `AGENTS.md` authority document and `INDEX.md` routing document so agents have one unambiguous bootstrap path without losing discoverability or tool-specific integration behavior.

## Problem Spec

`AGENTS.md` and `INDEX.md` currently reference one another as part of the repository's bootstrap and routing model. That relationship may reflect the repository's historical evolution rather than an intentional long-term architecture. The cyclic references can make it unclear which document is authoritative during startup, compaction recovery, native harness insertion, and session-index recovery. Total Recall currently needs a stable immediate recovery authority, so the broader entrypoint contract should be reconciled separately instead of being re-designed inside the Codex foundation child.

## Scope

In scope:

- Decide whether `AGENTS.md` is the sole authoritative operating document, whether `INDEX.md` is the sole routing document, or whether another explicit split is preferable.
- Map all repository, installer, harness, project-layer, and session-recovery references to both files.
- Remove accidental cyclic or contradictory instructions while preserving intentional navigation links.
- Define the compatibility and migration rules for existing installations and generated bootstrap content.
- Update tests, validators, and documentation after the authority/routing contract is approved.

Deferred:

- Changing the immediate Total Recall recovery contract, which will use `AGENTS.md` for now.
- Redesigning the entire Adaptive Agents repository information architecture beyond the two entrypoints.
- Reworking individual harness integrations unless required by the accepted entrypoint contract.

## Architectural Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Immediate Total Recall recovery authority | `AGENTS.md` | Use the existing canonical operating-instructions entrypoint while the broader relationship is unresolved. |
| Timing | Separate backlog item | Avoid expanding the active Codex Total Recall foundation scope with repository bootstrap redesign. |

## Related Work

- Related feature: [Total Recall for Session Details](PL-20261027-total-recall.md)
- Related active child: [Codex Total Recall Foundation](PL-20261027-total-recall/PL-20261027-total-recall-codex-foundation.md)
- Repository entrypoint: `AGENTS.md` and `INDEX.md`
