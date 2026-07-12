# PL-20260711: Instruction Load Budget

- Status: Completed
- Work Unit: PL-20260711-instruction-load-budget
- Origin: Backlog ([PL-20260711-instruction-load-budget.backlog.md](PL-20260711-instruction-load-budget.backlog.md))
- Activated: 2026-07-11
- Closed: 2026-07-12

## Objective

Implement a deterministic inventory and CI gate for the static files required to initialize Adaptive Agents through the canonical `AGENTS.md` route. Report the startup source size and rough token cost, warn at 80% utilization, and reject startup cost above the 32,768 estimated-token high-water mark. Active planning and task-conditional guidance are diagnostic only and do not affect the gate.

## Specifications

The approved [backlog specification](PL-20260711-instruction-load-budget.backlog.md) is the detailed contract for deliverables, route semantics, data shapes, algorithms, CLI behavior, CI topology, tests, guardrails, and boundary conditions. Do not silently change that contract during implementation; record any evidence-driven adjustment in `## Decisions` and update the active specification before applying it.

### Problem Spec

Adaptive Agents does not measure the transitive context cost of files its routing tells models they must read. A deterministic, model-neutral estimate is needed to detect instruction bloat and enforce a 32 Ki-token compaction safeguard without treating optional links or the entire repository as mandatory context.

### Feature Specs

1. Maintain a reviewed route manifest with named required-read profiles and explicit reasons for every counted path.
2. Normalize strict UTF-8 source text and calculate deterministic byte, character, word, hash, and rough token metrics.
3. Generate a stable machine-readable startup baseline with ordered files, metrics, totals, formulas, and limits.
4. Provide startup-focused default, read-only `--check`, and explicit `--update-baseline` modes, plus an all-profile diagnostic `--report`.
5. Warn at 26,215 startup estimated tokens and fail above 32,768 startup estimated tokens.
6. Run isolated tests and the non-mutating gate on Ubuntu and Windows, exposing one stable branch-protection status.
7. Integrate the read-only check into repository health and document local commands and external branch-protection setup.

### Interface And Contract Specs

Required implementation artifacts:

- `instruction-load-routes.json`
- `instruction-load-baseline.json`
- `schemas/instruction-load-routes.schema.json`
- `schemas/instruction-load-baseline.schema.json`
- `scripts/check-instruction-load-budget.sh`
- `scripts/check-instruction-load-budget.py`
- `scripts/test-instruction-load-budget.py`
- `.github/workflows/static-validation.yml`

CLI contract:

```text
bash scripts/check-instruction-load-budget.sh
bash scripts/check-instruction-load-budget.sh --report
bash scripts/check-instruction-load-budget.sh --check
bash scripts/check-instruction-load-budget.sh --update-baseline
```

- The shell script is the canonical human, repository-health, and CI entrypoint.
- With no arguments, print the static `startup` profile's counted-file total, used and remaining estimated tokens, utilization, and PASS/FAIL result.
- Default status, `--check`, and `--update-baseline` select only the `startup` profile. They do not read, hash, baseline, or enforce active planning and task-conditional Markdown.
- `--report` expands all reviewed profiles for diagnostics but does not define or enforce the static startup gate.
- Default status validates current startup routes and source metrics but does not compare baseline drift; `--check` remains the strict startup CI and repository-health gate.
- The shell script uses `#!/usr/bin/env bash`, `set -euo pipefail`, resolves the adjacent Python script from `BASH_SOURCE`, and forwards all arguments unchanged.
- The shell script invokes an available Python 3 interpreter, preserves stdout and stderr, and returns the Python process exit code. If no Python 3 interpreter is available, it emits one actionable error and exits nonzero.
- The Python script remains directly executable for focused tests and native Windows troubleshooting.
- Exit `0`: success, including warning-only utilization.
- Exit `1`: validation, route, drift, stale-baseline, or budget failure.
- Exit `2`: missing, incompatible, or unknown arguments.
- `--report` and `--check` write nothing.
- `--update-baseline` atomically replaces only the baseline and never runs in CI.

