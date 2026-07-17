# PL-20260717: Reorganize retrospectives directory structure

- Status: Completed
- Work Unit: PL-20260717-reorganize-retrospectives
- Origin: Backlog ([PL-20260717-reorganize-retrospectives.backlog.md](PL-20260717-reorganize-retrospectives.backlog.md))
- Activated: 2026-07-17
- Memory: [PL-20260717-reorganize-retrospectives.memory.md](PL-20260717-reorganize-retrospectives.memory.md)

## Objective

Reorganize the `retrospectives/` directory so the `inbox/` folder contains only notes awaiting initial triage (status `Captured`). Promoted, deferred, and rejected retrospectives live in sibling directories so a glance at the directory tree reveals how many items remain open.

## Specifications

### Problem Spec

The current `retrospectives/inbox/` contained a mix of all statuses — 14 `Promoted`, 9 `Captured`, 1 `Deferred`, 0 `Rejected` (as of 2026-07-17). A quick glance at the directory did not distinguish between "items that still need triage" and "items that have already been resolved." This made prioritization, review, and inbox shipping harder than necessary.

Queue-separation principle established:
- **`inbox/`** = needs initial triage only (`Captured` status)
- **`deferred/`** = triaged, set aside for later re-evaluation (`Deferred` status — an explicit user decision to revisit)
- **`promoted/`** = lesson has been applied to durable guidance (`Promoted` status)
- **`rejected/`** = considered and declined (`Rejected` status, retained per "do not delete" principle)

### Feature Spec

#### 1. Directory layout

Create four sibling directories under `retrospectives/` with INDEX.md routing. Move existing notes to the directory matching their declared status. The inbox retains only Captured notes plus README.md and template.md.

#### 2. Checker coverage

Both `scripts/check-adaptive-agents.sh` and the Project Layer template checker scan all four sibling directories. A status-directory invariant enforces that a note's `Status` metadata matches its parent directory (e.g., `promoted/` notes must be `Promoted`).

#### 3. Migration path for existing Project Layers

A standalone upgrade script (`scripts/migrate-project-layer-retrospectives.sh`) converts existing flat-inbox Project Layers to the sibling-directory layout. It is idempotent and wired into the Project Layer upgrade skill's Propose and Apply steps.

#### 4. Template alignment

The Project Layer template (`templates/project-layer/.adaptive-agents/retrospectives/`) includes the same four sibling directories with INDEX.md files, ensuring newly bootstrapped layers start with the correct layout.

### Behavioral Spec

| Case | Expected behavior |
| --- | --- |
| Existing Promoted note in inbox | Moved to `promoted/`; status unchanged; promotion links unchanged (same depth). |
| Existing Deferred note in inbox | Moved to `deferred/`; "Deferred" means explicitly triaged and set aside, not awaiting triage. |
| Existing Captured note in inbox | Stays in `inbox/` — still needs triage. |
| Empty Rejected directory | Created with INDEX.md and guidance, even though empty. |
| Checker encounters note in wrong directory | Fails with status-directory invariant violation. |
| Existing Project Layer with old layout | Migration script moves non-Captured notes; INDEX.md created if missing; idempotent on rerun. |
| Capture/triage/review prompts | Unchanged — they reference `inbox/` which still means "notes awaiting triage." |

## Applicable Guidance

- `instructions/coding.instructions.md` — small, reversible changes; preserve existing style; verify against source code and test output.
- `instructions/tdd.instructions.md` — update test expectations before production behavior changes.

## Scope

1. Create four sibling directories: `retrospectives/inbox/`, `promoted/`, `deferred/`, `rejected/`.
2. Move 13 Promoted notes and 1 Deferred note to matching directories via `git mv`.
3. Create `retrospectives/INDEX.md` as routing map.
4. Create `retrospectives/rejected/INDEX.md` with guidance.
5. Update `retrospectives/inbox/README.md` to describe sibling directories.
6. Update `retrospectives/inbox/template.md` to document post-triage relocation.
7. Rewrite both checkers to scan all sibling directories and enforce status-directory invariant.
8. Update Project Layer template with sibling directories and INDEX.md files.
9. Create `scripts/migrate-project-layer-retrospectives.sh` with idempotent conversion.
10. Wire migration script into `skills/upgrade-project-layer/SKILL.md` Propose and Apply steps.
11. Fix cross-reference in `playbooks/adaptive-automation-roadmap.md` to point to `promoted/`.

