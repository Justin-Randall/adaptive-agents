# PL-20260711: GitHub Copilot Agent Mode Support

- Status: Backlog
- Readiness: Ready
- Created: 2026-07-11

## Objective

Verify and extend the VS Code installer so GitHub Copilot Agent Mode consistently loads the canonical Adaptive Agents `AGENTS.md` without writing project-owned instruction files.

## Problem Spec

The existing VS Code integration registers external user-wide instruction locations, but Agent Mode and code-review surfaces may discover instructions differently. Their actual loading and access behavior must be tested before adding another entrypoint or settings mutation.

## Scope

Verify official native loading syntax and read/write access boundaries first; then update the existing installer and health check only where required, keeping the two-part pattern proven by Claude Code and VS Code: one native user-level entry point loading canonical `AGENTS.md` content (prose or imperative directives naming the file are not imports; no project-owned instruction files such as `.github/copilot-instructions.md`), plus the narrowest persistent grant marking the Adaptive Agents repository safe to read and write. Preserve unrelated settings, guarantee content-idempotent reruns, avoid copied guidance, and dogfood from an unrelated repository across fresh sessions for the sentinel, a content-proof probe answerable only from repository content (the sentinel alone can be a false positive), and a routed write-back (e.g., retrospective capture).

Parity gap to close while here: the VS Code integration predates the installer-duties contract — it has no isolated automated test script (`scripts/test-install-vscode.sh` does not exist) and no live-config validation function in `scripts/check-adaptive-agents.sh` (Claude Code and OpenCode both have one). Bring it up to parity as part of this work.
