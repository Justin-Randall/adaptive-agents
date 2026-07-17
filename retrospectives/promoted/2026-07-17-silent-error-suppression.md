# Retrospective: Do not silently suppress errors; let them surface

- Date: 2026-07-17
- Status: Promoted
- Scope: User-wide
- Session or task: Implementing `scripts/session-start/check-upgrade.sh`

## Observation

Code used `|| true` in shell and `2>/dev/null` to suppress command failures, which hid the fact that a derived file path was never validated before reading. The error suppression made the bug invisible — the code appeared to work because the failure was swallowed, not because the logic was correct. A future refactor that removes the suppression would introduce a regression with no obvious connection to the change.

## Evidence

1. `"$(cat "$REFUSAL_FILE" 2>/dev/null)" || true` — the `|| true` swallows all failure modes (missing file, missing directory, permission denied, corrupt content).
2. The missing-directory bug was only caught during human review, not by testing or error output, because the suppression made it asymptomatic in normal operation.
3. The same pattern appears across languages: empty `catch` blocks in TypeScript/Python/Java, `void` casts in C#, `On Error Resume Next` in VB, or bare `except:` that catches and discards everything.
4. In each case, the suppression hides not just the anticipated failure but also unexpected ones (wrong path, wrong permissions, wrong data format).

## Impact

Silent error suppression makes bugs harder to find, harder to diagnose, and easier to reintroduce during refactoring. A suppressed error may be correct for one specific case (e.g., "this file is optional") but will mask every other failure mode for that operation. Errors should be handled explicitly — decide what to do with each failure mode rather than silencing everything and hoping for the best.

## Scope Decision

- Candidate: User-wide
- Rationale: Error handling discipline applies across all languages, tools, and platforms.
- Project Layer considered: This is a general coding practice, not specific to any project.

## Proposed User-Wide Target

`instructions/coding.instructions.md` — the existing coding standards now include a rule against silent error suppression, promoted alongside the related path-validation rule.

## Promotion Decision

- Status: Promoted
- Decision: Promoted to existing guidance
- Rationale: The lesson is concrete, cross-language, and complements the path-validation rule promoted from the same session. Both rules address the same underlying fragility from different angles.

## Promotion Links

- [Coding instructions](../../instructions/coding.instructions.md)
