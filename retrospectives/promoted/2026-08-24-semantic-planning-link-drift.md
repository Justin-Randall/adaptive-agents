# Retrospective: Semantic Planning Link Drift

- Date: 2026-08-24
- Status: Promoted
- Scope: User-wide
- Session or task: Activating a Project Layer plan and validating lifecycle links

## Observation

A moving active-plan document was used as the target for dependencies and historical references. After a new plan became active, those links remained technically valid but changed meaning: a dependency could resolve to the current plan itself, and older records could appear to refer to unrelated active work.

## Evidence

- The existing Project Layer validator reported no failures while the semantic dependency was wrong.
- A targeted scan found active-plan references in backlog entries, closed records, and operational guidance; 19 files required manual correction.
- The corrections accumulated over many weeks, demonstrating a repeated pattern of incorrect historical-link behavior rather than a single incidental mistake.
- Replacing historical references with immutable work-unit documents repaired the dependency direction without changing the active-work routing convention.

## Impact

Path existence and reachability checks are insufficient for lifecycle-managed planning links. Activation and closure must preserve historical provenance, and validation must distinguish intentional current-work references from historical references that become misleading when the active plan rotates.

## Scope Decision

- Candidate: User-wide
- Rationale: The issue recurred across 19 files over many weeks, and any Project Layer that uses a moving active-plan document can experience the same semantic drift. The lifecycle invariant and validation policy should be shared across projects.
- Project Layer considered: The immediate link repair is project-local, but the underlying activation, closure, and validator behavior is part of the shared Project Layer contract.

## Proposed User-Wide Target

- `skills/manage-planning/` — state that active-plan paths are moving current-work pointers, not historical provenance, and require retargeting during activation and closure.
- `templates/project-layer/` — add deterministic checks for self-referential active-plan links and historical links from backlog or closed records to the moving active path.
- `scripts/test-project-layer.sh` — add regression fixtures for allowed current-work links, rejected self-references, and rejected historical active-plan links.
- Optional future `skills/` workflow — provide model-assisted review for ambiguous prose relationships, producing suggestions only and requiring human approval.

## Template and Upgrade Implications

- This validation refinement should be a patch-level Project Layer template release because it adds checks and guidance without requiring new project-owned content or a structural migration.
- New Project Layers receive the behavior from the latest template.
- Existing Project Layers retain their copied validator until they run the review-based upgrade workflow; the upgrade must preserve project-owned plans, memory, backlog, closed history, and customizations.
- A user-wide installation may also run the canonical validator against multiple target layers for fleet-wide audits, but that does not replace the versioned validator stored with each layer.

## Validator Placement Tradeoff

Keeping a small validator in each Project Layer provides version-pinned, offline, target-local validation and lets a layer validate the contract it claims to use. The cost is copied implementation drift and the need for explicit upgrades.

A single user-wide validator centralizes fixes but requires every host to resolve the canonical installation and weakens versioned-template semantics. The preferred design is hybrid: canonical source and upgrade workflow in Adaptive Agents, a version-aware validator in each Project Layer, and optional centralized auditing for multiple targets.

## Promotion Decision

- Status: Promoted
- Decision: Applied the approved promotion patch to the planning guidance, Project Layer template validator, and regression tests.
- Rationale: The recurring 19-file failure pattern was confirmed as a user-wide lifecycle issue, and the approved durable guidance and validation changes are now in place.

## Promotion Links

- [Manage planning](../../skills/manage-planning/SKILL.md)
- [Project Layer planning skill](../../templates/project-layer/.adaptive-agents/skills/manage-planning/SKILL.md)
- [Project Layer validator](../../templates/project-layer/.adaptive-agents/scripts/check-project-layer.sh)
- [Project Layer validator tests](../../scripts/test-project-layer.sh)
