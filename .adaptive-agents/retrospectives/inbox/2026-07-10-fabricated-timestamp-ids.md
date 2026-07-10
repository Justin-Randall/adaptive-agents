# Retrospective: Fabricated timestamp IDs

- Date: 2026-07-10
- Status: Promoted
- Scope: User-wide
- Session or task: Adding OpenCode backlog item (PL-20260710)

## Observation

When creating a backlog file that requires a UTC timestamp ID, the agent fabricated `PL-20260710T190000Z` (since changed to date-only `PL-YYYYMMDD` format) instead of getting the actual current time from the terminal. The off-by-~3.5-hour error was caught by the user, who asked how the timestamp was generated. The agent then corrected it using `date -u`.

## Evidence

1. The agent created `PL-20260710T190000Z-opencode-installer-support.md` (since renamed to date-only `PL-20260710-opencode-installer-support.md`) without running `date -u` first.
2. When asked, the agent acknowledged the guesswork and immediately corrected to `PL-20260710T152450Z` (since further simplified to `PL-20260710`) after running the actual command.

## Impact

Fabricated timestamps undermine the collision-resistance property of the plan ID scheme and introduce silently wrong metadata. The `manage-planning` skill describes creating new plans but the agent should get the date from the terminal via `date -u +%Y%m%d` rather than fabricating it.

## Scope Decision

- Candidate: User-wide
- Rationale: Determining the current date or time is not project-specific — it applies to timestamps, log messages, build tags, commit messages, and other common coding tasks. The lesson about verifying time by running a command rather than fabricating it belongs in user-wide engineering guidance, not in a single skill.
- Project Layer capture note: The immediate trigger was a Project Layer planning operation, but the underlying failure pattern (fabricating a value that can be retrieved via a terminal command) is general.

## Proposed Project Target

- `instructions/global.instructions.md` — add a concrete example to the verification discipline: "When you need the current date or time, run `date -u +%Y%m%d` (or similar) rather than fabricating it."
