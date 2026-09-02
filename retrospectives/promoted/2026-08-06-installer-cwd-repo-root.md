# Retrospective: Installer sub-scripts resolve repo root from cwd

- Date: 2026-08-06
- Status: Promoted
- Scope: User-wide
- Session or task: Adaptive Agents upgrade run

## Observation

Running the umbrella installer from outside the Adaptive Agents repository caused the Claude Code, OpenCode, and Antigravity sub-installers to fail with a misleading error.

## Evidence

The umbrella installer derives its repository root from its script location. The affected sub-installers instead preferred the current Git repository, causing invocation from an unrelated repository to select the wrong root.

## Impact

Users running installation from another working directory received a confusing partial failure even though the installer path was valid.

## Scope Decision

- Candidate: User-wide
- Rationale: The installers are user-wide tools intended to be invoked from arbitrary working directories.
- Project Layer considered: Not applicable because this is canonical installer behavior.

## Proposed User-Wide Target

- `scripts/install-claude-code.sh`
- `scripts/install-opencode.sh`
- `scripts/install-antigravity.sh`
- Their focused installer tests

## Promotion Decision

- Status: Promoted
- Decision: Resolve each installer root from its own script location and test invocation from an unrelated Git repository.
- Rationale: The failure is reproducible, the intended repository is unambiguous, and focused regression coverage can falsify the fix.

## Promotion Links

- [Claude Code installer](../../scripts/install-claude-code.sh)
- [OpenCode installer](../../scripts/install-opencode.sh)
- [Antigravity installer](../../scripts/install-antigravity.sh)
- [Claude Code installer tests](../../scripts/test-install-claude-code.sh)
- [OpenCode installer tests](../../scripts/test-opencode.sh)
- [Antigravity installer tests](../../scripts/test-install-antigravity.sh)
