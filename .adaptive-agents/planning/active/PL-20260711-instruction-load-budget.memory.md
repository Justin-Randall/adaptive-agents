# PL-20260711-instruction-load-budget Memory

Curated cross-session context for the Instruction Load Budget work unit.

## Current State

- The checker, shell wrapper, route manifest, schemas, baseline, focused tests, CI workflow, repository-health integration, routing, and README commands are implemented.
- All 27 focused tests pass locally on Windows.
- The current reviewed profiles are below the warning threshold; measured utilization ranges from 6.1% to 28.6%.
- User-observed `--report` and `--check` dogfood remains before closure.
- The detailed backlog specification remains the normative contract linked from `ACTIVE.md`.
- There is no model-specific tokenizer requirement; the estimate is a stable repository bloat heuristic.

## Decisions

- Count only files that imperative routing makes mandatory for a named profile.
- Use `max(ceil(words * 1.5), ceil(characters / 4))` with integer arithmetic.
- Warn at 26,215 estimated tokens and fail above 32,768 for static startup.
- Normalize line endings before metrics and hashing.
- Keep the route manifest authored and the baseline generated.
- Require Python 3.11+ standard library only.
- Use `bash scripts/check-instruction-load-budget.sh` as the canonical human, health-check, and CI entrypoint; keep Python as the implementation and direct troubleshooting interface.
- Make the shell wrapper resolve the adjacent Python script, forward arguments and streams unchanged, and preserve the Python exit code.
- Make no-argument invocation the concise static startup status: `AGENTS.md` plus `INDEX.md` estimated tokens versus 32,768, used and remaining estimated tokens, and startup PASS/FAIL.
- Baseline generation and `--check` measure only the `startup` profile. Active plans and task-conditional Markdown remain optional diagnostics under `--report` and cannot stale or fail the startup gate.
- Require user dogfooding of `--report` and `--check` before closure.

## Immediate Next Step

- Regenerate the baseline after this counted memory update, run full repository validation, then have the user dogfood `--report` and `--check`.

## Dogfood Evidence Required

- User runs `bash scripts/check-instruction-load-budget.sh --report` and reviews profile membership, totals, utilization, and deltas.
- User runs `bash scripts/check-instruction-load-budget.sh --check` and confirms it is understandable, read-only, and successful for the accepted baseline.

## Blockers

- GitHub Actions platform execution cannot be observed until the workflow runs on a pushed branch or pull request.

## Deferred Discoveries

- None proposed.
