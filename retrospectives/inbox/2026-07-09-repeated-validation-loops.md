# Retrospective: Repeated validation loops after completion

- Date: 2026-07-09
- Status: Captured
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

- Status: Captured
- Decision: Not promoted yet.
- Rationale: The lesson appears durable, but it should be triaged before changing permanent guidance. It may belong in default coding completion discipline, Adaptive Agents maintenance validation guidance, or both.

## Promotion Links

Add Markdown links to changed durable guidance files if promoted.

- None yet.
