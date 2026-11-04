# PL-20260711 Copilot Agent Mode Support Memory

- Work unit: `PL-20260711-copilot-agent-mode`.
- The current installer is `scripts/install-vscode.sh`; it installs `~/.copilot/hooks/adaptive-agents.json` and invokes `scripts/vscode/copilot_total_recall.py`.
- Live dogfood proved prompt capture and repeated ledger search, but assistant response text is not captured by the current hook adapter.
- In the supplied Copilot session, `Stop` payloads include `transcriptPath` and `stopReason` but no response text; the response exists in the referenced Copilot `events.jsonl`.
- Do not repair or rewrite the supplied session ledger. Reproduce with isolated transcript fixtures and preserve the original evidence.
- Next action: write failing tests for bounded transcript response extraction and deduplication, then implement the smallest adapter change.
- Merge review found no blocking Copilot capture defect. Antigravity support is being deprecated and is intentionally excluded from check-mode follow-up.
- Planned fixes for remaining installers: make `--dry-run` and `--check` mutually exclusive, validate Claude/OpenCode configuration structurally rather than with path substring searches, and add direct read-only tests for tool-specific and umbrella checks.
- Check-mode implementation is complete for the non-deprecated installers; tests normalize MSYS and Windows drive path forms and pass in Git Bash.
