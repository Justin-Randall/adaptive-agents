# Retrospective: Closed Active Plans Must Archive and Leave an Empty Active Marker

- Date: 2026-09-12
- Status: Promoted
- Scope: User-wide
- Session or task: Closing a completed project-layer plan and setting the next active state to No plan

## Observation

A closure can leave either stale completed content in the active plan file or remove the active file without creating an explicit empty-state marker. In both cases, the project layer cannot reliably represent the current state. The correct closure operation is to archive the completed packet and replace the active pointer with only the minimal canonical empty-state marker, with no stale plan content remaining and no missing active state.

## Evidence

- A project-layer validation pass initially accepted the file shape only after the empty-state heading was added, but the file still contained the completed plan body.
- The user identified the stale content and explicitly requested a delete-style closure so a future active plan, including No plan, cannot inherit old content.
- An earlier captured retrospective records the same failure mode, establishing recurrence rather than a one-off formatting mistake.
- A later closure archived the completed packet and removed the active plan file but did not create the canonical empty-state replacement, leaving the active planning directory empty and its no-plan state undiscoverable.

## Impact

Agents can create contradictory or ambiguous planning state: indexes can say no plan is active while the active file appears to contain a live plan, or the active planning directory can be empty with no discoverable no-plan state. Closure workflows must archive the completed packet, then replace the active pointer with only the canonical empty marker, and validate that the marker contains no plan sections, objectives, or historical content.

## Scope Decision

- Candidate: User-wide
- Rationale: The failure has recurred across project-layer plan closures and concerns the shared planning lifecycle, not one project's domain.
- Project Layer considered: The current project exposed the failure, but project-local guidance cannot prevent the same closure behavior in other projects using the shared planning workflow.

## Proposed User-Wide Target

- `instructions/planning-conventions.md`
- `skills/manage-planning/SKILL.md`
- `templates/project-layer/.adaptive-agents/playbooks/end-work.md`
- `templates/project-layer/.adaptive-agents/scripts/check-project-layer.sh`
- `scripts/inspect-project-layer-upgrade.sh`

## Promotion Decision

- Status: Promoted
- Decision: Promoted to durable planning guidance, Project Layer validation, and upgrade inspection.
- Rationale: The recurrence was confirmed, the empty-state contract was clarified, and focused regression coverage now protects the archive-first closure workflow.

## Promotion Links

- [Planning conventions](../../instructions/planning-conventions.md)
- [Manage planning](../../skills/manage-planning/SKILL.md)
- [Project Layer end-work playbook](../../templates/project-layer/.adaptive-agents/playbooks/end-work.md)
- [Project Layer validator](../../templates/project-layer/.adaptive-agents/scripts/check-project-layer.sh)
- [Project Layer upgrade inspector](../../scripts/inspect-project-layer-upgrade.sh)

---

*Promoted after explicit user approval and repository validation.*
