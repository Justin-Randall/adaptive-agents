# Retrospective: Repeated validation loops after completion

- Date: 2026-07-09
- Status: Promoted
- Session or task: Adaptive Agents guidance and maintenance workflow review

## Observation

Repeated validation checks can cause agents to keep looping after the requested work is already complete and a focused validation has succeeded.

## Evidence

The user explicitly identified this lesson as worth capturing: repeated validation checks can cause loops after successful completion.

## Impact

This matters because validation should increase confidence, not prevent task closure. Once the requested scope is complete and an appropriate focused check has passed, repeating equivalent checks can waste time, obscure the actual result, and make the agent appear stuck.

## Proposed Durable Target

- `instructions/`
- `skills/`

## Promotion Decision

- Status: Promoted
- Decision: Promoted to existing durable guidance.
- Rationale: The lesson is durable because it applies across coding and guidance-maintenance tasks. Existing instructions already cover the desired behavior: stop after the requested scope is complete and a focused validation has succeeded, and avoid rerunning equivalent checks unless new work, new evidence, or a user request justifies it.

## Promotion Links

Add Markdown links to changed durable guidance files if promoted.

- [Coding instructions](../../instructions/coding.instructions.md)
- [Update Adaptive Agents skill](../../skills/update-adaptive-agents/SKILL.md)
