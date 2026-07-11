# PL-20260711: GitHub Copilot Agent Mode Support

- Status: Backlog
- Readiness: Ready
- Created: 2026-07-11

## Objective

Verify and extend the VS Code installer so GitHub Copilot Agent Mode consistently loads the canonical Adaptive Agents `AGENTS.md` without writing project-owned instruction files.

## Problem Spec

The existing VS Code integration registers external user-wide instruction locations, but Agent Mode and code-review surfaces may discover instructions differently. Their actual loading and access behavior must be tested before adding another entrypoint or settings mutation.

## Scope

Verify official native loading syntax and access boundaries first; then update the existing installer and health check only where required. Preserve unrelated settings, guarantee content-idempotent reruns, avoid copied guidance, and dogfood from an unrelated repository for both the sentinel and a routed workflow.
