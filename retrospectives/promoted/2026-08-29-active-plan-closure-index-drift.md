# Retrospective: Active Plan Closure Left Stale Content Visible

- Date: 2026-08-29
- Status: Promoted
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

The lesson is implemented in:

- `skills/manage-planning/SKILL.md`
- `templates/project-layer/.adaptive-agents/scripts/check-project-layer.sh`
- `scripts/test-project-layer.sh`

## Promotion Decision

- Status: Promoted
- Decision: Promote the existing full-file closure rule and validator regression coverage.
- Rationale: The shared planning skill requires replacing the complete active file, and the Project Layer validator and regression suite reject stale plan content after the empty-state marker.

## Promotion Links

- [Manage planning skill](../../skills/manage-planning/SKILL.md) — requires replacing the entire active plan with the empty-state document.
- [Project Layer validator](../../templates/project-layer/.adaptive-agents/scripts/check-project-layer.sh) — validates the empty-state document and rejects leftover plan content.
- [Project Layer regression tests](../../scripts/test-project-layer.sh) — covers stale plan sections and work-unit metadata after the empty-state marker.

---

*Promoted after review; the linked guidance and validation coverage are in place.*
