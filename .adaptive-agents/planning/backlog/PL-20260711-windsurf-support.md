# PL-20260711: Windsurf Support

- Status: Backlog
- Readiness: Ready
- Created: 2026-07-11

## Objective

Provide an idempotent Windsurf integration that loads the canonical Adaptive Agents `AGENTS.md` through one verified native entrypoint.

## Problem Spec

Windsurf supports rule files and compatibility fallbacks, but their user-wide scope, precedence, import semantics, and external-file behavior require verification. Generating separate rules or modifying memory would create unnecessary configuration layers.

## Scope

Verify official native loading syntax and access boundaries first; then implement the smallest user-wide installer and health check. Preserve unrelated configuration through structured updates, guarantee content-idempotent reruns, avoid copied guidance, and dogfood from an unrelated repository for both the sentinel and a routed workflow.
