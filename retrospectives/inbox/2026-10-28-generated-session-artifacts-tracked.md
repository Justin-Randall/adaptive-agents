# Retrospective: Generated session artifacts were tracked by source control

- Date: 2026-10-28
- Status: Captured
- Scope: User-wide
- Session or task: Total Recall dogfood and cleanup

## Observation

A compact-session dogfood directory was created inside a project workspace and was not treated as disposable runtime output. Its session graph, locks, map, event records, indexes, ledger, and manifest were tracked by Git and persisted in repository history. Cleanup therefore required deleting the generated directory and reviewing a source-control deletion.

## Evidence

Git path inspection showed that the generated session artifacts were tracked rather than ignored. The artifact set consisted of session maps, locks, and generated graph records rather than hand-authored project source.

## Impact

Agent dogfood can pollute any project that uses Adaptive Agents, create noisy commits, expose session content in source control, and make cleanup easy to miss. Generated session state should be written outside tracked project trees by default, or an explicit ignore rule should be installed before dogfood begins. Cleanup should verify both filesystem absence and Git tracking status.

## Scope Decision

- Candidate: User-wide
- Rationale: The failure mode applies to every project and harness that uses Adaptive Agents dogfood or generated session artifacts.
- Project Layer considered: Insufficient; this is a cross-project storage and source-control hygiene concern.

## Proposed User-Wide Target

If promoted, consider a focused artifact-hygiene playbook or instruction, plus installer/storage guidance defining where generated session state belongs and how project-local exclusions are established.

## Promotion Decision

- Status: Captured
- Decision: Await triage and explicit approval before promotion.
- Rationale: The observation is clear and user-wide, but the durable remedy—global storage, project-local ignored storage, or both—needs design review.

## Promotion Links

- None yet.

## Resolution

- Status: Pending verification
- Evidence: The offending generated directory was removed from the worktree; prevention has not yet been implemented.

---

*After triage, move this note to `promoted/`, `deferred/`, or `rejected/` and update its status and promotion links.*
