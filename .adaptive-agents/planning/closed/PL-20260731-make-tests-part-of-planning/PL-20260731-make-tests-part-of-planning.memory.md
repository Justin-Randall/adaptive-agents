# PL-20260731-make-tests-part-of-planning — Working Memory

- Work Unit: PL-20260731-make-tests-part-of-planning
- Activated: 2026-07-31
- Status: Completed

## Trigger

The user observed that planning artifacts (active plan, backlog) never include tests. Requirements: tests must prove behavior (falsifiable), failure paths tested, tests written before feature work (surfacing seams/mocks/DI early), 100% coverage of code written, fast tests, language-appropriate methodology, CI with ask-if-missing. Guidance must stay lean — rule + link, discovery over enumeration, small token footprint.

## Design Constraints

- Lean footprint: instruction-load gate (32,768 budget) is the enforcement; new contract targets est. < ~800 tokens.
- New authoritative contract in `instructions/testing.instructions.md`; `tdd.instructions.md` stays a workflow doc.
- `## Test Plan` required in ACTIVE.md by both check-project-layer.sh copies ("No Active Plan" exempt); research plans use "research — no tests".
- Backlog `Test approach` one-liner; all 7 existing backlog items are research.
- CI ask-if-missing is behavioral in manage-planning, not a validator gate.
- Template manage-planning copy synced to live (epic-split drift) as part of the edit.
- template.json bumped 0.5.1 → 0.5.2.

## Open Questions

- None.

## Sources

- Graphify graph report + edge analysis: zero planning↔testing edges; planning-conventions.md only reachable via root INDEX.md.
- Repo CI precedent: `.github/workflows/static-validation.yml` (Ubuntu+Windows, 10-min timeout).
- `check-project-layer.sh` validator structure (active_text guards, work_unit patterns).

## Decisions

See ACTIVE.md Decisions section.
