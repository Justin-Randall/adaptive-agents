# Project Retrospectives

Project retrospectives capture learning whose intended behavior may be specific to {{PROJECT_NAME}}.

| Directory | Status | Purpose |
| --- | --- | --- |
| [inbox/](inbox/) | Captured | Notes awaiting initial triage |
| [promoted/](promoted/) | Promoted | Lessons applied to durable guidance |
| [deferred/](deferred/) | Deferred | Set aside for later re-evaluation |
| [rejected/](rejected/) | Rejected | Considered and declined |

- Read the [inbox rules](inbox/README.md).
- Create notes from the [retrospective template](inbox/template.md).
- See [promoted/INDEX.md](promoted/INDEX.md), [deferred/INDEX.md](deferred/INDEX.md), [rejected/INDEX.md](rejected/INDEX.md) for directory indexes.
- After triage, move the note to the matching sibling directory and update its status.
- Use [Manage retrospectives](../skills/manage-retrospectives/SKILL.md) before triage or promotion.
- Run `bash scripts/migrate-project-layer-retrospectives.sh` to convert an existing flat-inbox layout.

Choose scope before target type. Promotion remains inside this Project Layer unless a separately approved, sanitized proposal establishes that the lesson belongs user-wide.
