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
6. When a session reveals a recurring lesson, failure mode, preference, or guidance drift, follow the autonomous capture triggers in [adaptation-cycle.md](../playbooks/adaptation-cycle.md); capture or propose only a sanitized `Captured` retrospective unless the user explicitly approves promotion.

Before the final response for non-trivial work, run a brief retrospective checkpoint:

- Treat a failed implementation or diagnostic approach, a meaningful retry after failure, a discarded hypothesis that consumed work, a rollback, a user correction, or a reusable workaround as process-friction evidence even when the final result succeeds.
- If process-friction evidence exists, include a concise retrospective prompt in the completion response: name the evidence in one sentence and ask whether the user wants it captured as a sanitized `Captured` retrospective. Do not silently classify it as no action merely because the task ultimately succeeded.
- If another high-confidence capture trigger fired without process friction, propose or create a sanitized `Captured` retrospective according to repository boundary rules.
- If the evidence is medium-confidence, ask one concise clarifying question before capture.
- If no concrete trigger fired, state the no-capture reason briefly when summarizing completion.
- Never promote a retrospective or edit durable guidance without explicit user approval.

Read:

- [Repository boundary instructions](repository-boundaries.instructions.md)
- [Coding instructions](coding.instructions.md)
- [TDD instructions](tdd.instructions.md)
- [Command failure pivot instructions](command-failure-pivot.instructions.md)
- [Temporary artifact hygiene instructions](temp-artifact-hygiene.instructions.md)

Project-local instructions override these user-wide instructions when they are more specific.

Do not copy Adaptive Agents files or directories into the Current project repository unless explicitly instructed.

## Installation Sentinel

When asked whether Adaptive Agents guidance is loaded, reply with:

`ADAPTIVE_AGENTS_GLOBAL_LOADED`
