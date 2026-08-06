# Retrospective: Test-First Plan Language

- Date: 2026-08-04
- Status: Promoted
- Scope: User-wide
- Session or task: Converting a reviewed feature backlog item into an active implementation plan

## Follow-Up Observation

On 2026-08-05, the same gap was found again in the newly activated catalog plan: Slice 1 mentioned failing tests first, but later slices only described implementation tasks and validation gates. The plan was corrected before implementation began by adding a mandatory test-first workflow and explicit test-first steps to every slice.

## Observation

The active plan specified test coverage, focused validation, and CI commands, but did not explicitly require tests to be written before production implementation. The omission was discovered during plan review when the user asked whether the plan was test-first.

## Evidence

The plan's work slices originally listed implementation tasks followed by test additions and broader validation. No explicit `TDD`, `test-first`, or failing-test-before-implementation rule appeared until the plan was amended after review.

## Impact

A test checklist does not establish test-first execution. Without explicit ordering, an implementation session may write production code first and add tests afterward, weakening the intended feedback loop and making the plan's engineering method ambiguous.

The recurrence shows that a general test approach and a single test-first slice are insufficient. The ordering must be stated as a plan-wide rule and repeated at each slice boundary where implementation begins.

## Scope Decision

- Candidate: User-wide
- Rationale: The gap is in reusable agent planning language and can recur across unrelated implementation plans.
- Project Layer considered: The feature itself is project-specific, but the planning-language lesson applies to any repository where the agent creates an implementation plan.

## Proposed User-Wide Target

Where in the canonical Adaptive Agents repository might this belong if promoted?

- `instructions/` or `skills/`

A durable rule or planning skill should require: focused failing tests first, smallest production change second, focused test rerun third, and broader validation only after the slice passes.

## Promotion Decision

- Status: Promoted
- Decision: Promoted to existing guidance after explicit approval.
- Rationale: The issue recurred across consecutive plan activations and was corrected before implementation. The existing testing and TDD guidance was strengthened with explicit per-slice test-first ordering in the planning conventions.

## Promotion Links

- [Planning conventions](../../instructions/planning-conventions.md)
- [Testing instructions](../../instructions/testing.instructions.md)
- [TDD instructions](../../instructions/tdd.instructions.md)

---

*This note records the original observation and its promotion into durable guidance.*