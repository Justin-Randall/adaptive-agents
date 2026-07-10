---
description: "Use when: applying Adaptive Agents repository boundary rules or deciding where user-wide guidance belongs."
---

# Repository Boundary Instructions

The Adaptive Agents repository is the user-wide guidance repository. A Current project repository is the codebase currently being modified.

When working inside another project:

- Treat Adaptive Agents files as reusable user-wide guidance.
- Read the Current project repository's own local instructions when they exist.
- Check for `.adaptive-agents/INDEX.md` and load its routed project-owned guidance and current planning context after user-wide guidance.
- Let project-local instructions override Adaptive Agents guidance when they are more specific.
- Do not create Adaptive Agents directories or files inside the Current project repository unless explicitly instructed or applying the user-approved Project Layer bootstrap workflow.
- Do not copy `skills/`, `memory/`, `retrospectives/`, `agents/`, `playbooks/`, or `schemas/` into the Current project repository unless explicitly instructed.
- If a durable user-wide lesson should be captured, propose or write it in the Adaptive Agents repository, not the Current project repository.
- If unsure whether a lesson is durable, create or propose a retrospective note before modifying permanent instructions.

## Project Layer Exception

An Adaptive Agents Project Layer is a project-owned `.adaptive-agents/` directory created from the canonical template through [Bootstrap Project Layer](../skills/bootstrap-project-layer/SKILL.md).

- It is not a nested copy of the user-wide Adaptive Agents knowledgebase.
- Bootstrap must interview the user, preview changes, and receive explicit approval.
- The user chooses whether it is tracked, clone-locally excluded, or repository-wide ignored.
- Installed Adaptive Agents guidance discovers it without adding root instruction files or editor settings to the project.
- Project-layer instructions and skills must stay project-specific. Reusable cross-project guidance belongs in this canonical repository.