### Data And Metric Specs

- Canonical Markdown remains authoritative; the manifest is an audited measurement model and contains no instruction text.
- Paths are explicit repository-relative POSIX paths with no globs, backslashes, URI schemes, drive prefixes, or traversal.
- Profiles inherit ordered paths, reject cycles, and deduplicate within each profile while preserving first-seen order.
- If `ACTIVE.md` has no active plan, active memory is omitted. Otherwise, the manifest names the exact active work-unit memory path.
- Normalize CRLF and lone CR to LF before all metrics.
- Count words with `len(normalized_text.split())`.
- Hash normalized UTF-8 bytes with SHA-256.
- Calculate profile estimates with integer arithmetic:

```text
word_estimate = (total_words * 3 + 1) // 2
character_estimate = (total_characters + 3) // 4
estimated_tokens = max(word_estimate, character_estimate)
```

- JSON output uses two-space indentation, deterministic ordering, and exactly one trailing LF.
- Python 3.11 or newer and standard-library APIs only.

### Behavioral Specs

- Optional references, historical artifacts, and unrelated Markdown never count merely because they are linked or reachable.
- Any counted-file hash change makes the committed baseline stale, including same-size edits.
- Exactly 32,768 estimated tokens passes; 32,769 fails.
- Exactly 26,215 estimated tokens warns without failing.
- Profile-specific limits may be stricter than the global limit but never looser.
- Warning-only results return success.
- The checker reports all safely discoverable failures in stable profile and file order.
- No mode mutates the manifest; only `--update-baseline` may mutate the baseline.

## Applicable Guidance

- `.adaptive-agents/ARCHITECTURE.md` — preserve canonical routing, Project Layer ownership, and deterministic validation boundaries.
- `instructions/global.instructions.md` — load routed engineering guidance and run the completion retrospective checkpoint.
- `instructions/repository-boundaries.instructions.md` — keep this repository's canonical and Project Layer ownership distinct.
- `instructions/coding.instructions.md` — use testable seams, source-backed claims, and focused reversible changes.
- `instructions/tdd.instructions.md` — begin behavior changes with focused failing tests and validate each slice.
- `instructions/command-failure-pivot.instructions.md` — classify command failures and pivot rather than retrying equivalent guesses.
- `instructions/temp-artifact-hygiene.instructions.md` — keep generated test artifacts isolated and cleaned up.
- `.adaptive-agents/skills/manage-planning/SKILL.md` — maintain active progress, decisions, verification, and work-unit memory.

## Scope

- Verify the candidate required-read inventory against current imperative routing language.
- Add the reviewed manifest, generated baseline, schemas, Python CLI, and isolated tests.
- Add Ubuntu and Windows CI coverage with one final required-status job.
- Integrate the read-only gate into repository health.
- Document report, check, baseline-update, dogfood, and branch-protection steps.

## Out Of Scope

- Model-specific tokenizer accounting or network services.
- Tool-added system prompts outside this repository.
- Third-party runtime packages.
- Automatic baseline rewriting during checks or CI.
- Local Git hooks or automated branch-protection configuration.
- Counting every linked or reachable Markdown file.

## Acceptance Criteria

- [x] Every counted file traces to mandatory routing language and a profile trigger.
- [x] Optional links and unrelated Markdown are excluded.
- [x] Manifest and baseline satisfy their schemas and built-in structural validation.
- [x] LF and CRLF content produce identical metrics and hashes.
- [x] Baseline generation is byte-stable on Windows and Linux.
- [x] `--check` is read-only and rejects invalid startup routes, stale startup baselines, unsafe paths, and startup cost above 32,768 estimated tokens.
- [x] Warning utilization starts at 26,215 without failing.
- [x] Exactly 32,768 passes and 32,769 fails.
- [x] Focused tests cover all twenty scenarios in the backlog specification without touching real user configuration.
- [x] Repository health invokes the read-only budget check.
- [x] CI runs repository static validation, including the shell-wrapped startup budget check and its regression tests, on Ubuntu and Windows and exposes one stable `static-validation` status.
- [x] README documents shell-wrapper commands for report, check, baseline update, dogfood observation, and branch protection; direct Python usage is secondary troubleshooting guidance.
- [x] No model-specific tokenizer or third-party runtime package is required.
- [x] The shell wrapper forwards arguments, output streams, and exit codes without changing checker behavior.
- [x] No-argument invocation reports static startup estimated tokens versus the 32,768 high-water mark and exits from that startup PASS/FAIL status.
- [x] Active planning and task-conditional Markdown are absent from the committed baseline and cannot fail the startup gate.
- [x] Dogfood instructions give the user copy-paste commands and explain what successful and warning output looks like.
- [x] The user runs default status and `--check`, observes the static startup total and utilization, and confirms the output is understandable before closure.

