# Retrospective: Active Plan Layout and Validator Mismatch

- Date: 2026-08-30
- Status: Captured
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

Where in the canonical Adaptive Agents repository might this belong if promoted?

- `instructions/`
- `skills/`
- `playbooks/`
- `memory/`
- Not sure yet

## Promotion Decision

- Status: Captured
- Decision: Defer triage and promotion until explicit review.
- Rationale: The observation is concrete and user-confirmed, but the correct durable target and whether the validator convention should be generalized require review. Do not promote this raw note automatically.

## Promotion Links

Add Markdown links to changed durable guidance files if promoted.

- None yet.

---

*After triage, move this note to `promoted/`, `deferred/`, or `rejected/` and update its status and promotion links.*