## Out of Scope

- Modifying prompt files (they reference `inbox/` which still exists).
- Changing the adaptation cycle playbook.
- Retrospective schema files.
- Promotion patch format changes.
- Bulk link rewriting (all siblings at same depth).
- Manual migration of the live Project Layer (done via upgrade script).

## Acceptance Criteria

| # | Criterion | Verification |
| --- | --- | --- |
| AC1 | All 14 Promoted notes reside in `retrospectives/promoted/` with status unchanged. | File listing + grep for status |
| AC2 | The single Deferred note resides in `retrospectives/deferred/` with status unchanged. | File listing + grep for status |
| AC3 | `retrospectives/inbox/` contains only Captured notes (9 files) plus README.md and template.md. | File listing + grep for status |
| AC4 | `retrospectives/rejected/` exists with INDEX.md and no notes. | File listing |
| AC5 | `retrospectives/INDEX.md` exists and lists all four sibling directories with note counts. | File existence + content check |
| AC6 | Promoted notes' relative promotion links resolve correctly after move (same depth). | `git diff --check` + path depth inspection |
| AC7 | Checkers validate all sibling directories, not just inbox. | `check-adaptive-agents.sh` passes |
| AC8 | Status-directory invariant enforced. | Checker failure on misclassified note |
| AC9 | Project Layer template checker has sibling-directory coverage. | `test-project-layer.sh` passes |
| AC10 | Inbox README and template describe sibling directories. | File content review |
| AC11 | `bash scripts/check-adaptive-agents.sh` passes with 0 failures. | Full health check run |
| AC12 | `bash scripts/test-project-layer.sh` passes. | Project Layer test run |
| AC13 | All 7 capture/triage/review prompts work without modification. | Static link check |
| AC14 | Project Layer template has `promoted/`, `deferred/`, `rejected/` directories with INDEX.md. | File listing |
| AC15 | Upgrade script exists, idempotent, migrates Promoted note, creates INDEX.md when missing. | Test fixture verification |
| AC16 | Upgrade skill references migration script in Propose and Apply steps. | Skill content review |

## Decisions

| Date | Decision | Rationale |
| --- | --- | --- |
| 2026-07-17 | Four sibling directories mapping 1:1 to statuses | Cleanest separation; inbox means only "needs triage." |
| 2026-07-17 | Deferred notes go to `deferred/` | "Deferred" is an explicit user decision to revisit later, not an untriaged item. |
| 2026-07-17 | `rejected/` INDEX.md created even when empty | Signals intended layout from day one; satisfies "do not delete" principle. |
| 2026-07-17 | `git mv` for file movement | Preserves rename history; no patch-format change needed. |
| 2026-07-17 | No prompt file changes needed | All prompts reference `inbox/` which still means "notes awaiting triage." |
| 2026-07-17 | Standalone migration script, wired into upgrade skill | Keeps conversion independent from template copy; agents discover it during upgrades. |
| 2026-07-17 | `--target` flag on migration script | Consistent with `inspect-project-layer-upgrade.sh` convention. |

## Verification

Implementation verification:

- `git mv` of 13 Promoted notes to `retrospectives/promoted/` — 100% rename tracking.
- `git mv` of 1 Deferred note to `retrospectives/deferred/` — 100% rename tracking.
- `bash scripts/check-adaptive-agents.sh`: 176 passed, 0 failures (1 pre-existing Antigravity warning).
- `bash scripts/test-project-layer.sh`: 14 passed, 0 failures.
- `git diff --check`: clean.
- Checker validates status-directory invariant for all four sibling directories.
- Project Layer template checker updated with same invariant.
- Migration script created, accepts `--target`, idempotent, creates INDEX.md when missing.
- Upgrade skill updated to reference migration script in Propose and Apply steps.
- Index files created: `retrospectives/INDEX.md`, `promoted/INDEX.md`, `deferred/INDEX.md`, `rejected/INDEX.md`.
- Template sibling directories created with INDEX.md files.
- `playbooks/adaptive-automation-roadmap.md` stale link fixed.
- All acceptance criteria satisfied. User approved closure on 2026-07-17.
