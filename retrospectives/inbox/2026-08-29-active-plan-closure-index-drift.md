# Retrospective: Active Plan Closure Left Stale Content Visible

- Date: 2026-08-29
- Status: Captured
- Scope: User-wide
- Session or task: Closing and archiving an approved project-layer plan

## Observation

Replacing an active-plan pointer with a short `No active plan` placeholder did not remove the old plan content from the active file. The resulting Markdown began with the empty-state message and then continued with the completed plan, making the closed plan appear to remain active.

## Evidence

- The active planning file contained the new empty-state text followed by the full completed plan.
- The planning index said there was no active plan, but opening the active file still displayed the archived plan content.
- The completed packet had already been moved to the closed-work directory, so the stale display was caused by active-file content drift rather than an additional active plan.

## Impact

Agents and users can interpret stale content after an empty-state marker as an active plan, undermining planning status and making closure ambiguous. Empty-state files must be validated as complete documents, not only checked at their first line.

## Scope Decision

- Candidate: User-wide
- Rationale: The failure is a reusable planning-file closure and validation hazard that can occur in any project using the Adaptive Agents planning convention.
- Project Layer considered: The observed file belongs to one project, but the prevention rule applies to the shared planning workflow and should be reviewed before promotion.

## Proposed User-Wide Target

Where the lesson may belong after triage:

- `instructions/planning-conventions.md`
- `playbooks/adaptation-cycle.md`
- `skills/update-adaptive-agents/SKILL.md`

## Promotion Decision

- Status: Captured
- Decision: Defer promotion pending triage.
- Rationale: The failure is clear, but the narrowest durable owner and the exact validation rule should be selected during review.

## Promotion Links

- None yet.

---

*Captured for canonical Adaptive Agents triage; no durable rule was changed automatically.*
