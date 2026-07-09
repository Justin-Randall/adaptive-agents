---
description: "Use when: applying Adaptive Agents repository boundary rules or deciding where user-wide guidance belongs."
---

# Repository Boundary Instructions

The Adaptive Agents repository is the user-wide guidance repository. A Current project repository is the codebase currently being modified.

When working inside another project:

- Treat Adaptive Agents files as reusable user-wide guidance.
- Read the Current project repository's own local instructions when they exist.
- Let project-local instructions override Adaptive Agents guidance when they are more specific.
- Do not create Adaptive Agents directories or files inside the Current project repository unless explicitly instructed.
- Do not copy `skills/`, `memory/`, `retrospectives/`, `agents/`, `playbooks/`, or `schemas/` into the Current project repository unless explicitly instructed.
- If a durable user-wide lesson should be captured, propose or write it in the Adaptive Agents repository, not the Current project repository.
- If unsure whether a lesson is durable, create or propose a retrospective note before modifying permanent instructions.
