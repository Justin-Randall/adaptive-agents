# Active Memory

Curate this file for cross-session handoff. Replace stale details rather than keeping an append-only journal.

## Current State

- Template, bootstrap, discovery routing, scoped retrospectives, project memory, documentation, integrated validation, upgrade inspection, regression tests, installer verification, and dogfood creation are complete.
- The active packet remains open pending user review and approval to close it.

## Decisions

- Keep `INDEX.md` authoritative and `README.md` human-oriented but non-authoritative.
- Keep progress and verification in `ACTIVE.md`; use this file only for cross-session facts and decisions.
- Project-layer backlog writes, activation, closure, and next-work selection require user approval.
- Track this repository's dogfood Project Layer so it serves as a shared example.
- Choose retrospective scope before target type; uncertain lessons stay project-local when a Project Layer exists.

## Blockers

- None.

## Deferred Discoveries

- Consider adding a first-class deterministic activation/closure command after the model-led lifecycle has been dogfooded further.
- Consider richer template upgrade baselines if content-aware three-way merges become necessary.
