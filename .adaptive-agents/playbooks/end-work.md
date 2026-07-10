# End Work

Use this playbook when active work appears complete or must stop.

1. Re-read `planning/active/ACTIVE.md` and its linked supporting documents.
2. Summarize acceptance-criteria status and verification evidence.
3. Propose exactly one disposition: `Completed`, `Deferred`, `Cancelled`, or `Superseded`.
4. Scan `planning/backlog/INDEX.md` before proposing deferred-work changes. Propose an update to an existing item or a new detailed item; do not write it yet.
5. Ask the user to approve or adjust the disposition, backlog changes, and closure.
6. After approval:
   - Create a directory `planning/closed/PL-YYYYMMDDTHHMMSSZ-descriptive-slug/`.
   - Save the current SDD-formatted `ACTIVE.md` as `planning/closed/PL-YYYYMMDDTHHMMSSZ-descriptive-slug/PL-YYYYMMDDTHHMMSSZ.sdd.md`.
   - If the plan was activated from a backlog item, copy the original backlog entry into the same directory as `planning/closed/PL-YYYYMMDDTHHMMSSZ-descriptive-slug/PL-YYYYMMDDTHHMMSSZ.backlog.md`.
   - Update `planning/closed/INDEX.md` with the new entry.
   - If the disposition is **Completed**, **Cancelled**, or **Superseded**, remove the backlog entry from `planning/backlog/INDEX.md` (the backlog file stays, only the index entry is removed). If the disposition is **Deferred**, leave the backlog entry in place.
7. Create a fresh `planning/active/ACTIVE.md` and `MEMORY.md` only after the user chooses a backlog item or approves new direct exploratory, debugging, maintenance, or implementation work.
8. Update `planning/INDEX.md` and run `scripts/check-project-layer.sh`.

Never close work, alter the backlog, or select subsequent work without approval.
