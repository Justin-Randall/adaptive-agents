---
name: manage-planning
description: "Use when: reading or changing the Project Layer active plan, working memory, backlog, or closed-work history."
---

# Manage Planning

Use [Planning](../../planning/INDEX.md) as the authoritative planning router.

## Start Work

1. Read `planning/active/ACTIVE.md` and its linked supporting documents.
2. If the current request changes the active objective, explain the conflict and ask whether to close, replace, or retain the current plan.
3. Work may originate from a backlog plan or begin directly as approved research, debugging, maintenance, or implementation.
4. Never activate work silently.

## Record Deferred Work

1. Keep out-of-scope discoveries in `planning/active/MEMORY.md` while evaluating them.
2. Scan `planning/backlog/INDEX.md` before opening detailed backlog plans.
3. Propose updating a matching detailed plan or creating a new `PL-####-descriptive-slug.md` plan.
4. Wait for approval before changing the backlog index or detailed plans.

## Maintain Active Context

- Keep progress, acceptance criteria, decisions, and verification in `ACTIVE.md`.
- Curate `MEMORY.md` for handoff-critical state; replace stale details instead of appending a session transcript.
- Link every active supporting Markdown document from `ACTIVE.md`.

## End Work

Follow [End work](../../playbooks/end-work.md). Closure, disposition, backlog continuations, and subsequent work all require user approval.

Run `bash .adaptive-agents/scripts/check-project-layer.sh` after planning structure changes.