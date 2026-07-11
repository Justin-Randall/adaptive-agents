# PL-20260711: Gemini CLI Support

- Status: Backlog
- Readiness: Ready
- Created: 2026-07-11

## Objective

Provide an idempotent Gemini CLI integration that loads the canonical Adaptive Agents `AGENTS.md` through one verified native entrypoint.

## Problem Spec

Gemini CLI uses `GEMINI.md`, but user-wide discovery, import semantics, and external repository access must be verified. Installing copied commands or skills would duplicate routing already owned by `AGENTS.md` and `INDEX.md`.

## Scope

Verify official native loading syntax and access boundaries first; then implement the smallest user-wide installer and health check. Preserve unrelated configuration through structured updates, guarantee content-idempotent reruns, avoid copied guidance, and dogfood from an unrelated repository for both the sentinel and a routed workflow.
