# Retrospective: Duplicate backlog item created despite existing item

- Date: 2026-07-11
- Status: Captured
- Scope: Agent-wide
- Session or task: Adding OpenCode to backlog (PL-20260710)

## Observation

When asked to add an OpenCode feature to the backlog, the agent scanned the existing backlog, saw `PL-20260710-opencode-installer-support.md`, but incorrectly classified it as "narrowly about installer scripts" and created a new, broader item. The agent should have stopped, flagged the existing item, and asked the user whether to work with the existing one instead.

## Evidence

1. The backlog index listed `PL-20260710-opencode-installer-support.md` (Ready) before the agent acted.
2. The agent created `PL-20260711-opencode-support.md` with a broader scope description.
3. The user called this out: "I did not see the existing backlog item. Go ahead and revert [...] why did you not stop and let me know there was an item that already exists that might be the same feature?"

## Impact

Wasted effort creating and reverting a file. More importantly, eroded trust — the user had to correct the agent on something the agent had already read.

## Root Cause

The agent applied a narrow interpretation of the existing item ("installer scripts only") and convinced itself the new item was different enough, rather than treating overlap as a stop-and-ask signal.

## Lesson

When asked to create a new plan/feature/backlog item, scan existing items first. If *any* existing item overlaps in topic — even if the new request seems broader or more specific — stop, present the overlap, and ask the user whether to work with the existing item or create a new one. Let the user decide.

## Proposed Project Target

- `instructions/global.instructions.md` — add a concrete rule: "When asked to create a new plan, feature, backlog item, or similar artifact, check whether existing items already address the request. If overlap exists, present it to the user and ask before duplicating."
