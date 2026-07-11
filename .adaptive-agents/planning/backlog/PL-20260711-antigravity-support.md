# PL-20260711: Antigravity Support

- Status: Backlog
- Readiness: Ready
- Created: 2026-07-11

## Objective

Provide an idempotent Antigravity integration that loads the canonical Adaptive Agents `AGENTS.md` through one verified native entrypoint.

## Problem Spec

Antigravity exposes several extension surfaces, but the native instruction entrypoint, user-wide scope, import semantics, and external-path behavior require verification. Plugin manifests, commands, skills, and hooks should not be generated unless the core loading path demonstrably requires them.

## Scope

Verify official native loading syntax and access boundaries first; then implement the smallest user-wide installer and health check. Preserve unrelated configuration through structured updates, guarantee content-idempotent reruns, avoid copied guidance, and dogfood from an unrelated repository for both the sentinel and a routed workflow.
