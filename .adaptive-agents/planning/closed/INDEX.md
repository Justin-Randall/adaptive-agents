# Closed Work

Closed active packets are preserved in descriptive directories with one of these dispositions: `Completed`, `Deferred`, `Cancelled`, `Superseded`, or `Reopened`. Each directory contains:

- `PL-YYYYMMDD.sdd.md` — the final SDD-formatted active plan at time of closure.
- `PL-YYYYMMDD.backlog.md` — the original backlog entry, if the plan was activated from backlog.
- Legacy formats still accepted: `PL-YYYYMMDDTHHMMSSZ`, `PL-####`.

| ID | Plan | Disposition | Outcome |
| --- | --- | --- | --- |
| PL-20260709 | [Implement the Project Layer](PL-20260709-implement-project-layer/PL-20260709.sdd.md) | Completed | The canonical Project Layer template, bootstrap skill, upgrade workflow, scoped retrospectives, validation, and dogfood layer are all implemented and verified. |
| PL-20260710 | [Add SDD Output to Planning Artifacts](PL-20260710-add-sdd-output-to-planning-artifacts/PL-20260710.sdd.md) | Completed | SDD section structure defined, canonical template updated, manage-planning skill expanded, backlog conversion protocol documented, ID format migrated to ISO 8601, all validators passing. |
| PL-20260710 | [OpenCode Installer Support](PL-20260710-opencode-installer-support/PL-20260710.sdd.md) ([backlog](PL-20260710-opencode-installer-support/PL-20260710.backlog.md)) | Reopened | Dogfooding found that AGENTS.md was not honored; follow-up work is tracked as PL-20260711 OpenCode Installer Rework. |
