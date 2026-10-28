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
- `codex_total_recall.py` is the Python-first Codex lifecycle-hook adapter for the user-scoped Total Recall session graph; `--hooks-json` prints the installer-facing hook contract.
- `test-codex-total-recall.py` exercises event capture, hierarchical indexes, deterministic reachability validation, recovery context, and hook coverage.
