# End Work

Use this playbook when active work appears complete or must stop.

1. Re-read `planning/active/ACTIVE.md` and its linked supporting documents.
2. Summarize acceptance-criteria status and verification evidence.
3. Propose exactly one disposition: `Completed`, `Deferred`, `Cancelled`, or `Superseded`.
4. Scan `planning/backlog/INDEX.md` before proposing deferred-work changes. Propose an update to an existing item or a new detailed item; do not write it yet.
5. Ask the user to approve or adjust the disposition, backlog changes, and closure.
6. After approval:
   - Curate the active `<work-unit-id>.memory.md` to preserve decisions, verified behavior, unresolved problems, rejected approaches, constraints, and restart context; remove stale session detail.
   - Create `planning/closed/<work-unit-id>/`.
   - Save `ACTIVE.md` as `planning/closed/<work-unit-id>/<work-unit-id>.sdd.md`.
   - Move `<work-unit-id>.memory.md` into the same directory without renaming it so the SDD's relative link remains valid.
   - If the plan was activated from a backlog item, copy it into the same directory as `<work-unit-id>.backlog.md`.
   - Update `planning/closed/INDEX.md` with the new entry.
   - If the disposition is **Completed**, **Cancelled**, or **Superseded**, remove the backlog entry from `planning/backlog/INDEX.md` (the backlog file stays, only the index entry is removed). If the disposition is **Deferred**, leave the backlog entry in place.
7. Create a fresh `planning/active/ACTIVE.md` and `<new-work-unit-id>.memory.md` only after the user chooses a backlog item or approves new direct exploratory, debugging, maintenance, or implementation work. For reopened work, link the prior closed SDD and memory and carry forward only still-valid context.
8. Update `planning/INDEX.md` and run `scripts/check-project-layer.sh`.

Never close work, alter the backlog, or select subsequent work without approval.
