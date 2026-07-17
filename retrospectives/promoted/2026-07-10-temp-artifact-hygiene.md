# Retrospective: Temporary artifact hygiene against workspace policy

- Date: 2026-07-10
- Status: Promoted
- Scope: User-wide
- Session or task: Non-trivial Go replication fix with coverage gate

## Observation

Intermediate diagnostic and coverage artifacts were created outside the active workspace's designated scratch or temporary-output directory, and some were not cleaned up after the task completed.

## Evidence

Sanitized session evidence: coverage HTML output, function-level coverage text, and other intermediate files were created in the source directory rather than in the project's designated scratch or temp location. The workspace's local instructions explicitly required routing all ad hoc outputs to a specific scratch directory and cleaning up afterward. This policy was not followed.

## Impact

Artifacts left outside designated scratch locations risk accidental commit noise, workspace clutter, and confusion about which files are source-controlled. Consistent hygiene reduces these risks and aligns with project-local conventions.

## Proposed Durable Target

- `instructions/`
- `playbooks/`

## Promotion Decision

- Status: Promoted
- Decision: Promote with focused durable updates in `instructions/` and `playbooks/`.
- Rationale: Existing durable guidance mentioned scratch output only as one command-failure pivot tactic, which was too narrow for repeated artifact hygiene misses. The lesson is recurring and cross-project, so it now has a dedicated default instruction and an operational playbook.

## Promotion Links

- [instructions/temp-artifact-hygiene.instructions.md](../../instructions/temp-artifact-hygiene.instructions.md)
- [playbooks/temp-artifact-hygiene.md](../../playbooks/temp-artifact-hygiene.md)
- [instructions/global.instructions.md](../../instructions/global.instructions.md)
- [INDEX.md](../../INDEX.md)
