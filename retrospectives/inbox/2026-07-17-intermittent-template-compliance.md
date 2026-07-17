# Retrospective: Intermittent SDD template compliance during plan activation

- Date: 2026-07-17
- Status: Captured
- Scope: User-wide
- Session or task: Activating the Markdown Browser backlog item

## Observation

When activating a backlog item and creating the active plan (`ACTIVE.md`), agents intermittently omit required template sections that are present in the canonical template at `templates/project-layer/.adaptive-agents/planning/active/ACTIVE.md`. The user has observed this happening multiple times across different sessions.

Specifically, the `## Progress` section (with its three checkboxes) and the `## Supporting Documents` section were omitted in the most recent activation, despite being present in the template. The template's full structure includes: Objective, Specifications, Applicable Guidance, Scope, Acceptance Criteria, Progress, Decisions, Verification, and Supporting Documents.

## Evidence

- The canonical template (`templates/project-layer/.adaptive-agents/planning/active/ACTIVE.md`) includes `## Progress`, `## Decisions`, `## Verification`, and `## Supporting Documents` sections.
- The activated ACTIVE.md for PL-20260717-markdown-browser omitted `## Progress` and `## Supporting Documents` on first write (corrected after user review). `## Decisions` and `## Verification` were present.
- The user reports this has happened "a number of times already" across different sessions.
- The `manage-planning` skill at `.adaptive-agents/skills/manage-planning/SKILL.md` does not explicitly enumerate the required SDD template sections that must be included in an active plan.

## Impact

Inconsistent active plan structure means:

- Users must manually review and correct plans after activation, creating friction.
- Missing sections get overlooked until the validation step, requiring rework.
- The SDD model loses value when plans drift from the canonical structure.
- The template itself becomes less authoritative if agents routinely skip sections.

## Scope Decision

- Candidate: User-wide
- Rationale: This is an agent behavior pattern (template compliance), not specific to the Project Layer. The canonical template lives at `templates/project-layer/` and the fix likely belongs in instructions or skills that govern activation behavior (e.g., `instructions/coding.instructions.md`, the `manage-planning` skill, or the activation workflow in `global.instructions.md`).
- Project Layer considered: Project-local instructions already reference the template, but the issue is agent compliance with a defined structure, not the structure itself.

## Proposed User-Wide Target

- `instructions/coding.instructions.md`
- `.adaptive-agents/skills/manage-planning/SKILL.md`
- Or a new instruction about template requirements during plan activation

## Promotion Decision

- Status: Captured
- Decision:
- Rationale:

## Promotion Links

- None yet.
