# Retrospective: Active Plan Layout and Validator Mismatch

- Date: 2026-08-30
- Status: Promoted
- Scope: User-wide
- Session or task: Activating a project-layer plan while investigating a token-accounting regression

## Observation

The agent created a nested work-unit directory under the project layer's active planning directory and placed an `ACTIVE.md` there, even though the project convention uses one root `planning/active/ACTIVE.md` as the current-work entry point. After user correction, the agent consolidated the plan correctly, but then created a companion work-unit memory file because the local validator required it. The user clarified that the intended active layout is a single `ACTIVE.md` and asked that the reusable process lesson be captured in the system Adaptive Agents repository.

## Evidence

- The project planning router explicitly identifies `planning/active/ACTIVE.md` as the current-work entry point.
- The project validator rejected the root plan until a work-unit memory filename was present, although that companion-file requirement was not stated in the project-layer planning instruction.
- The user corrected the nested-directory assumption and separately requested a user-wide retrospective.
- The active plan was ultimately consolidated into the root `ACTIVE.md`; the companion memory file was restored only after the user approved it to satisfy validation.

## Impact

Agents can overfit to retired-plan directory examples or validator behavior and introduce extra active-plan files that violate the project's intended current-work shape. When instructions and validation checks disagree, silently choosing one creates avoidable churn and erodes user trust. The agent should identify the disagreement, state it plainly, and follow the user's explicit structural requirement while recording the validation conflict.

## Scope Decision

- Candidate: User-wide
- Rationale: The failure mode is a reusable agent workflow problem involving plan activation, instruction precedence, and validator interpretation. It can recur in unrelated repositories that have moving active pointers and automated structural checks.
- Project Layer considered: The repository-specific path and validator details belong to the project layer, but the general lesson about checking both the authoritative instruction and validator, and resolving conflicts explicitly, applies across projects.

## Proposed User-Wide Target

The lesson is implemented in:

- `skills/manage-planning/SKILL.md`

## Promotion Decision

- Status: Promoted
- Decision: Add a planning workflow for reconciling explicit user instructions with validator results.
- Rationale: The skill now requires comparing the project contract, template version, and validator tests before recommending a change, and requires honest reporting when a user intentionally overrides a valid check.

## Promotion Links

- [Manage planning skill](../../skills/manage-planning/SKILL.md) — directs agents to investigate and explain instruction/validator conflicts before changing project structure or the validator.
- [Project Layer planning skill](../../templates/project-layer/.adaptive-agents/skills/manage-planning/SKILL.md) — documents the active-plan and memory-file contract involved in the originating mismatch.
- [Project Layer validator](../../templates/project-layer/.adaptive-agents/scripts/check-project-layer.sh) — enforces the canonical active-plan and supporting-memory structure.

---

*Promoted after review; the conflict-resolution workflow is now part of planning guidance.*
