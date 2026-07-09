# Retrospective: Submodule push order and recursion traps

- Date: 2026-07-09
- Status: Captured
- Session or task: Publishing a parent repository and nested submodules after local implementation and testability commits

## Observation

When a repo includes nested submodules, recursive push defaults can fail in misleading ways. The reliable workflow is to push repos intentionally in dependency order and avoid recursive pushes unless nested submodule refs are explicitly aligned.

## Evidence

- Push attempts failed with non-fast-forward and recursive submodule errors while trying to push parent and child repositories in one step.
- Recursive push from one child submodule attempted to push its own nested submodule and blocked publication, even though the immediate target commit for the parent user task was elsewhere.
- Nested submodule state was detached/offset versus expected branch tips, which caused recursive push checks to reject otherwise valid publication steps.
- User feedback explicitly called out submodule handling as incorrect and requested continuation.
- Resolution succeeded after switching to direct, ordered pushes and disabling recursive submodule behavior for the specific push operations.

## Impact

Without a clear submodule publication strategy, agents can enter avoidable push failure loops, waste time on the wrong repository level, and lose user trust at handoff time.

## Proposed Durable Target

Where might this belong if promoted?

- `playbooks/`
- `instructions/`
- `skills/`

## Promotion Decision

- Status: Captured
- Decision: Not promoted yet.
- Rationale: The lesson appears durable, but it should be validated across at least one additional multi-submodule publication session before codifying global push-order rules.

## Promotion Links

Add Markdown links to changed durable guidance files if promoted.

- None yet.

## Dogfood Check

- Check: Re-run this guidance on the next parent-plus-submodule publication task.
- Success criteria: Pushes complete without recursive submodule errors and without switching into repeated diagnostics loops.
- Evidence to collect: sanitized command forms used, summarized submodule status before/after, and whether fallback recursion-disabling was required.
