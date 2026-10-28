# PL-20261027-total-recall-codex-foundation Memory

Curated handoff context for the active Codex Total Recall foundation work unit.

## Status

Completed — foundation implementation and its approved closure review are complete; installer-owned and semantic-recall follow-ups remain tracked separately.

## Current Context

- Branch: `pl-20261027-total-recall`.
- Parent epic: [Total Recall for Session Details](../backlog/PL-20261027-total-recall.md).
- Source child: [Codex Total Recall Foundation](../backlog/PL-20261027-total-recall/PL-20261027-total-recall-codex-foundation.md).
- The sibling installer child remains in `Backlog` and depends on this foundation.
- Canonical runtime session artifacts are planned under `~/.adaptive-agents/sessions/codex/<adaptive-session-uuid>/`.

## Verified Planning Facts

- Local Codex runtime probe reports `codex-cli 0.163.0-alpha.10.2`; `codex features list` reports `hooks` as stable and enabled. No `codex hooks` subcommand exists; current docs identify `~/.codex/hooks.json`, inline `config.toml`, and project-local equivalents as hook sources.
- Codex hook documentation covers `SessionStart`, `PreCompact`, `PostCompact`, `SessionEnd`, `UserPromptSubmit`, `PreToolUse`, and `PostToolUse`.
- Current hook docs also expose `Stop`, `SubagentStart`, and `SubagentStop`; `Stop` can provide the latest assistant message, while subagent hooks report the parent session id and subagent identity.
- Hook payloads expose a provider `session_id`; transcript format is not a stable persistence interface.
- `SessionStart` with `source: "compact"` can provide recovery context before continuation, including after mid-turn automatic compaction.
- Provider compaction state is opaque in the OpenAI compaction guidance. Local Codex hook documentation does not establish that the opaque item is exposed to command hooks.
- The installed user config currently uses legacy `sandbox_mode = "elevated"` and `[sandbox_workspace_write]`; no hooks are configured. The existing installer must not be changed by this foundation child, because hook provisioning and migration belong to the installer child.
- The repository has GitHub static validation for Ubuntu and Windows with Python 3.11 in `.github/workflows/static-validation.yml`.

## Foundation Evidence

- `scripts/codex_total_recall.py` now provides adapter-owned UUID mapping, Markdown event records, root/index-of-indices generation, atomic writes, cross-platform locking, deterministic ledger/link/anchor/reachability validation, malformed-ledger fail-closed behavior, compact `SessionStart` recovery context, and a model-visible `UserPromptSubmit` semantic-maintenance contract.
- `scripts/test-codex-total-recall.py` passes 13 focused tests using the bundled Python runtime, including idempotence, representative event retention, stable provider-to-adaptive identity mapping, isolated session-namespace write validation, orphan/accounting failures, malformed-ledger preservation, recovery context with Adaptive Agents authority paths, semantic-maintenance prompting, fenced-payload link filtering, and hook configuration coverage. `scripts/test-codex-hooks-config.py` passes 2 provisioning tests, including Windows command serialization.
- An isolated command-hook integration probe generated and validated a complete session graph without writing to the real user session store.
- A real ephemeral Codex CLI run (`codex-cli 0.163.0-alpha.10.2`) dispatched `SessionStart`, `UserPromptSubmit`, and `Stop` to the adapter from a temporary trusted project hook layer; one UUID session graph with three event records was generated and validated, then all temporary artifacts were removed.
- A corrected `gpt-5.6-luna` interactive Codex run forced manual compaction with `/compact`. The graph captured the complete observed lifecycle, including `PreCompact`, `PostCompact`, compact `SessionStart`, recovery `UserPromptSubmit`, tool activity, `Stop`, and `SessionEnd`; it validates successfully. Codex's own rollout transcript contains a `ContextCompaction` item and developer messages tagged `hooks.additional_context` containing the recovery text, canonical `AGENTS.md`, and absolute graph `INDEX.md` path. After compaction the model read the graph and linked events, validated it, and returned `COMPACT-HOOK-FACT-4472`.
- The post-compaction model answered the marker `ALPHA-RECALL-7291`, proving fact recall after compaction, but transcript inspection found no `ACTIVE.md` or `Codex Total Recall Foundation` content delivered after compaction. The only recovery guidance delivered was the concise pointer from `recovery_context`; the `PL-20261027-total-recall` text found in session metadata was branch/session context, not retrieved planning guidance.
- The generated `INDEX.md` and sub-indexes were structurally valid but semantically weak: they contained complete event-ledger, recent, and event-type navigation without meaningful breadcrumbs for instructions, decisions, requirements, unresolved questions, evidence, or artifacts. Event categorization is not sufficient Total Recall navigation.
- A separate non-compaction Codex model dogfood established the missing semantic behavior: the model wrote `Durable fact: DOGFOOD-FACT-4821` into the root semantic section, linked it to the captured `UserPromptSubmit` event with a descriptive explanation, and the deterministic validator passed. The preserved evidence is under `.tmp-codex-total-recall-dogfood/`.
- The session root now starts with a deterministic Recovery Bootstrap section linking to canonical Adaptive Agents `AGENTS.md` as a local `file://` Markdown target. The validator resolves and verifies local file links and anchors, including that external authority link; a focused test proves a missing external Markdown target fails validation. Web URLs remain references rather than session-graph artifacts.
- The Codex installer path now has a conservative Python hook-config helper. It creates the user-level `hooks.json` when absent, rewrites only an existing Adaptive Agents-owned config, preserves unrelated user hooks by failing closed, and is covered by focused tests. A generated fixture is preserved at `.tmp-codex-total-recall-dogfood/verified-hooks.json`.
- The first real Codex retry exposed a Windows command-parser defect: quoting a no-space executable at the beginning of `commandWindows` caused hook exit code 1. Removing only that unnecessary outer quote fixed real hook dispatch; the later full forced-compaction run is evidence of the corrected configuration.
- The validator initially parsed Markdown-looking links inside fenced raw hook payloads as graph edges. `_without_fenced_code()` now excludes those serialized payloads from reachability analysis, with a regression test; real graph validation passes after the fix.
- A later named-rule dogfood could not start because Codex's own `C:\Users\User\.codex` directory and `state_5.sqlite` grant only `ReadAndExecute` to the Codex sandbox account. Codex exits with SQLite error 14 before loading project hooks. The Total Recall session namespace remains writable. The user chose to defer Codex-home permission repair and the named-rule dogfood to the installer child, which can run outside this restricted Codex environment; do not conflate that repair with the adapter's narrow session-namespace permission contract.
- Codex's documented `PreCompact` hook runs before compaction and accepts common control output, but does not provide model-visible `additionalContext`; plain stdout is ignored. Therefore pre-compact semantic graph construction cannot depend on prompting the model from the `PreCompact` hook itself. The full-session semantic maintenance query must run incrementally or through a separate supported path before compaction, while `PreCompact` performs the deterministic checkpoint and `SessionStart(source=compact)` restores only the graph pointer and retrieval contract.
- The detailed [event coverage matrix](PL-20261027-total-recall-codex-foundation-event-coverage.md) records a current activation blocker for hosted tools: official docs say they do not use the local function-tool hook path, and the transcript format is not a stable persistence API.

