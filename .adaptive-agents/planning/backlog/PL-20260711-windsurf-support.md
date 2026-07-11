# PL-20260711: Windsurf Support

- Status: Backlog
- Readiness: Ready
- Created: 2026-07-11

## Objective

Provide an idempotent Windsurf integration that loads the canonical Adaptive Agents `AGENTS.md` through one verified native entrypoint.

## Problem Spec

Windsurf supports rule files and compatibility fallbacks, but their user-wide scope, precedence, import semantics, and external-file behavior require verification. Generating separate rules or modifying memory would create unnecessary configuration layers.

## Scope

Verify official native loading syntax and read/write access boundaries first; then implement the smallest user-wide installer and health check applying the two-part pattern proven by Claude Code and VS Code: one native entry point loading canonical `AGENTS.md` content (prose or imperative directives naming the file are not imports), plus the narrowest persistent grant marking the Adaptive Agents repository safe to read and write. Preserve unrelated configuration through structured updates, guarantee content-idempotent reruns, avoid copied guidance, and dogfood from an unrelated repository across fresh sessions for the sentinel, a content-proof probe answerable only from repository content (the sentinel alone can be a false positive), and a routed write-back (e.g., retrospective capture).
