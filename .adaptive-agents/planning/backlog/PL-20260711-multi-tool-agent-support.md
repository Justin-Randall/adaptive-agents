# PL-20260711: Multi-Tool Agent Coding Support

- Status: Backlog
- Readiness: Ready
- Created: 2026-07-11

## Objective

Coordinate user-wide Adaptive Agents integrations for Claude Code, Codex CLI, Cline, Cursor, Windsurf, GitHub Copilot Agent Mode, Antigravity, Gemini CLI, and OpenCode around one verified native entrypoint per tool.

## Problem Spec

Each coding agent has different instruction discovery, import semantics, access boundaries, and configuration scopes. A shared contract is needed without assuming one tool's file format or settings apply to another. Generated copies must not become competing sources of truth.

## Scope

Track the individual tool plans and require each integration to implement the two-part pattern proven by Claude Code and VS Code: (1) one verified native entry point in the tool's user-level startup config loading canonical `AGENTS.md` content (prose or imperative directives naming the file are not imports), and (2) the tool's narrowest persistent grant marking the Adaptive Agents repository safe to read and write from sessions rooted elsewhere. Each installer must preserve and deduplicate user configuration, remain content-idempotent, avoid copied guidance, expose deterministic health checks, and pass fresh-session dogfooding from an unrelated repository for the sentinel, a content-proof probe answerable only from repository content (the sentinel alone can be a false positive), and a routed write-back.
