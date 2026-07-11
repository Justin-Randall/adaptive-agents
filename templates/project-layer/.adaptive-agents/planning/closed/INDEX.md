# Closed Work

Closed active packets are preserved in descriptive directories with one of these dispositions: `Completed`, `Deferred`, `Cancelled`, or `Superseded`. Each directory contains:

- `<work-unit-id>.sdd.md` — the final SDD-formatted active plan at time of closure.
- `<work-unit-id>.backlog.md` — the original backlog entry, if the plan was activated from backlog.
- `<work-unit-id>.memory.md` — curated decisions, verified behavior, unresolved problems, constraints, and restart context.
- The memory artifact is a curated closure snapshot and remains immutable; reopened work links to it and carries forward only still-valid context.
- Legacy date-only artifact names and ID formats `PL-YYYYMMDDTHHMMSSZ` and `PL-####` remain accepted.

| ID | Plan | Disposition | Outcome |
| --- | --- | --- | --- |
