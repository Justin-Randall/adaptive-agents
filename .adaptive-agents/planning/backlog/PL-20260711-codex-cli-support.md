# PL-20260711: Codex CLI Support

- Status: Backlog
- Readiness: Ready
- Created: 2026-07-11

## Objective

Provide an idempotent Codex CLI integration that loads the canonical Adaptive Agents `AGENTS.md` through one verified native entrypoint.

## Problem Spec

Codex supports `AGENTS.md`, but user-wide discovery, precedence, and external repository access must be verified rather than inferred. Generating plugins, memory, or copied instructions would duplicate canonical routing without evidence those layers are required.

## Scope

Verify official native loading syntax and read/write access boundaries first; then implement the smallest user-wide installer and health check applying the two-part pattern proven by Claude Code and VS Code: one native entry point loading canonical `AGENTS.md` content (prose or imperative directives naming the file are not imports), plus the narrowest persistent grant marking the Adaptive Agents repository safe to read and write. Preserve unrelated configuration through structured updates, guarantee content-idempotent reruns, avoid copied guidance, and dogfood from an unrelated repository across fresh sessions for the sentinel, a content-proof probe answerable only from repository content (the sentinel alone can be a false positive), and a routed write-back (e.g., retrospective capture).
