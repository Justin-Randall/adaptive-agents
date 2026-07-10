# Retrospective: Fabricated timestamp IDs

- Date: 2026-07-10
- Status: Promoted
- Scope: User-wide
- Session or task: Adding OpenCode backlog item (PL-20260710T152450Z)

## Observation

When creating a backlog file that requires a UTC timestamp ID, the agent fabricated `PL-20260710T190000Z` instead of getting the actual current time from the terminal. The off-by-~3.5-hour error was caught by the user, who asked how the timestamp was generated. The agent then corrected it using `date -u`.

## Evidence

1. The agent created `PL-20260710T190000Z-opencode-installer-support.md` without running `date -u` first.
2. When asked, the agent acknowledged the guesswork and immediately corrected to `PL-20260710T152450Z` after running the actual command.

## Impact

Fabricated timestamps undermine the collision-resistance property of the ISO 8601 ID scheme and introduce silently wrong metadata. The `manage-planning` skill describes creating new plans but doesn't explicitly say "get the timestamp from the terminal via `date -u +PL-%Y%m%dT%H%M%SZ`". Without that instruction, an agent may guess instead of measuring.

## Scope Decision

- Candidate: User-wide
- Rationale: Determining the current date or time is not project-specific — it applies to timestamps, log messages, build tags, commit messages, and other common coding tasks. The lesson about verifying time by running a command rather than fabricating it belongs in user-wide engineering guidance, not in a single skill.
- Project Layer capture note: The immediate trigger was a Project Layer planning operation, but the underlying failure pattern (fabricating a value that can be retrieved via a terminal command) is general.

## Proposed Project Target

- `instructions/global.instructions.md` — add a concrete example to the verification discipline: "When you need the current date or time, run `date -u +%Y%m%dT%H%M%SZ` (or similar) rather than fabricating it."
