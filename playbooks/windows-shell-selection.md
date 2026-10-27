# Windows Shell Selection Playbook

Use this playbook when command execution on Windows includes Bash-oriented scripts, strict shell flags, or mixed shell workflows.

## Goal

Run each command in a compatible shell on the first attempt and pivot quickly when a shell mismatch is detected.

## Procedure

1. Classify the command before execution:
   - Bash-oriented: `.sh` scripts, commands that rely on Bash syntax, or scripts using strict shell flags.
   - Windows-native: PowerShell cmdlets, Windows tooling, and commands documented for PowerShell/cmd.
2. If the command is Bash-oriented, resolve the shell implementation before running it:
   - `C:\Windows\System32\bash.exe` is the WSL launcher, not Git Bash. Do not use it as a Bash implementation for repository scripts.
   - When Git is installed, derive the Git Bash executable from the resolved `git.exe` installation (normally the sibling `bin\bash.exe`) and select that executable explicitly in the command runner.
   - Do not invoke a bare `bash` from PowerShell unless its resolved command is verified to be Git Bash or another known Bash implementation.
3. If the command is Windows-native, keep PowerShell as the default shell.
4. Run the command once in the selected shell.
5. If the launcher reports `Access is denied`, `Bash/E_ACCESSDENIED`, or fails before printing the script's own output, classify it as a launcher/environment failure. Do not retry the same command through the same `bash` path; select the verified Git Bash executable or use a non-Bash diagnostic path.
6. If failure indicates a shell mismatch (for example `invalid option` from strict shell flags), pivot to a compatible shell before any equivalent retries.
7. Record the failure class and pivot choice in the task summary when this affects diagnostic confidence.

## Guardrails

- Do not keep retrying equivalent commands in the same incompatible shell.
- Keep shell selection scoped to the command category; do not force one shell for all workflows.
- When Git Bash is unavailable, report the fallback shell and proceed with reduced confidence noted.

## Invoking .sh Scripts

- Never invoke a `.sh` script with PowerShell's `&` operator — Windows opens the file's associated editor and the script never runs (the exit code can still be 0).
- Resolve and confirm the Git Bash executable first. On Windows PowerShell, inspect `Get-Command git.exe` and derive the Git installation's `bin\bash.exe`; then pass that full path as the command runner's shell when supported. If the runner cannot select a shell and bare `bash` resolves to the WSL launcher, do not retry the script through bare `bash`; report the unavailable Git Bash path and use an equivalent native diagnostic or stop with validation marked pending.

## Cross-Environment Paths in Tests

- Use a temp dir visible to both environments (`$LOCALAPPDATA/Temp`), not Git Bash's `mktemp -d` (`/tmp` is MSYS2-only).
- Pass Windows paths to `python -c` with forward slashes (`\U` etc. otherwise raise unicode-escape errors).
- Match test expectations to the path format the tool actually produces (Git Bash `/d/...` vs Windows `D:/...`).
- Keep temporary `HOME`/`USERPROFILE` overrides scoped to the isolated subprocess; a leaked temp home makes valid-looking output against the wrong config.
- Verify the real destination files, not just exit codes — the installer's reported directory can be wrong.
