# PL-20260711: Codex CLI Support

- Status: Backlog
- Readiness: Ready
- Created: 2026-07-11

## Objective

Provide an idempotent Codex CLI integration that loads the canonical Adaptive Agents `AGENTS.md` through one verified native entrypoint.

## Problem Spec

Codex supports `AGENTS.md`, but user-wide discovery, precedence, and external repository access must be verified rather than inferred. Generating plugins, memory, or copied instructions would duplicate canonical routing without evidence those layers are required.

## Scope

Verify official native loading syntax and access boundaries first; then implement the smallest user-wide installer and health check. Preserve unrelated configuration through structured updates, guarantee content-idempotent reruns, avoid copied guidance, and dogfood from an unrelated repository for both the sentinel and a routed workflow.
