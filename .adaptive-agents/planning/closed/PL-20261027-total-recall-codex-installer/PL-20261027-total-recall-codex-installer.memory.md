# PL-20261027-total-recall-codex-installer — Working Memory

## Handoff

- The Codex Total Recall foundation is closed and supplies `scripts/codex_total_recall.py`, `scripts/codex_hooks_config.py`, focused tests, deterministic graph validation, and real CLI lifecycle evidence.
- The installer child now owns global runtime provisioning, hook/configuration migration, exact Codex-home/session permissions, upgrade safety, health checks, and installer-enabled compaction dogfood.
- Foundation evidence and constraints are preserved in [the closed foundation memory](../PL-20261027-total-recall-codex-foundation/PL-20261027-total-recall-codex-foundation.memory.md).

## Initial Constraints

- Do not place a virtual environment, machine-specific dependencies, or generated runtime artifacts under tracked repository content.
- Preserve unrelated user-authored Codex configuration and approval behavior; fail closed on unknown existing hook ownership.
- Do not mutate user-generated session records during ordinary install or upgrade.
- The foundation dogfood environment could not write Codex's state database, so permission-sensitive desktop validation remains open for this installer child.

## Official Codex Research Findings

- Codex records trust against the current hook definition hash and skips changed/untrusted non-managed hooks until review; installation must surface trust state and cannot infer activation from `hooks.json` presence alone. Source: [official Codex Hooks documentation](https://learn.chatgpt.com/docs/hooks#review-and-trust-hooks).
- Hooks can load from user or project `hooks.json` and inline `config.toml`; project layers require trust, and defining both representations in one layer produces a warning. Migration must detect duplicate/conflicting representations and preserve unrelated entries. Source: [advanced configuration](https://learn.chatgpt.com/docs/config-file/config-advanced#hooks).
- Permission profiles are supported on native Windows, macOS, Linux, and WSL, but do not compose with legacy `sandbox_mode`/`sandbox_workspace_write`; migration needs an explicit compatibility matrix and must avoid mixed configuration. Source: [permissions documentation](https://learn.chatgpt.com/docs/permissions).
- Windows desktop uses the native Windows agent by default and shares the native `%USERPROFILE%\\.codex` home, while WSL uses a separate Linux Codex home unless explicitly redirected. Desktop, native CLI, and WSL are separate dogfood profiles. Source: [Windows desktop documentation](https://learn.chatgpt.com/docs/app/windows).
- `UserPromptSubmit`, `Stop`, and `Interrupt` ignore matchers; `SessionStart`, `PreCompact`, `PostCompact`, and selected tool/subagent events honor event-specific matcher values. The generated configuration and health check must model this distinction. Source: [matcher rules](https://learn.chatgpt.com/docs/hooks#matcher-patterns).
- Correctness-critical capture should remain synchronous. Background hooks can finish out of order or be cancelled, and model-visible hook output is limited/spilled, so recovery context must remain concise. Source: [hook execution and output limits](https://learn.chatgpt.com/docs/hooks#run-hooks-in-the-background).

## Dogfood Boundary

- This is a Copilot session, not a ChatGPT Codex desktop session. It can support implementation and planning, but it is not evidence of Codex hook dispatch, state access, or compaction recovery.
- Running the installer from this Copilot session may modify the installer-owned Codex runtime/configuration and required permission surfaces as part of dogfood; that is not a Codex self-update because Copilot and Codex are separate applications. Preserve unrelated user-authored configuration and session records, and keep automated tests isolated in temporary fixtures.
- Do not treat CLI-only or Copilot evidence as proof of desktop behavior. The desktop run must capture its surface/version, recovery-context delivery, graph/index consultation, deterministic graph validation, and named-rule retrieval/application after compaction.

## Verified Installer Baseline

- `scripts/install-codex.sh` currently configures hooks to invoke the foundation adapter from the repository checkout using a selected system Python; a managed global runtime and Python environment are not yet provisioned.
- The adapter's default session store is user-scoped at `~/.adaptive-agents/sessions/codex`, but the current installer does not provision the exact required access to this namespace.
- `scripts/codex_hooks_config.py` recognizes ownership by the top-level Adaptive Agents description and rewrites the complete expected hooks document. A differently described existing file is preserved and rejected, but additional hook entries in an Adaptive Agents-described file are not merged forward. Migration tests must include extra user-authored entries and prove preservation or fail-closed behavior before mutation.
- These baseline findings identify installer work; they do not change the foundation's artifact, hook-event, or deterministic-validation contract.

## Approved Installer Architecture

- Use a per-user Adaptive Agents runtime root at `~/.adaptive-agents/codex/total-recall/`, resolved from the native user home and kept outside the repository, Codex config home, and session-record namespace.
- Use the selected system Python at its resolved absolute path, require Python 3.11+, and validate it during install/health checks. Do not create a venv or bundle Python unless dependency or compatibility evidence warrants it.
- Use versioned runtime payloads with an explicit manifest recording schema/runtime versions, minimum Python, interpreter path, and managed-file hashes. Prefer a stable launcher across payload upgrades where Codex's hook contract permits.
- Stage and validate updates before switching active state; retain the previous payload for rollback. Never include user-generated session records in ordinary installation, migration, or rollback.
- Preserve the existing Codex permission model; add only narrow required access for supported configurations. Do not silently convert legacy sandbox settings to profiles; fail closed with an actionable diagnostic on unsupported or ambiguous states and preserve approval behavior.
- The runtime and manifest are implemented with schema/runtime versions, selected interpreter, minimum Python version, adapter hash, canonical guidance root, stable launcher, active pointer, and manifest integrity hash. Native Windows integration is covered; macOS/Linux/WSL path and permission behavior remain unverified.
- Permission-profile configurations are intentionally unsupported and fail closed. No implicit profile conversion is attempted.
- Installer rollback restores the active pointer, launcher, Codex config, global redirect, and hooks file. Runtime-level staging failure and installer-level conflict scenarios are covered, but injected failures at every shell mutation boundary and end-to-end upgrades still need tests.
- `--check` validates the managed runtime and installer-owned user Codex configuration. It does not prove Codex's effective hook trust/review state or inspect project-level configuration layers.
- The desktop review UI showed ten new entries as generic `Hook 1`-style titles. The documented user-hook schema exposes no per-handler title/name field; top-level `description` identifies the hooks file, and optional `statusMessage` is for execution feedback rather than hook-review naming. Do not add an undocumented `name` field. Source: [official hooks documentation](https://learn.chatgpt.com/docs/hooks).
- The installer already configures the narrow filesystem writable roots. Hook execution trust is a separate Codex security decision: non-managed hooks require explicit review/trust tied to the exact definition hash, and changed/new definitions are skipped until trusted. Current documentation provides no supported user-level config or installer API to pre-approve these local hooks. Automatic managed trust requires an admin-controlled system/MDM/cloud/enterprise `requirements.toml` source; personal accounts do not use the cloud-managed hooks path. The CLI `--dangerously-bypass-hook-trust` is documented only for one-off automation, not as a persistent desktop installation mechanism. Sources: [hooks and trust](https://learn.chatgpt.com/docs/hooks) and [advanced configuration](https://learn.chatgpt.com/docs/config-file/config-advanced).

## Completion Review

The installer-scoped acceptance criteria are met for the native Windows profile, and the user approved closure with limitations. Verified focused results: Windows-native installer integration (19 checks); foundation adapter (13); managed runtime/launcher (7); permission (2); hook configuration (6). Shell syntax and `git diff --check` passed. Pylance reported no diagnostics in the new runtime installer or launcher; possible-unbound/optional-argument diagnostics remain in existing configuration and adapter code and were not broadly refactored. The full repository health check reported two unrelated planning/link failures and one Claude Code warning; those existing issues were left untouched.

The actual Windows Codex profile passed installation and `--check`. User-approved hooks dispatched in Codex desktop and captured a session graph with 17 lifecycle events, including `PreCompact` and `PostCompact`; deterministic validation passed. A read-only scan of all seven local Codex session graphs found seven valid graphs, no broken Markdown links, and no orphan Markdown files.

Semantic indexing and named-rule retrieval were not established: three of seven indexes had model-authored breadcrumbs, while four retained the no-breadcrumb placeholder, including the compacted dogfood session. The adapter preserves model-authored content and provides advisory maintenance context; it does not itself summarize conversation payloads. This is a foundation reliability gap, not evidence that event capture or graph validation failed.

Other accepted limitations: hook trust remains an explicit Codex review decision; no supported installer mechanism pre-approves local hooks, and the documented schema has no per-handler review-title field. Cross-platform behavior, deeper mutation-boundary failure injection, end-to-end upgrade coverage, broader configuration-layer and matcher checks, and timeout/output-budget validation remain incomplete. These are non-blocking for the accepted Windows installer deliverable and are assigned to the installer-hardening backlog child.

Engineering-quality assessment: implementation and test changes are scoped to the installer integration, preserve unrelated Codex configuration and session records in tested paths, and document unsupported permission profiles as fail-closed. No new runtime/launcher diagnostics were found. Existing repository-health failures and out-of-scope diagnostics are recorded rather than silently treated as fixed.

## Next Actions

1. Continue semantic-index quality, maintenance-reliability, and post-compaction named-rule retrieval work in [the existing session graph quality backlog item](../../backlog/PL-20261027-total-recall/PL-20261027-total-recall-session-graph-quality.md).
2. Continue cross-platform, upgrade/rollback, mutation-boundary, health-check, matcher, and output-budget work in [the installer-hardening backlog item](../../backlog/PL-20261027-total-recall/PL-20261027-total-recall-codex-installer-hardening.md).
3. Keep the parent epic open until its semantic recall and post-compaction rule-retrieval requirements have evidence.