## Dogfood Procedure

After implementation and automated validation, give the user these commands from the repository root:

```bash
./scripts/check-instruction-load-budget.sh
bash scripts/check-instruction-load-budget.sh --report
bash scripts/check-instruction-load-budget.sh --check
```

Explain that default status should show static startup estimated tokens versus the 32,768 high-water mark and a startup PASS/FAIL result. Explain that `--report` should show diagnostic profile composition without defining the gate. Explain that `--check` should produce no file changes, exit `0`, warn only when startup reaches 80%, and fail with an actionable startup file/metric delta if the manifest, baseline, path contract, or hard limit is violated.

Ask the user to confirm that profile membership and totals match their understanding of what models must read. Do not close the work until this dogfood confirmation is recorded or the user explicitly waives it.

## Progress

- [x] Verify the candidate route inventory against current imperative wording.
- [x] Add focused failing tests for normalization, profile expansion, and limit boundaries.
- [x] Add schemas and the reviewed route manifest.
- [x] Implement metrics, validation, reporting, and deterministic serialization.
- [x] Implement baseline update and read-only check behavior.
- [x] Generate and review the initial baseline.
- [x] Add CI and repository-health integration.
- [x] Dogfood the documented README commands with the user.

## Decisions

- Use a rough model-neutral token heuristic, not a model-specific tokenizer.
- Apply a hard high-water mark of 32,768 estimated tokens to static startup cost.
- Warn at 26,215 estimated tokens (80%, rounded upward).
- Keep canonical Markdown authoritative; the manifest is measurement configuration only.
- Require explicit baseline updates so instruction growth and route changes remain reviewable.
- Use a thin Bash wrapper as the canonical public entrypoint while retaining Python for deterministic cross-platform logic.
- Require user-observed `--report` and `--check` output before closure.

## Verification

- `python scripts/test-instruction-load-budget.py` — 31 tests passed on Windows, including proof that oversized active Markdown does not affect baseline or gate results.
- `./scripts/check-instruction-load-budget.sh` — startup passed at 4,111 estimated tokens out of 32,768 (12.5%).
- `instruction-load-baseline.json` — contains only the `startup` profile and its two static files, `AGENTS.md` and `INDEX.md`.
- `bash scripts/check-instruction-load-budget.sh --update-baseline` — generated the initial deterministic baseline.
- `bash scripts/check-instruction-load-budget.sh --check` — passed against the generated baseline.
- `bash scripts/check-adaptive-agents.sh --verbose` — 141 checks passed with zero failures and zero warnings; successful nested test totals and startup utilization are emitted as CI evidence.
- `bash .adaptive-agents/scripts/check-project-layer.sh` — zero failures.
- Editor diagnostics and `git diff --check` — no errors; Windows line-ending notices only.
- The user confirmed the first cross-platform `static-validation` GitHub Actions run passed after commit `0a44ce3`; detailed pass evidence was insufficient, so verbose CI evidence was added in the follow-up.
- User-observed CLI dogfood confirmed working 2026-07-12.

## Supporting Documents

- [Backlog specification](PL-20260711-instruction-load-budget.backlog.md) — approved detailed implementation contract.
- [PL-20260711-instruction-load-budget memory](PL-20260711-instruction-load-budget.memory.md) — cross-session decisions and handoff state.
