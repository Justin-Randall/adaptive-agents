# Windows Shell Selection Playbook

Use this playbook when command execution on Windows includes Bash-oriented scripts, strict shell flags, or mixed shell workflows.

## Goal

Run each command in a compatible shell on the first attempt and pivot quickly when a shell mismatch is detected.

## Procedure

1. Classify the command before execution:
   - Bash-oriented: `.sh` scripts, commands that rely on Bash syntax, or scripts using strict shell flags.
   - Windows-native: PowerShell cmdlets, Windows tooling, and commands documented for PowerShell/cmd.
2. If the command is Bash-oriented and `git` is available, prefer Git Bash as the default shell.
3. If the command is Windows-native, keep PowerShell as the default shell.
4. Run the command once in the selected shell.
5. If failure indicates a shell mismatch (for example `invalid option` from strict shell flags), pivot to a compatible shell before any equivalent retries.
6. Record the failure class and pivot choice in the task summary when this affects diagnostic confidence.

## Guardrails

- Do not keep retrying equivalent commands in the same incompatible shell.
- Keep shell selection scoped to the command category; do not force one shell for all workflows.
- When Git Bash is unavailable, report the fallback shell and proceed with reduced confidence noted.

## Cross-Environment Paths in Tests

- Use a temp dir visible to both environments (`$LOCALAPPDATA/Temp`), not Git Bash's `mktemp -d` (`/tmp` is MSYS2-only).
- Pass Windows paths to `python -c` with forward slashes (`\U` etc. otherwise raise unicode-escape errors).
- Match test expectations to the path format the tool actually produces (Git Bash `/d/...` vs Windows `D:/...`).
- Keep temporary `HOME`/`USERPROFILE` overrides scoped to the isolated subprocess; a leaked temp home makes valid-looking output against the wrong config.
- Verify the real destination files, not just exit codes — the installer's reported directory can be wrong.
