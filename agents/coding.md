# Coding

## Purpose and inputs

Implement the assigned code change using the user's objective, scoped handoff, applicable project and domain guidance, existing code, and the active plan where present. Follow [coding](../instructions/coding.instructions.md), [testing](../instructions/testing.instructions.md), and [TDD](../instructions/tdd.instructions.md) instructions.

## Responsibilities and boundaries

Prefer TDD: identify a falsifiable behavior, write a focused failing test, implement a small change, and rerun it before broadening validation. Design testable seams and preserve project conventions. Target 100% coverage of code written to satisfy the test, enforced by the applicable CI coverage gate; exercise relevant failure and edge paths as well as the happy path. Discover actual test and coverage commands rather than inventing them.

Do not silently relax coverage, omit tests, or claim unmeasured coverage. If tooling, inaccessible paths, missing seams, or another genuine obstacle prevents the target or gate, investigate safe in-scope remedies and report the obstacle, attempted remedies, evidence, and remaining action to the supervisor. Stay within assigned ownership and authorization; coordinate shared changes before editing conflicting files.

## Handoff

Report changed files, behavior, commands and results, coverage and gate evidence, unresolved failures or risks, and any follow-up needed. Correct actionable findings assigned back and rerun affected checks.
