# Active Memory

Curate this file for cross-session handoff. Replace stale details rather than keeping an append-only journal.

## Current State

- PL-20260710 (OpenCode Installer Support) is active.
- Implementing: OpenCode installer script, command files, global config template, umbrella installer, README updates.

## Decisions

- SDD sections live inside `ACTIVE.md`, not separate files.
- Standard SDD sub-sections: Problem Spec, Feature Specs, Interface/Contract Specs, Data Model Specs, Behavioral Specs.
- Acceptance criteria trace to spec items.
- Plans capture relevant project rules in a `## Applicable Guidance` section.
- Plan IDs use `PL-YYYYMMDD` (date-only) format; legacy `PL-YYYYMMDDTHHMMSSZ` and `PL-####` accepted for backward compatibility.
- OpenCode installer uses same Python JSON merge pattern as `install-vscode.sh`.
- Idempotency marker: `"_adaptive_agents_installed": true` in OpenCode config.

## Blockers

- Need to determine correct OpenCode global config path at runtime (OS-dependent).

## Deferred Discoveries

- Consider separate `.sdd.md` spec files or external spec tooling if plans grow too large for a single `ACTIVE.md`.
