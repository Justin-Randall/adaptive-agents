# Retrospective: Windows bash wrapper breaks strict shell validation

- Date: 2026-07-10
- Status: Promoted
- Scope: User-wide
- Session or task: Upgrading a project-owned Adaptive Agents Project Layer and validating with the layer checker.

## Observation

A shell validation step failed when invoked through the default Windows bash command. The same checker succeeded when run through a full Bash implementation.

## Evidence

A validator script that starts with strict shell flags failed immediately under the default Windows bash wrapper. The agent pivoted to an alternate Bash executable and the same script completed successfully with zero failures.

## Impact

This can cause false-negative tooling failures during setup, upgrade, and validation workflows. Without a quick pivot, agents may misdiagnose template quality, repeat failing commands, or stall progress.

## Scope Decision

- Candidate: User-wide
- Rationale: The failure mode is environment/tooling-specific and can recur across unrelated repositories whenever shell scripts are run on Windows systems with a wrapper bash in PATH.
- Project Layer considered: Project-local guidance is insufficient because the issue is not tied to one repository's code or conventions.

## Proposed User-Wide Target

Where in the canonical Adaptive Agents repository might this belong if promoted?

- `instructions/`
- `playbooks/`

## Promotion Decision

- Status: Promoted
- Decision: Promoted to command-failure instruction guidance plus a dedicated Windows shell selection playbook.
- Rationale: The failure mode is cross-project and recurring on Windows when Bash wrappers are used for strict shell scripts.

## Promotion Links

Add Markdown links to changed durable guidance files if promoted.

- [instructions/command-failure-pivot.instructions.md](../../instructions/command-failure-pivot.instructions.md)
- [playbooks/windows-shell-selection.md](../../playbooks/windows-shell-selection.md)
- [INDEX.md](../../INDEX.md)
