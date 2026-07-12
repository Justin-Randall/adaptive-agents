# PL-20260712-branch-development-guidance Memory

Curated cross-session context for the Branch Development Guidance work unit.

## Status

Spec completed — 2026-07-12. All promotion patches applied, validation passes. Branch not yet merged (awaiting user dogfooding before PR).

## Key Context

- `main` is documented as protected in `README.md` line 74.
- This work unit is self-applying its own guidance: created on branch `pl-branch-development-guidance`, will PR back to `main`.
- Branch protection could not be verified via GitHub API (no auth available). The README documentation is the reliable signal.

## Decisions

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-07-12 | Place branch guidance in `.adaptive-agents/instructions/branch-workflow.md` | Project-layer instruction, not user-wide; repo-scoped conventions belong in project layer |
| 2026-07-12 | Use branch name `pl-branch-development-guidance` (short slug, not full work-unit ID) | Shorter branch names are easier to type and reference; the full work-unit ID is documented in ACTIVE.md |
| 2026-07-12 | Detection heuristics prefer local file reads over API calls | API requires auth and is unreliable; README/CONTRIBUTING/.github/ checks are free and deterministic |
| 2026-07-12 | Promote branch workflow to user-wide guidance | User explicitly requested a proposed change to Adaptive Agents; the lesson is repo-agnostic and durable |
| 2026-07-12 | Forge-agnostic approach (not GitHub-specific) | User works with GitLab too; `gh` not installed on this system. Instruction must work across forges |
| 2026-07-12 | Automerge-ready is the goal, not CLI automation | Branch state (synced, validated, clean commit) matters more than which tool creates the PR/MR. PR description must be easy for a human to approve in one read |
| 2026-07-12 | Local commits encouraged, squash before PR/MR | Local commits provide checkpoints and revert points. Only the cleaned feature delivery reaches the primary branch |

## Deferred Discoveries

- Could extend this guidance later with a `scripts/check-branch-protection.sh` helper that reads protection status from available sources and exits with a clear recommendation. Not in current scope.
