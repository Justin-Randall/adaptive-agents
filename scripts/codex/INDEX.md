# Codex Scripts

Entry point: [install-codex.sh](../install-codex.sh). Installation still uses a
versioned, self-contained adapter behind the stable user-scoped launcher;
reorganizing this checkout does not require migrating existing installations.

## Runtime and Installation

- [codex_config.py](codex_config.py): preserve user configuration while merging
  the narrow repository/session-store permission grant.
- [codex_hooks_config.py](codex_hooks_config.py): provision managed hooks without
  overwriting unrelated file or inline configuration.
- [codex_total_recall_installer.py](codex_total_recall_installer.py): stage,
  validate and activate versioned runtime payloads with integrity manifests.
- [codex_total_recall_launcher.py](codex_total_recall_launcher.py): source for the
  stable installed launcher; validates the active manifest before dispatch.
- [codex_total_recall.py](codex_total_recall.py): authoritative Markdown capture,
  bounded anchor reads/search/recent events, declared-link validation and
  nonblocking hooks. Old JSON/JSONL recall sessions remain unsupported.

## Dogfood and Historical Evidence

- [codex_markdown_recall.py](codex_markdown_recall.py): explicit-root wrapper
  around the canonical runtime for isolated tests.
- [dogfood-codex-markdown.py](dogfood-codex-markdown.py): isolated Luna task/topic,
  compaction and fresh-context recall trials. `--packaged-runtime` tests the real
  stable launcher; `--frozen-session` tests unchanged historical navigation.
  Model usage is opt-in. Reports and failures are retained; live configuration
  is never upgraded by this driver.
- [dogfood-codex-total-recall.py](dogfood-codex-total-recall.py): shared native
  app-server client and historical JSONL evidence helpers; live entrypoint retired.
- [dogfood-codex-recall-pivot.py](dogfood-codex-recall-pivot.py): historical replay
  helpers; live entrypoint retired.
- [recover-codex-total-recall.py](recover-codex-total-recall.py): retired recovery
  entrypoint that fails without changing historical files.

See [Codex tests](tests/INDEX.md) for deterministic checks without model usage.
