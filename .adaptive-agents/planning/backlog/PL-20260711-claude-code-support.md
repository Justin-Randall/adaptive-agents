# PL-20260711: Claude Code Support

- Status: Backlog
- Readiness: Ready
- Created: 2026-07-11

## Objective

Provide an idempotent user-wide Claude Code installer that loads the canonical Adaptive Agents `AGENTS.md` through Claude's native instruction mechanism.

## Problem Spec

Claude Code reads `CLAUDE.md`, not `AGENTS.md`. Prose directing the model to read an external path fails when runtime file access is outside the active working directories. A valid integration requires a native `@` import and the narrow `permissions.additionalDirectories` grant needed for files routed from `AGENTS.md`.

## Scope

Create and validate the Claude installer, umbrella routing, health checks, and documentation. Preserve unrelated settings with a structured merge, deduplicate the access grant, keep same-version reruns byte-for-byte stable, and dogfood from outside the guidance repository for both the sentinel and a routed planning workflow.
