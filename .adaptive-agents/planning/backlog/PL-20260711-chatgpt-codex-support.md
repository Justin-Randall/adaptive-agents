# PL-20260711: ChatGPT Codex Support

- Status: Backlog
- Readiness: Ready
- Created: 2026-07-11
- Test approach: isolated installer regression tests plus fresh-session dogfooding across local Codex clients and supported OS paths

## Objective

Provide one idempotent user-wide integration for local ChatGPT Codex clients (desktop app, CLI, and IDE extension) across supported operating systems, loading the canonical Adaptive Agents `AGENTS.md` through one verified native entrypoint.

## Problem Spec

The local desktop app, CLI, and IDE extension share Codex agent configuration and the global `AGENTS.md` entrypoint under `CODEX_HOME` (default `~/.codex`). On Windows, the desktop app and native CLI use `%USERPROFILE%\\.codex` by default; WSL uses its Linux home unless `CODEX_HOME` is explicitly shared. Codex automatically loads global `AGENTS.md`, with `AGENTS.override.md` taking precedence, then layers project instructions. Differences are platform-specific path discovery and sandbox enforcement, not separate local-client integrations. Official docs do not establish a native include directive or symlink behavior for loading another file's content, so a prose pointer alone is insufficient and the single-source mechanism remains to be verified. Permissions are separate from instructions and project trust: user-level `config.toml` can add the installation path as a workspace-write root, or a named permission profile can grant path-scoped read/write access. The active sandbox/profile determines effective access; preserve normal approval behavior so access inside the grant avoids prompts without disabling approvals outside it. Project trust controls whether project-local `.codex/config.toml` settings load; it does not grant access to this external installation. See [Codex configuration](https://learn.chatgpt.com/docs/developer-settings), [Windows desktop app](https://learn.chatgpt.com/docs/app/windows), [Codex AGENTS.md discovery](https://learn.chatgpt.com/docs/agent-configuration/agents-md), and [Codex permissions](https://learn.chatgpt.com/docs/permissions).

## Scope

Verify the native global-entrypoint behavior and smallest single-source loading mechanism for local ChatGPT Codex clients; do not assume that a prose pointer or symlink imports the canonical file. Implement one installer that resolves `CODEX_HOME` and OS-specific default paths, updates the shared user-level permission configuration with the narrowest persistent read/write grant, and preserves the user's active sandbox/approval behavior and unrelated settings. Ensure content-idempotent reruns, add isolated installer tests, and validate the current Windows desktop app plus other supported local clients/platforms. Dogfood from an unrelated repository in fresh sessions for the sentinel, a content-proof probe answerable only from canonical repository content, and a routed write-back (for example, a retrospective capture).
