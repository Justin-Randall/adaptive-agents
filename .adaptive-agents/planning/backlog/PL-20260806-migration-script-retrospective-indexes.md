# PL-20260806: Migration Script Missing Promoted/Deferred Retrospective INDEX Files

- Status: Backlog
- Readiness: Needs refinement
- Created: 2026-08-06
- Test approach: run the migration script against a fixture layer in a temp dir and verify `promoted/INDEX.md`, `deferred/INDEX.md`, and `rejected/INDEX.md` all exist with valid status mappings, are content-idempotent on re-run, and that a subsequent `inspect-project-layer-upgrade.sh` reports no missing retrospective INDEX paths

## Objective

Fix `scripts/migrate-project-layer-retrospectives.sh` so migrating a Project Layer to the sibling-directory retrospective layout creates all three status sibling INDEX files — `promoted/INDEX.md`, `deferred/INDEX.md`, and `rejected/INDEX.md` — matching the canonical template, so an upgrade no longer reports those paths as missing after migration.

## Problem Spec

The canonical Project Layer template ships `retrospectives/promoted/INDEX.md`, `retrospectives/deferred/INDEX.md`, and `retrospectives/rejected/INDEX.md`. The migration script creates the `promoted/`, `deferred/`, and `rejected/` directories and writes `rejected/INDEX.md` plus the routing `retrospectives/INDEX.md` (only if missing), but never writes `promoted/INDEX.md` or `deferred/INDEX.md`. Reproduced while upgrading a Project Layer from template `0.4.0` to `0.5.4`: after running the migration, `scripts/inspect-project-layer-upgrade.sh` still reported `retrospectives/promoted/INDEX.md` and `retrospectives/deferred/INDEX.md` as missing canonical paths, requiring manual file creation. The Upgrade Project Layer skill documents the script as handling "the full conversion including INDEX.md creation," which overstates what the script actually produces.

## Scope

1. Make the migration script create `promoted/INDEX.md` and `deferred/INDEX.md` when the sibling directories are created, with content matching the canonical template.
2. Keep the existing `rejected/INDEX.md` and routing `retrospectives/INDEX.md` behavior: content-idempotent, never overwriting existing user-authored files.
3. Reconcile the Upgrade Project Layer skill's "full conversion including INDEX.md creation" claim with the corrected script behavior.
4. Add a focused automated test using a fixture layer in a temp directory: migrate layers containing `Captured`, `Promoted`, `Deferred`, and `Rejected` notes; assert all sibling INDEX files exist, statuses map to the correct directories, and re-runs are content-stable.

## Out of Scope

- Changing the canonical template's sibling INDEX file contents.
- The installer cwd/root-detection failure captured in the system-wide retrospectives inbox (2026-08-06) — tracked separately.
