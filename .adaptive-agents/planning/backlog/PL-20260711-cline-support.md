# PL-20260711: Cline Support

- Status: Backlog
- Readiness: Ready
- Created: 2026-07-11

## Objective

Provide an idempotent Cline integration that loads the canonical Adaptive Agents `AGENTS.md` through one verified native entrypoint.

## Problem Spec

Cline supports several rule and compatibility formats, but the reliable user-wide entrypoint, precedence, and external-file behavior are not established. Copying rules, skills, hooks, or ignore files would duplicate unrelated functionality.

## Scope

Verify official native loading syntax and access boundaries first; then implement the smallest user-wide installer and health check. Preserve unrelated configuration through structured updates, guarantee content-idempotent reruns, avoid copied guidance, and dogfood from an unrelated repository for both the sentinel and a routed workflow.
