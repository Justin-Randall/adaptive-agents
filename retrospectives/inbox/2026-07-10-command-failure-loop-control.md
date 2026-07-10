# Retrospective: Command failure loop control

- Date: 2026-07-10
- Status: Captured
- Scope: User-wide
- Session or task: Non-trivial Go replication fix with coverage gate

## Observation

After the first meaningful command failure, the agent continued trying equivalent command variants instead of switching to a safer diagnostic path. This produced multiple failing terminal invocations, noisy output, and wasted time before a working approach was found.

## Evidence

Sanitized session evidence: after a Go coverage command failed to produce the expected output format, the agent ran three additional variants of the same command (different flags, different output targets) before switching to a different diagnostic approach. Each variant failed in the same way because the root cause was a tool limitation, not a flag choice.

## Impact

Repeated equivalent failures after the first meaningful failure waste session time, produce noisy logs, and delay the actual fix. A retry budget and pivot strategy would reduce wasted iterations and surface the correct diagnostic path sooner.

## Proposed Durable Target

- [instructions/command-failure-pivot.instructions.md](../../instructions/command-failure-pivot.instructions.md)

## Promotion Decision

- Status: Promoted
- Decision: Promote the general retry-budget and pivot behavior to default instructions. Defer a broader command-line tool-pattern skill until there is more repeated evidence for specific tools.
- Rationale: The durable lesson is the cross-tool failure loop: after meaningful command failures, inspect the failure class and pivot diagnostics instead of running equivalent variants. Tool-specific examples for `git`, `go`, `task`, Bash, and PowerShell are useful as examples, but a broad skill would be under-evidenced from this session alone.
