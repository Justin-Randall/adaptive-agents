# Active Memory

Curate this file for cross-session handoff. Replace stale details rather than keeping an append-only journal.

## Current State

- PL-20260710T110000Z (SDD Output for Planning Artifacts) is closed as Completed.
- No active plan. The active slot is empty pending selection of next work.

## Decisions

- SDD sections live inside `ACTIVE.md`, not separate files.
- Standard SDD sub-sections: Problem Spec, Feature Specs, Interface/Contract Specs, Data Model Specs, Behavioral Specs.
- Acceptance criteria trace to spec items.
- Plans capture relevant project rules in a `## Applicable Guidance` section.
- Plan IDs use ISO 8601 UTC timestamp format (`PL-YYYYMMDDTHHMMSSZ`); legacy `PL-####` accepted for backward compatibility.

## Blockers

- None.

## Deferred Discoveries

- Consider separate `.sdd.md` spec files or external spec tooling if plans grow too large for a single `ACTIVE.md`.
- Consider a first-class deterministic activation/closure command after the model-led lifecycle has been dogfooded further.
