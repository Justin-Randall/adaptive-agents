---
description: "Use when: changing production behavior, adding tests, fixing bugs, or planning test-driven work."
---

# TDD Instructions

The authoritative testing contract is [Testing instructions](testing.instructions.md).

Prefer test-driven development for production code changes.

Plans must define the test approach before implementation: a `Test approach` line in the backlog item and a `## Test Plan` in ACTIVE.md.

For non-trivial behavior changes:

- Start from a failing behavior, failing test, named file, symbol, or nearby implementation surface.
- Add or identify the cheapest focused check that can falsify the intended behavior.
- Make small, reversible changes.
- Run the focused check after the first substantive edit when the environment provides one.
- Broaden validation only when the change touches shared behavior, cross-module contracts, or user-facing workflows.
- Do not fix unrelated bugs or broken tests unless explicitly asked.
