# Scripts

This directory contains deterministic setup, validation, inspection, installation, and migration scripts for Adaptive Agents.

Scripts should be safe to run repeatedly when practical, report actionable failures, and avoid writing outside their documented target paths.

## Markdown Browser

- `ui.py` starts or generates the system-owned Markdown Browser.
- `markdown_browser.py` contains the HTTP server, Project Layer/System navigation, SSE, and watchdog implementation.
- Run `py -3 scripts/ui.py serve --target <project-root>` from this repository to browse any project that has a `.adaptive-agents` Project Layer.

Use this area for executable repository maintenance. Put procedural explanations in [playbooks](../playbooks/INDEX.md) and user-facing setup narrative in [README.md](../README.md).

## Tool Installers

- `install.sh` detects supported local tools; pass `--tool codex` to target ChatGPT Codex.
- `install-codex.sh` writes a minimal global Codex redirect to canonical `AGENTS.md`, grants workspace write access to the repository and session store, provisions the managed Total Recall runtime and hook configuration, and supports `--check`.
- `codex_total_recall_installer.py` stages and validates versioned runtime payloads, active pointers, and integrity manifests under the per-user runtime root.
- `codex_total_recall_launcher.py` is the stable hook entrypoint; it verifies the active managed payload before dispatching the adapter.
- `test-install-codex.sh` exercises installer lifecycle and preservation behavior with isolated temporary Codex homes.
- `test-codex-total-recall-installer.py` covers managed runtime provisioning, integrity checks, rollback behavior, and launcher dispatch.
- `test-codex-config.py` verifies narrow repository/session-store permission merging and idempotence.
- `codex_hooks_config.py` safely creates or validates the Adaptive Agents-owned `hooks.json` without overwriting unrelated user hooks.
- `test-codex-hooks-config.py` verifies hook provisioning, migration ownership, and fail-closed handling of conflicting user configuration.
- [codex_total_recall.py](codex_total_recall.py) is the self-contained runtime-1.2 Markdown adapter: complete deterministic capture, bounded anchor reads/literal search/recent events, declared-link validation and nonblocking hooks. PostToolUse supplies actual result-part handles within 1,200 bytes. Old JSON/JSONL sessions and migration/coverage/line-reader flags are explicitly unsupported; start fresh.
- [dogfood-codex-recall-pivot.py](dogfood-codex-recall-pivot.py) retains historical JSONL replay helpers for report tests. Its live entrypoint is retired; use Markdown dogfood.
- [codex_markdown_recall.py](codex_markdown_recall.py) is a thin explicit-root wrapper around the canonical runtime for isolated tests, not a second implementation or alternate format.
- [dogfood-codex-markdown.py](dogfood-codex-markdown.py) compares selective and proactive guidance using six ordinary Luna turns, native Markdown capture, per-turn index snapshots, compaction and fresh-context source-backed questions. Alternatively, `--frozen-session` tests an existing unmodified graph/ledger in hook-free, read-only fresh Luna contexts with index-only controls and natural questions. It incurs model usage, retains evidence, and never upgrades the live profile. Run `--help` for the required isolated workspace/report arguments; predeclared budgets and quality gates are in the active plan.
- [test-codex-markdown-recall.py](test-codex-markdown-recall.py) checks fidelity, stable within-event anchors, safe append/restart, concurrency, legacy rejection and bounded search/read pagination. [test-codex-markdown-dogfood.py](test-codex-markdown-dogfood.py) checks the experiment's evidence accounting without model usage.
- [test-codex-total-recall.py](test-codex-total-recall.py) tests the Markdown-only hook/CLI contract, source preservation, opportunistic topics, raw UTF-8, removed flags and fail-closed legacy rejection.
- [recover-codex-total-recall.py](recover-codex-total-recall.py) is an explicitly retired JSONL recovery entrypoint. [Its regression test](test-codex-total-recall-recovery.py) proves preview, apply and CLI fail without mutating historical files.
- [dogfood-codex-total-recall.py](dogfood-codex-total-recall.py) retains the shared native app-server client and historical evidence helpers; its JSONL live entrypoint is retired. Use [Markdown dogfood](dogfood-codex-markdown.py), including `--packaged-runtime` to test the installed stable launcher in an isolated profile.
- [test-codex-total-recall-dogfood.py](test-codex-total-recall-dogfood.py) validates retained historical ordered-retrieval reports without restoring legacy runtime support.
