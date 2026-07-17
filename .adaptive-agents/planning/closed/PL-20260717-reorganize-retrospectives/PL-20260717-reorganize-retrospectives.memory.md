# PL-20260717-reorganize-retrospectives — Working Memory

- Work Unit: PL-20260717-reorganize-retrospectives
- Activated: 2026-07-17
- Status: Completed

## Trigger

The inbox contained a mix of all statuses (14 Promoted, 9 Captured, 1 Deferred, 0 Rejected), making it impossible to tell at a glance how many items still needed triage.

## Verified Platform Evidence

| Evidence | Finding |
| --- | --- |
| `git mv` rename tracking | All 14 moved notes detected as renames (100% similarity). |
| Health check | 176 passed, 0 failures on first validation after structural changes. |
| Project Layer tests | 14 passed, 0 failures after updating path expectations. |
| INDEX.md reachability | All sibling INDEX.md files linked from `retrospectives/INDEX.md` and template. |
| Status-directory invariant | Checker flags notes in wrong directories. |

## Sources

- Existing `retrospectives/inbox/` files and status metadata.
- Existing `scripts/check-adaptive-agents.sh` and Project Layer template checker.

## Decisions

| Date | Decision | Rationale |
| --- | --- | --- |
| 2026-07-17 | Four sibling directories, one per status | Clean 1:1 mapping; inbox = needs triage only. |
| 2026-07-17 | Deferred notes to `deferred/` | Deferred is an explicit triage decision, not an untriaged item. |
| 2026-07-17 | `git mv` for moves | Preserves rename history. |
| 2026-07-17 | Standalone migration script | Keeps conversion independent from template recopy. |
| 2026-07-17 | Wire into upgrade skill | Agents discover script during upgrade workflow. |

## Constraints

- Do not change prompt files — they reference `inbox/` which still exists.
- Do not change adaptation cycle — four-status model is unchanged.
- Do not bulk-rewrite links — all siblings at same depth.
- Migration script must be idempotent.

## Closure

Completed and approved on 2026-07-17. All 16 acceptance criteria satisfied.
