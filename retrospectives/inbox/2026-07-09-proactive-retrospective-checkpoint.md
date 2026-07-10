# Retrospective: Proactive retrospective checkpoint

- Date: 2026-07-09
- Status: Promoted
- Session or task: Agent process-quality review after a non-trivial coding session

## Observation

The agent completed a non-trivial technical task but did not proactively identify capture-worthy process failures, then initially reported only that no retrospective had been captured instead of assessing whether one should have been proposed.

## Evidence

Sanitized session evidence included repeated command/tool attempts after failures, temporary diagnostic artifacts created outside the active workspace's expected scratch or temporary-output policy, and explicit user feedback that these issues should have triggered retrospective capture.

## Impact

Without an explicit completion-time retrospective checkpoint, agents can finish technically successful work while missing reusable learning about their own process failures. This weakens the adaptation loop and makes capture behavior inconsistent.

## Proposed Durable Target

- `instructions/`
- `playbooks/`
- `skills/`
- `prompts/`

## Promotion Decision

- Status: Promoted
- Decision: Add a mandatory completion-time retrospective checkpoint and align capture triggers, confidence tiers, update guidance, and end-of-session prompt output.
- Rationale: The issue is reusable across future sessions, supported by concrete user feedback, and affects the default agent workflow rather than a project-specific implementation detail.

## Promotion Links

- [Global user-wide instructions](../../instructions/global.instructions.md)
- [Coding instructions](../../instructions/coding.instructions.md)
- [Adaptation cycle](../../playbooks/adaptation-cycle.md)
- [Update Adaptive Agents](../../skills/update-adaptive-agents/SKILL.md)
- [End-of-session capture prompt](../../prompts/end-of-session-capture.prompt.md)
