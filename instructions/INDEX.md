# Instructions

This directory contains durable user-wide rules for coding agents.

Use instruction files for behavior that should apply predictably across sessions, such as repository boundaries, coding standards, command failure handling, test discipline, or temporary artifact hygiene.

## Routing

- [global.instructions.md](global.instructions.md) is the default entrypoint for non-trivial work.
- [repository-boundaries.instructions.md](repository-boundaries.instructions.md) defines Adaptive Agents versus current-project ownership.
- [coding.instructions.md](coding.instructions.md) defines implementation standards.
- [tdd.instructions.md](tdd.instructions.md) defines behavior-change validation expectations.
- [command-failure-pivot.instructions.md](command-failure-pivot.instructions.md) defines shell failure retry discipline.
- [temp-artifact-hygiene.instructions.md](temp-artifact-hygiene.instructions.md) defines diagnostic artifact cleanup expectations.
- [branch-workflow.instructions.md](branch-workflow.instructions.md) defines branch and commit workflow preferences.
