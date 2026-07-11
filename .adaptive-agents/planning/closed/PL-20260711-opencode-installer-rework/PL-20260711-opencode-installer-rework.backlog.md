# PL-20260711: OpenCode Installer Rework

- Status: Backlog
- Readiness: Ready
- Created: 2026-07-11

## Objective

Redesign the OpenCode installer so OpenCode verifiably loads the canonical Adaptive Agents `AGENTS.md` through one tool-native entrypoint.

## Problem Spec

The previous OpenCode installer was closed as completed, but dogfooding showed that OpenCode sessions did not reliably honor `AGENTS.md` or return `ADAPTIVE_AGENTS_GLOBAL_LOADED`. The existing configuration layers have not established which OpenCode mechanism actually loads user-wide instructions, whether external-path access is granted, or whether successful behavior survives fresh sessions rather than cached state.

## Scope

Verify OpenCode's official native loading syntax, precedence, external-path boundaries, trust prompts, and effective user-level config before redesigning the installer. Use one canonical entrypoint, preserve and deduplicate unrelated settings, remove redundant generated layers, keep same-version reruns byte-for-byte stable, and validate the exact install destination. Dogfood the sentinel and a routed planning workflow from an unrelated repository across multiple fresh sessions so intermittent loading remains a failure rather than a pass.
