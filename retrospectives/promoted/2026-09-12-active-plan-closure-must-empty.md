# Retrospective: Closing Without Replacement Must Leave No Plan

- Date: 2026-09-12
- Status: Promoted
- Scope: User-wide
- Session or task: Closing a completed project-layer plan without selecting replacement backlog work

## Required Behavior

When the user closes the active plan without asking for a new active plan, set `planning/active/ACTIVE.md` to exactly:

```markdown
# No Active Plan
```

Archive the completed plan separately in `planning/closed/<work-unit-id>/`. Do not leave the completed plan, a partial plan, or active supporting-file links in `planning/active/`.

## Failure Observed

Previous closures either left the completed plan body under an empty heading or removed `ACTIVE.md` without creating the no-plan marker. Both outcomes made the active planning state incorrect or undiscoverable.

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
