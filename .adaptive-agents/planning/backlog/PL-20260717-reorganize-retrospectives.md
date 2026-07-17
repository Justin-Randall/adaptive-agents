# PL-20260717: Reorganize retrospectives directory structure

- Status: Backlog
- Readiness: Ready
- Created: 2026-07-17
- Tags: retrospectives, organization

## Objective

Reorganize the `retrospectives/` directory so the `inbox/` folder contains only notes awaiting initial triage (status `Captured`). Promoted, deferred, and rejected retrospectives live in sibling directories so a glance at the directory tree reveals how many items remain open.

## Problem Spec

The current `retrospectives/inbox/` contains a mix of all statuses — 14 `Promoted`, 9 `Captured`, 1 `Deferred`, 0 `Rejected` (as of 2026-07-17). A quick glance at the directory does not distinguish between "items that still need triage" and "items that have already been resolved." This makes prioritization, review, and inbox shipping harder than necessary.

Queue-separation principle:

- **`inbox/`** = needs initial triage only (`Captured` status)
- **`deferred/`** = triaged, set aside for later re-evaluation (`Deferred` status — an explicit user decision to revisit)
- **`promoted/`** = lesson has been applied to durable guidance (`Promoted` status)
- **`rejected/`** = considered and declined (`Rejected` status, retained per "do not delete" principle)

## Scope

### Included

1. Create four sibling directories in canonical `retrospectives/`: `inbox/`, `promoted/`, `deferred/`, `rejected/`.
2. Move existing canonical notes to the directory matching their status via `git mv` (preserves rename history).
3. Create `retrospectives/INDEX.md` as a routing map listing each sibling directory with note counts (following `planning/INDEX.md` pattern).
4. Create `retrospectives/rejected/INDEX.md` with guidance on what belongs in `rejected/` (since the directory is initially empty).
5. Update `retrospectives/inbox/README.md` to describe the sibling directories and their purpose.
6. Update `retrospectives/inbox/template.md` to document post-triage relocation (promoted/deferred/rejected notes are moved to the matching sibling directory).
7. Rewrite `scripts/check-adaptive-agents.sh` — `check_retrospectives()` and `check_retrospective_private_patterns()` — to scan all sibling directories, not just `inbox/`. Add a status-directory invariant: a note's status must match its parent directory (e.g., `promoted/` notes must be `Promoted`, `inbox/` notes must not be `Promoted` or `Rejected`).
8. Update the Project Layer template's checker (`templates/project-layer/.adaptive-agents/scripts/check-project-layer.sh`) with the same sibling-directory coverage.
9. Create sibling directories in the Project Layer template (`templates/project-layer/.adaptive-agents/retrospectives/promoted/`, `deferred/`, `rejected/`) with appropriate INDEX.md files, and update the template's `retrospectives/INDEX.md` to list them.
10. Create `scripts/migrate-project-layer-retrospectives.sh` — an upgrade script that existing Project Layers can run to convert their retrospective directory from the old flat-inbox layout to the new sibling-directory layout. The script shall:
    - Scan `retrospectives/inbox/` for notes whose status is not `Captured`
    - Create sibling directories if missing
    - Move each non-Captured note to the matching sibling directory
    - Create `retrospectives/INDEX.md` with routing table if missing or outdated
    - Create `retrospectives/rejected/INDEX.md` if missing
    - Be safe to re-run (idempotent)
    - Report what was moved and what was created

### Not Included (Deliberately Out of Scope)

- **No changes to the live Project Layer (`.adaptive-agents/`).** The live Project Layer is migrated by running the upgrade script, not by manual edits in this work unit.
- **No changes to prompt files.** The 7 prompts that reference `retrospectives/inbox/` work correctly — inbox still means "notes awaiting triage" and "capture new notes here." The sibling directories are referenced by the checker and INDEX.md, not by capture/triage prompts.
- **No changes to the adaptation cycle playbook.** The four-status model, promotion workflow, and learning flow are identical; only file locations change.
- **No retrospective schema files.** The format is validated procedurally by the checker, not by schema.
- **No changes to the promotion patch format.** Moves use `git mv` before patch application; patches reference the new path with `*** Update File:`. No new operation needed.
- **No bulk link rewriting.** All sibling directories are at the same depth as `inbox/` (two levels below repo root), so existing relative promotion links like `../../instructions/...` work unchanged.

### Design Decisions

| Decision | Outcome |
|---|---|
| File relocation | `git mv` for rename tracking; then patch updates status/promotion-links at the new path. No patch-format change. |
| Deferred notes | Move to `deferred/`. "Deferred" is an explicit user decision to revisit later, not an untriaged item. Inbox = needs initial triage only. |
| `rejected/` directory | Create with INDEX.md + guidance, even though currently empty. Signals intended layout and satisfies "do not delete rejected notes" from day one. |
| `retrospectives/INDEX.md` | Create as routing map, consistent with `planning/INDEX.md`. |
| Relative links on move | All siblings at same depth — no link rewriting needed. Adjacent sibling directories produce identical relative paths. |

### Acceptance Criteria

| # | Criterion | Verification |
|---|---|---|
| AC1 | All 14 Promoted notes reside in `retrospectives/promoted/` with status unchanged. | File listing + grep for status |
| AC2 | The single Deferred note resides in `retrospectives/deferred/` with status unchanged. | File listing + grep for status |
| AC3 | `retrospectives/inbox/` contains only Captured notes (9 files) plus README.md and template.md. | File listing + grep for status |
| AC4 | `retrospectives/rejected/` exists with INDEX.md and no notes. | File listing |
| AC5 | `retrospectives/INDEX.md` exists and lists all four sibling directories with note counts. | File existence + content check |
| AC6 | Promoted notes' relative promotion links resolve correctly after move (all siblings at same depth — no change needed). | `git diff --check` + path depth inspection |
| AC7 | `check_retrospectives()` validates all sibling directories, not just inbox. | `check-adaptive-agents.sh` passes |
| AC8 | Status-directory invariant enforced: promoted/ notes must be Promoted; inbox/ notes must be Captured (not Promoted or Rejected); deferred/ notes must be Deferred. | Checker failure on misclassified note |
| AC9 | `check_retrospective_private_patterns()` scans all sibling directories. | Checker covers all paths |
| AC10 | Project Layer template checker has the same sibling-directory coverage. | `test-project-layer.sh` passes |
| AC11 | Inbox README and template describe sibling directories. | File content review |
| AC12 | `bash scripts/check-adaptive-agents.sh` passes with 0 failures. | Full health check run |
| AC13 | `bash scripts/test-project-layer.sh` passes. | Project Layer test run |
| AC14 | All 7 capture/triage/review prompts continue to work without modification (they reference `inbox/` paths only, which still exist). | Static link check + grep for broken `promoted/`/`deferred/`/`rejected/` references in prompts |
| AC15 | Project Layer template has `promoted/`, `deferred/`, `rejected/` directories with INDEX.md files. | File listing for `templates/project-layer/.adaptive-agents/retrospectives/` |
| AC16 | Upgrade script exists at `scripts/migrate-project-layer-retrospectives.sh`. | File existence |
| AC17 | Upgrade script is idempotent (safe to re-run). | Run twice on the same fixture; verify identical output |
| AC18 | Upgrade script migrates a note with status `Promoted` from `inbox/` to `promoted/`. | Fixture with one Promoted note in inbox; script moves it |
| AC19 | Upgrade script creates `retrospectives/INDEX.md` with routing table when missing. | Fixture without INDEX.md; script creates it |

## Dependencies

None. This is a self-contained structural change with no external dependencies. The work unit is independent of other backlog items.
