---
applyTo: "**"
---

# Global User-Wide Instructions

These are the default user-wide instructions for non-trivial coding work.

Before making changes:

1. Follow the repository boundary rules.
2. Apply the general coding standards.
3. Prefer test-driven development when changing production behavior.
4. Load task-specific skills from `skills/` only when relevant.
5. When modifying Adaptive Agents guidance, load [Update Adaptive Agents](../skills/update-adaptive-agents/SKILL.md).

Read:

- [Repository boundary instructions](repository-boundaries.instructions.md)
- [Coding instructions](coding.instructions.md)
- [TDD instructions](tdd.instructions.md)

Project-local instructions override these user-wide instructions when they are more specific.

Do not copy Adaptive Agents files or directories into the Current project repository unless explicitly instructed.

## Installation Sentinel

When asked whether Adaptive Agents guidance is loaded, reply with:

`ADAPTIVE_AGENTS_GLOBAL_LOADED`
