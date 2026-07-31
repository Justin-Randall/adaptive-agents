# PL-20260731: Claude Code Entrypoint Health Check False-Negative

- Status: Backlog
- Readiness: Needs refinement
- Created: 2026-07-31
- Test approach: verify the health check passes on a correctly installed integration and fails on a genuinely missing import

## Objective

Fix `check-adaptive-agents.sh` `check_claude_code` so it correctly validates the installed native entrypoint import regardless of path format (Git Bash `@/d/...` vs Windows `@D:/...`), eliminating the false "does not import" warning on a correctly configured integration.

## Problem Spec

The Claude Code integration is installed with a native import `@/d/github.com/Justin-Randall/adaptive-agents/AGENTS.md` (Git-Bash form) inside the `#==ADAPTIVE_AGENTS_START==` delegation block, and the Claude Code support plan (PL-20260711) verified it loads. But the live health check warns `Claude Code CLAUDE.md does not import @D:/github.com/...AGENTS.md` because `check_claude_code` matches the exact string `@$REPO_ROOT/AGENTS.md` (Windows form `D:/...`) against the file. Reproduced: `grep -Fxq "@D:/...AGENTS.md"` returns NO MATCH while the native import line exists. Verification must accept the canonical path in either normalized form, or the checker should resolve the path before comparing.

## Scope

1. Make the import check path-format tolerant (normalize drive letter case, leading-slash `/d/` vs `D:/` forms).
2. Keep the delegation-section check and the settings grant check unchanged.
3. Add/extend a focused test for the path-form mismatch (temp-dir config, matching the installer-duties contract).
4. Re-run the health check; the Claude Code warning must become a PASS on this machine.

## Out of Scope

- Changing the installer's written path format.
- Other tools' health checks (same pattern applies only if it recurs).
