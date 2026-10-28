# PL-20261027-total-recall-codex-installer-hardening Memory

Curate this file for cross-session handoff. Replace stale details rather than keeping an append-only journal.

## Current State

- Active on branch `pl-20261027-total-recall-codex-installer-hardening`.
- Activated from the Total Recall installer-hardening backlog child with user approval.
- The prerequisite installer child is completed; its verified Windows behavior and known limitations are recorded in the [closed installer packet](../closed/PL-20261027-total-recall-codex-installer/PL-20261027-total-recall-codex-installer.sdd.md).
- Existing Project Layer planning-link validation failures were repaired; the Project Layer checker now passes with 0 failures.
- No installer implementation, installer run, or dogfood has been performed for this active work yet.

## User-Reported Reproduction

- Running `scripts/install-codex.sh` after a prior installation reports that the Codex permission grant is already present, then exits because user `config.toml` defines inline hooks and the installer refuses to create or update `hooks.json` while that representation conflict exists.
- The relevant guard is in `scripts/codex_hooks_config.py`; the exact user-level hook configuration must be preserved while verifying Codex's supported behavior.
- The active plan requires invoking `scripts/install-codex.sh` directly in isolated temporary-home tests and during approved desktop dogfood. Passing helper-only tests is not enough.

## Constraints and Handoff

- Preserve unrelated Codex configuration, user-authored inline hooks, approval behavior, and user session records.
- Automated tests must use temporary Codex homes and must never mutate real user configuration.
- Real dogfood must use ChatGPT Codex desktop from an unrelated project; Copilot and CLI-only runs are not desktop evidence.
- Treat hook trust review as a separate user action. Installer file presence or `--check` must not be presented as proof of effective hook trust.
- Native Windows is the currently verified installer profile. macOS, Linux, and WSL behavior remain to be tested or explicitly recorded as unavailable.
- Determine the safe inline-hook coexistence or migration behavior from supported Codex semantics before implementing a change; do not silently delete or rewrite user hooks.

## Completion Review

Complete this section before closure.

- Final diff and relevant outputs reviewed for correctness, regressions, and unintended scope: Pending
- Acceptance criteria verified and remaining gaps identified: Pending
- Engineering quality assessed for clarity, maintainability, discoverability, necessary scope, and semantic duplication: Pending
- Findings fixed or dispositioned, with rationale for unresolved or deferred items: Pending

## Decisions

- None beyond the constraints recorded in the active plan.

## Blockers

- The supported resolution for inline `config.toml` hooks coexisting with installer-managed `hooks.json` needs source verification before implementation is selected.

## Deferred Discoveries

- None proposed.
