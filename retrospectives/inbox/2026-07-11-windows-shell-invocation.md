# 2026-07-11: Windows Shell Invocation Friction

- Status: Captured
- Scope: User-wide
- Captured: 2026-07-11

## Observation

Running `.sh` scripts directly via `& "path\to\script.sh"` in PowerShell fails silently — Windows opens the `.sh` file with its associated editor (notepad/npp) instead of executing it. The exit code may appear as success (0) but the script never actually ran.

## Impact

Wasted retries, no output to diagnose, false confidence that validation passed.

## Root Cause

`.sh` is not a recognized executable extension on Windows. PowerShell's `&` operator launches the file-associated app, not a shell interpreter. Git Bash (or WSL) must be explicitly invoked: `bash scripts/foo.sh`.

## Recommendation

When running `.sh` workflows on Windows:
- Use `bash scripts/check-adaptive-agents.sh` (Git Bash) explicitly.
- Verify Git Bash is on PATH before invoking.
- If the script has `set -euo pipefail`, ensure the shell supports it (Git Bash does; PowerShell wrapper shells may not).
- Never assume `& "path\to.sh"` works — always use `bash path\to.sh`.

## Evidence

- Three consecutive attempts to run `check-adaptive-agents.sh` via `&` produced zero output and zero error.
- Each invocation appeared to succeed (exit code 0 in some shells) but the script never ran.
- The `install-opencode.sh` and `install-vscode.sh` scripts likely have the same issue.