## Decisions and Constraints

- Preserve the backlog source specification; formal acceptance criteria and ordered test execution are now in `planning/active/ACTIVE.md`.
- Do not fabricate provider compaction output when only lifecycle trigger/turn metadata is available.
- Do not make project-local layers or Codex-private transcript storage the canonical session graph location.
- Deterministic validation must enforce the non-orphaning/reachability invariant even when the model proposes semantic organization.
- Automated tests must use isolated temporary configuration and must not mutate the real user Codex configuration.

## Completion Review

- Disposition: Completed with installer-child handoff.
- Acceptance criteria: foundation-scoped criteria are satisfied and checked in the closed SDD. Codex-home permission repair, named-rule post-compaction dogfood, broader surface compatibility, and Bash installer execution are explicitly outside this foundation closure and transferred to `PL-20261027-total-recall-codex-installer`.
- Verification: 13 adapter tests, 2 hook-provisioning tests, Python compilation, instruction-load budget check, `git diff --check`, isolated hook integration, real Codex lifecycle dispatch, forced compaction, post-compaction graph consultation, semantic breadcrumb dogfood, and deterministic validation of preserved graphs.
- Quality review: deterministic validation owns event accounting, link/anchor resolution, root reachability, and non-orphaning; model-authored semantics remain advisory and source-linked. The session namespace write contract is tested in isolated fixtures. No unrelated user Codex configuration was mutated by automated tests.
- Deferred handoff: the installer child must repair/provision Codex-home permissions outside the restricted environment, run the named-rule compaction dogfood, complete permission-sensitive installer tests, and perform final parent-level closure review.
- No blocking foundation defect remains within the supported CLI-only boundary.

## Handoff

1. Activate `PL-20261027-total-recall-codex-installer` as the next work unit.
2. Preserve the latest real compaction graph and semantic breadcrumb graph as user-inspectable evidence.
3. Retain hosted-tool coverage as an explicit activation limitation until Codex exposes a supported observation path.

## Deferred Questions

- Exact Codex version/surface rollout target and any version gates.
- Complete event coverage and supported fallback for unobservable event types.
- Resume/fork/subagent graph topology.
- Cross-platform permission merge shape.
- Synchronous hook timeout and serialization thresholds.
- Provider-compaction access path and reconciliation inputs.
- How Codex transcript/tool evidence can prove graph consultation and rule compliance rather than only provider-summary fact recall.
- Semantic breadcrumb schema, required concept coverage, and deterministic validation boundary.
