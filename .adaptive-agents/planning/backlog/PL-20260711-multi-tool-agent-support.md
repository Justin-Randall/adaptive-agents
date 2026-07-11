# PL-20260711: Multi-Tool Agent Coding Support

- Status: Backlog
- Readiness: Ready
- Created: 2026-07-11

## Objective

Coordinate user-wide Adaptive Agents integrations for Claude Code, Codex CLI, Cline, Cursor, Windsurf, GitHub Copilot Agent Mode, Antigravity, Gemini CLI, and OpenCode around one verified native entrypoint per tool.

## Problem Spec

Each coding agent has different instruction discovery, import semantics, access boundaries, and configuration scopes. A shared contract is needed without assuming one tool's file format or settings apply to another. Generated copies must not become competing sources of truth.

## Scope

Track the individual tool plans and require each integration to verify official native loading, handle external access explicitly, preserve and deduplicate user configuration, remain content-idempotent, avoid copied guidance, expose deterministic health checks, and pass live sentinel plus routed-workflow dogfooding from an unrelated repository.
