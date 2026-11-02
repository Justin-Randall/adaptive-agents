# Codex Tests

Run Python files directly with the repository's Python interpreter. Run shell
tests with Bash (Git Bash on native Windows). The root
[health checker](../../check-adaptive-agents.sh) includes these suites.

| Test | Boundary |
|---|---|
| [test-install-codex.sh](test-install-codex.sh) | Actual installer fresh install, upgrade, rerun, dry-run and configuration/session preservation. |
| [test-codex-config.py](test-codex-config.py) | Narrow permission merging and idempotence. |
| [test-codex-hooks-config.py](test-codex-hooks-config.py) | Hook ownership, inline migration and fail-closed conflicts. |
| [test-codex-total-recall-installer.py](test-codex-total-recall-installer.py) | Installed launcher, integrity, reader paths, Unicode, rollback and checkout relocation. |
| [test-codex-total-recall.py](test-codex-total-recall.py) | Markdown-only hook/CLI contract, source preservation and explicit legacy rejection. |
| [test-codex-markdown-recall.py](test-codex-markdown-recall.py) | Payload fidelity, stable anchors, concurrency, append/restart and bounded reads/search. |
| [test-codex-markdown-dogfood.py](test-codex-markdown-dogfood.py) | Evidence accounting, adequate search excerpts and report preservation. |
| [test-codex-total-recall-dogfood.py](test-codex-total-recall-dogfood.py) | Historical ordered source-retrieval evidence. |
| [test-codex-recall-pivot.py](test-codex-recall-pivot.py) | Historical pivot report checks. |
| [test-codex-total-recall-recovery.py](test-codex-total-recall-recovery.py) | Retired recovery fails without mutating files. |
