# End Work

Use this playbook when active work appears complete or must stop.

1. Re-read `planning/active/ACTIVE.md` and its linked supporting documents.
2. Summarize acceptance-criteria status and verification evidence.
3. Propose exactly one disposition: `Completed`, `Deferred`, `Cancelled`, or `Superseded`.
4. Scan `planning/backlog/INDEX.md` before proposing deferred-work changes. Propose an update to an existing item or a new detailed item; do not write it yet.
5. Ask the user to approve or adjust the disposition, backlog changes, and closure.
6. After approval, move the complete active packet to `planning/closed/PL-####-descriptive-slug/` and update `planning/closed/INDEX.md`.
7. Create a fresh `planning/active/ACTIVE.md` and `MEMORY.md` only after the user chooses a backlog item or approves new direct exploratory, debugging, maintenance, or implementation work.
8. Update `planning/INDEX.md` and run `scripts/check-project-layer.sh`.

Never close work, alter the backlog, or select subsequent work without approval.
