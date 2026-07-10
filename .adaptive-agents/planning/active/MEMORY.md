# Active Memory

Curate this file for cross-session handoff. Replace stale details rather than keeping an append-only journal.

## Current State

- PL-20260709T120000Z (Project Layer) is closed as Completed.
- PL-20260710T110000Z (SDD Output for Planning Artifacts) is the active plan.
- The SDD `## Specifications` section structure is defined in the active plan and will be dogfooded on PL-20260710T110000Z itself.
- Next step after this plan: update the canonical template to include the SDD section.

## Decisions

- Keep `INDEX.md` authoritative and `README.md` human-oriented but non-authoritative.
- SDD sections live inside `ACTIVE.md`, not separate files — keeps plans self-contained.
- The `## Specifications` section goes between `## Objective` and `## Scope`.
- Standard SDD sub-sections: Problem Spec, Feature Specs, Interface/Contract Specs, Data Model Specs, Behavioral Specs.
- Acceptance criteria trace to spec items — each AC references a named spec rule or sub-section.
- Plans capture relevant project rules in a `## Applicable Guidance` section with short descriptions and links to authoritative sources, so agents executing the plan see the rules directly.

## Blockers

- None.

## Deferred Discoveries

- Consider adding a first-class deterministic activation/closure command after the model-led lifecycle has been dogfooded further.
- Consider richer template upgrade baselines if content-aware three-way merges become necessary.
- Consider separate `.sdd.md` spec files or external spec tooling if plans grow too large for a single `ACTIVE.md`.
