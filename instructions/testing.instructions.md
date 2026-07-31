---
description: "Use when: planning, writing, or validating tests; choosing a test methodology; or setting up CI."
---

# Testing Instructions

Tests are a first-class planning artifact: backlog items carry a `Test approach` line and `ACTIVE.md` carries a `## Test Plan` before implementation.

- **Falsifiable proof** — every test proves a named behavior works; state what each test falsifies.
- **Failure paths** — test the happy path and the error, edge, and failure paths.
- **Tests before feature work** — write focused failing tests first; use what they surface (seams, mocks, injection needs, testability gaps) to drive early strategy: abstraction, interfaces, factories, injection.
- **Coverage** — 100% of the code written to satisfy the test is covered, enforced by a CI coverage gate.
- **Fast tests** — prefer fast unit-level checks in the focused loop; keep CI within a time budget.
- **Methodology** — use the language-appropriate methodology (BDD, TDD, SDD) and standard test framework; discover them from project conventions and language docs; record the choice in the Test Plan.
- **CI** — the project should run tests in CI with the coverage gate. If none exists, ask whether to include CI in scope or defer it to the backlog.

Deeper context:

- [TDD instructions](tdd.instructions.md)
- [Test Planning conventions](planning-conventions.md)
- Language test-framework and methodology documentation.
