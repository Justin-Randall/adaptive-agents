# Closed Work

Closed active packets are preserved in descriptive directories with one of these dispositions: `Completed`, `Deferred`, `Cancelled`, `Superseded`, or `Reopened`. Each directory contains:

- `<work-unit-id>.sdd.md` — the final SDD-formatted active plan at time of closure.
- `<work-unit-id>.backlog.md` — the original backlog entry, if the plan was activated from backlog.
- `<work-unit-id>.memory.md` — curated decisions, verified behavior, unresolved problems, constraints, and restart context.
- The memory artifact is a curated closure snapshot and remains immutable; reopened work links to it and carries forward only still-valid context.
- Legacy date-only artifact names and ID formats `PL-YYYYMMDDTHHMMSSZ` and `PL-####` remain accepted.

| ID | Plan | Disposition | Outcome |
| --- | --- | --- | --- |
| PL-20260709 | [Implement the Project Layer](PL-20260709-implement-project-layer/PL-20260709.sdd.md) | Completed | The canonical Project Layer template, bootstrap skill, upgrade workflow, scoped retrospectives, validation, and dogfood layer are all implemented and verified. |
| PL-20260710 | [Add SDD Output to Planning Artifacts](PL-20260710-add-sdd-output-to-planning-artifacts/PL-20260710.sdd.md) | Completed | SDD section structure defined, canonical template updated, manage-planning skill expanded, backlog conversion protocol documented, ID format migrated to ISO 8601, all validators passing. |
| PL-20260710 | [OpenCode Installer Support](PL-20260710-opencode-installer-support/PL-20260710.sdd.md) ([backlog](PL-20260710-opencode-installer-support/PL-20260710.backlog.md)) | Reopened | Dogfooding found that AGENTS.md was not honored; follow-up work is tracked as PL-20260711 OpenCode Installer Rework. |
| PL-20260711 | [Claude Code Support](PL-20260711-claude-code-support/PL-20260711-claude-code-support.sdd.md) ([backlog](PL-20260711-claude-code-support/PL-20260711-claude-code-support.backlog.md)) | Completed | Native `@AGENTS.md` import in `~/.claude/CLAUDE.md` plus a narrow `permissions.additionalDirectories` grant; dogfooded from an unrelated repo returning the sentinel and routing a backlog question through `manage-planning`. |
| PL-20260711 | [OpenCode Installer Rework](PL-20260711-opencode-installer-rework/PL-20260711-opencode-installer-rework.sdd.md) ([backlog](PL-20260711-opencode-installer-rework/PL-20260711-opencode-installer-rework.backlog.md)) | Completed | Diagnosed the false-positive sentinel (installed copy) and missing `permission.external_directory` grant; reworked to a single `instructions` entry loading canonical `AGENTS.md` plus a read/write trust grant, with legacy-layer migration. User-confirmed three-probe dogfood in the desktop app. |
