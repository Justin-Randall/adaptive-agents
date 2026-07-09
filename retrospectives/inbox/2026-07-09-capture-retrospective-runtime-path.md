# Retrospective: Capture retrospective prompt runtime path

- Date: 2026-07-09
- Status: Deferred
- Session or task: `/capture-retrospective` prompt usability and discovery behavior in VS Code

## Observation

Checked-in Adaptive Agents prompt files are useful durable sources, but slash-command discovery may not automatically find prompts placed in the repository top-level `prompts/` directory.

## Evidence

The `capture-retrospective` prompt exists as a checked-in source at `prompts/capture-retrospective.prompt.md`, but runtime invocation clarity was still needed. The session identified practical invocation paths (open prompt file and use the editor play button) and a tooling gap (installer support for user-profile prompt discovery).

## Impact

Without an explicit runtime invocation path, users may assume the prompt is unavailable, reducing adoption of retrospective capture and creating friction in the adaptation cycle.

## Proposed Durable Target

Where might this belong if promoted?

- `prompts/`
- `instructions/`
- `skills/`

## Promotion Decision

- Status: Deferred
- Decision: Deferred.
- Rationale: The prompt is discoverable enough to run from a fresh chat via slash command, so there is no current evidence of a durable runtime-discovery failure. Keep this as a tracked observation until repeat failures show a stable cross-session/runtime gap that warrants durable prompt-runtime guidance.

## Promotion Links

Add Markdown links to changed durable guidance files if promoted.

- None yet.

## Dogfood Result

- Result: Successful
- Evidence: The prompt created this retrospective when run from the prompt file, and it also ran from a fresh chat via slash command.
- Queue-review evidence: The retrospective inbox review prompt was inferred from the natural-language request "review the current retrospective inbox" without using a slash command, and a less capable flash model still produced the expected status summary.
- Boundary check: It did not promote anything or edit durable guidance.
- Next step: Build assisted triage.
- Approved-patch dogfood: Use a tiny approved retrospective update to verify the apply-approved-promotion prompt applies only approved hunks.
