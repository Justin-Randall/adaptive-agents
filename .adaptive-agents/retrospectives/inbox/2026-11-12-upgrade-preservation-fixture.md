# Retrospective: Upgrade Preservation Fixture Boundary

- Date: 2026-11-12
- Status: Captured
- Scope: Undetermined
- Session or task: Multi-agent roles and Project Layer upgrade proof

## Observation

An upgrade test placed project-specific planning guidance outside the section replaced by its simulated merge. The preservation assertion passed even though customization inside the replaced section would have been lost.

## Evidence

Independent review identified the gap in the Project Layer regression fixture. A new assertion with customization inside `Start Work` failed against the original merge and passed after the fixture's merge was narrowed. The focused suite subsequently passed 52 checks.

## Impact

A green preservation test can miss data loss when its distinctive input does not intersect the exact mutation boundary. Review and fixtures should make that boundary observable.

## Scope Decision

- Candidate: Undetermined; capture in this Project Layer first.
- Rationale: The observation arose in this repository's upgrade fixture; broader recurrence has not been established.
- User-wide escalation evidence needed: A similar failure across unrelated projects or explicit user intent for a general practice.

## Proposed Project Target

- Not sure yet; consider project testing guidance after triage.

## Promotion Decision

- Status: Captured
- Decision: No promotion requested.
- Rationale: Preserve the observation for review before changing durable guidance.

## Promotion Links

- None yet.
