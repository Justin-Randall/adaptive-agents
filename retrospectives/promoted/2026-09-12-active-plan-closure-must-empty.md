# Retrospective: Closed Active Plans Must Leave an Empty Active Marker

- Date: 2026-09-12
- Status: Promoted
- Scope: User-wide
- Session or task: Closing a completed project-layer plan and setting the next active state to No plan

## Observation

A closure edit changed the active plan heading to an empty-state marker but left the completed plan body in the same file. The project layer therefore reported no active plan while still displaying the closed plan's full specification. The correct closure operation is to archive the completed packet and replace the active pointer with only the minimal empty-state marker, with no stale plan content remaining.

## Evidence

- A project-layer validation pass initially accepted the file shape only after the empty-state heading was added, but the file still contained the completed plan body.
- The user identified the stale content and explicitly requested a delete-style closure so a future active plan, including No plan, cannot inherit old content.
- An earlier captured retrospective records the same failure mode, establishing recurrence rather than a one-off formatting mistake.

## Impact

Agents can create contradictory planning state: indexes say no plan is active while the active file appears to contain a live plan. Closure workflows must treat the active pointer as a replace-or-delete operation and validate that an empty state contains no plan sections, objectives, or historical content.

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