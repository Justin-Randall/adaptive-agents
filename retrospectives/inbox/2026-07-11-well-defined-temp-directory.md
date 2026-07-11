# Retrospective: Well-defined temporary directory missing from artifact hygiene rules

- Date: 2026-07-11
- Status: Captured
- Scope: User-wide
- Session or task: OpenCode cleanup follow-up; active plan implementation

## Observation

Temporary and scratch files continue to appear in workspace source directories despite existing temp-artifact-hygiene guidance. The current rules say "prefer paths inside the workspace-approved scratch location" and "never write ad hoc artifacts into source directories" — but they never define a concrete, always-available temp directory for workspaces that lack their own policy. A negative constraint without a positive alternative leads to drift.

## Evidence

- The `temp-artifact-hygiene.instructions.md` references a "workspace-approved scratch or temporary-output location" but never specifies what to use when none exists.
- The temp-artifact-hygiene playbook says "ask once for the preferred location" if none is documented — but during automated work or multi-step tasks, this is easily skipped or forgotten.
- Ad-hoc diagnostic scripts, coverage outputs, and intermediate files have been observed in source directories across multiple sessions.
- The existing `scripts/test-idempotency.sh` created by OpenCode uses `python -c "import tempfile; print(tempfile.mkdtemp())"` — the OS temp dir — which is correct in isolation but inconsistent with the instruction's "ask for a location" approach.

## Impact

- Source tree clutter increases risk of accidental commits of non-source files.
- The current rules provide a negative constraint ("don't put files in source") without a concrete positive fallback, making compliance harder than it should be.
- Without a well-defined default, different agents and tools pick different locations, creating inconsistency.

## Scope Decision

- Candidate: User-wide
- Rationale: The problem is structural in the instruction itself — it applies to any project that lacks its own scratch policy. Defining a portable default temp directory convention benefits all workspaces.
- Project Layer considered: A project could define its own scratch location, but the default fallback should be universal so agents have a consistent answer even before local policy is established.

## Proposed User-Wide Target

- `instructions/temp-artifact-hygiene.instructions.md` — add a concrete default temp directory fallback
- `playbooks/temp-artifact-hygiene.md` — update procedure to use the default when no project-local scratch exists
- `memory/` — add a note about the portable temp directory convention

## Promotion Decision

- Status: Captured
- Decision:
- Rationale:

## Promotion Links

- None yet.
