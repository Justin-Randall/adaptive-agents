# PL-20260717: VS Code Trusted-Directory Permissions for Adaptive Agents

- Status: Backlog
- Readiness: Ready
- Created: 2026-07-17
- Tags: bug, vscode, integration, permissions

## Objective

Eliminate the need for users to manually trigger "Is Adaptive Agents active?" to prompt VS Code's file-permission dialog. Grant permanent read/write access to the user-wide Adaptive Agents installation directory so the integration works transparently.

## Problem Spec

When the VS Code agent encounters a user-wide instruction file that references external paths (e.g., `@C:/Users/logic/github.com/Justin-Randall/adaptive-agents/...`), it prompts the user to approve file access one directory at a time. The current integration requires the user to know to ask "Is Adaptive Agents active?" — which triggers the agent to read enough files that VS Code surfaces the permission prompts. This is:

- **Non-discoverable** — new users can't know the magic question.
- **Frictionful** — even after knowing the question, each session may re-prompt depending on VS Code's permission caching.
- **Inconsistent** — other integrations (Claude Code, Cline) don't have this gate; VS Code should work just as smoothly.

The root cause is that VS Code Copilot has a per-file/per-directory permission model that is not being pre-configured during installation.

## Scope

1. Research VS Code's file permission/trust model for the Copilot agent — identify the correct mechanism for pre-granting read/write access to a directory (workspace trust, `files.dialog`, `security.allowed`, `copilot`-specific trusted paths, or equivalent).
2. Update `install-vscode.sh` to register the Adaptive Agents repository directory as permanently trusted for read/write.
3. Update `scripts/check-adaptive-agents.sh` to validate that the trust grant is present.
4. Dogfood from an unrelated repository: verify that opening a fresh VS Code session no longer prompts for permission on `@`-referenced files in the Adaptive Agents repo and that all three probes (sentinel, content-proof, routed write-back) pass without intervention.
