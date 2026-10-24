# Retrospective: Bootstrap Work Needs Explicit Repository and Shell Context

- Date: 2026-10-24
- Status: Promoted
- Scope: User-wide
- Session or task: Bootstrapping project-owned agent guidance from a separate canonical repository

## Observation

During a project-layer bootstrap, commands and file reads intended for the canonical guidance repository were initially evaluated from the current project workspace. A shell-specific existence check also used syntax incompatible with the active shell. These mismatches caused lookup and command failures before the target repository and shell were made explicit.

## Evidence

- The first directory check failed on shell syntax before making changes.
- Follow-up template reads and searches returned missing-path errors because their relative paths resolved from the project workspace.
- Explicitly using shell-compatible commands and the canonical repository root resolved the lookups, allowing the bootstrap to proceed and validate.

## Impact

Bootstrap workflows commonly cross repository boundaries and may use different shells. Making the target root and active shell explicit before each operation can avoid misleading missing-file results, reduce retries, and keep changes within the intended repository.

## Scope Decision

- Candidate: User-wide
- Rationale: The failure mode applies to agent-assisted setup workflows that operate across a canonical guidance repository and unrelated projects.
- Project Layer considered: The issue concerns cross-repository and shell context management, not the domain behavior of the project being bootstrapped.

## Proposed User-Wide Target

The lesson is implemented in:

- `skills/bootstrap-project-layer/SKILL.md`

## Promotion Decision

- Status: Promoted
- Decision: Add a portable context-discovery preflight to the bootstrap workflow.
- Rationale: The workflow now requires agents to distinguish source and target roots and discover shell/tool context from available evidence before cross-repository reads or commands.

## Promotion Links

- [Bootstrap Project Layer skill](../../skills/bootstrap-project-layer/SKILL.md) — identifies the source root, target root, and execution context before cross-repository bootstrap work.
- [Repository boundary instructions](../../instructions/repository-boundaries.instructions.md) — distinguishes the current project from user-wide Adaptive Agents guidance.
- [Command failure pivot instructions](../../instructions/command-failure-pivot.instructions.md) — selects syntax and command recovery based on the active shell/tool.

---

*Promoted after review; the bootstrap workflow now starts by discovering repository and execution context.*
