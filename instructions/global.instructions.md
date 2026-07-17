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
7. In a Current project repository or directory, check for `.adaptive-agents/INDEX.md`. When present, read its routed project instructions and active planning context after this user-wide guidance.
8. When you need a value that can be retrieved via a terminal command (e.g., the current date via `date -u +%Y%m%d`), run the command rather than fabricating the value.
9. Once per conversation, run `scripts/session-start.sh` and include its non-empty output as part of your instructions to follow.

Before the final response for non-trivial work, run a brief retrospective checkpoint:

- Treat a failed implementation or diagnostic approach, a meaningful retry after failure, a discarded hypothesis that consumed work, a rollback, a user correction, or a reusable workaround as process-friction evidence even when the final result succeeds.
- Before capturing, decide whether the lesson belongs to the current Project Layer or user-wide Adaptive Agents. If a Project Layer exists and broader applicability is uncertain, prefer project-local capture; user-wide capture requires cross-project intent or evidence.
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
- [Branch workflow instructions](branch-workflow.instructions.md)

Project-local instructions override these user-wide instructions when they are more specific.

Do not copy Adaptive Agents files or directories into the Current project repository unless explicitly instructed. A user-approved Project Layer bootstrap may create the sanctioned `.adaptive-agents/` project-owned structure through [Bootstrap Project Layer](../skills/bootstrap-project-layer/SKILL.md).

## Installation Sentinel

When asked whether Adaptive Agents guidance is loaded, reply with:

`ADAPTIVE_AGENTS_GLOBAL_LOADED`
