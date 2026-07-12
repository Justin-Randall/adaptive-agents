# PL-20260711-instruction-load-budget Memory

Curated closure snapshot for the Instruction Load Budget work unit.

## Status

Completed 2026-07-12. Verified by user dogfood of `--report` and `--check`.

## Decisions

- Count only files that imperative routing makes mandatory for a named profile.
- Use `max(ceil(words * 1.5), ceil(characters / 4))` with integer arithmetic.
- Warn at 26,215 estimated tokens and fail above 32,768 for static startup.
- Normalize line endings before metrics and hashing.
- Keep the route manifest authored and the baseline generated.
- Require Python 3.11+ standard library only.
- Use `bash scripts/check-instruction-load-budget.sh` as the canonical human, health-check, and CI entrypoint; keep Python as the implementation and direct troubleshooting interface.
- Make the shell wrapper resolve the adjacent Python script, forward arguments and streams unchanged, and preserve the Python exit code.
- Make no-argument invocation the concise static startup status.
- Baseline generation and `--check` measure only the `startup` profile.

## Verified Behavior

- 31 focused tests pass on Windows, including proof that oversized active Markdown does not affect baseline or gate results.
- Repository health (`check-adaptive-agents.sh --verbose`) passes 141 checks with zero failures; nested test totals and startup utilization emitted.
- Project layer (`check-project-layer.sh`) passes with zero failures.
- Cross-platform CI (`static-validation` workflow) confirmed passing by user after commit `0a44ce3`.
- All CLI modes verified: default status, `--report`, `--check`, `--update-baseline`.
- Startup gate passes at 4,111 estimated tokens (12.5% of 32,768 high-water mark).
- Editor diagnostics and `git diff --check` clean.

## Unresolved Problems

- GitHub Actions platform execution cannot be observed until the workflow runs on a pushed branch or pull request; user confirmed the first cross-platform run passed.

## Rejected Approaches

- Model-specific tokenizer (too precise, creates cross-model inconsistency).
- Third-party JSON Schema validators (unnecessary dependency for ~50-line documents).
- Automatic baseline rewriting during checks (would hide instruction growth).

## Constraints

- Strict UTF-8 with CRLF normalization to avoid Git checkout differences on Windows.
- Python 3.11+ standard library only — no pip packages for counting text or validating small JSON.
- CLI exit codes must be 0/1/2 only to integrate cleanly with CI and repository health.

## Restart Context

If reopened: regenerate baseline after manifest or counted-file changes with `--update-baseline`, run `python scripts/test-instruction-load-budget.py`, run `scripts/check-instruction-load-budget.sh --check`, and verify `check-adaptive-agents.sh --verbose` passes before committing.
