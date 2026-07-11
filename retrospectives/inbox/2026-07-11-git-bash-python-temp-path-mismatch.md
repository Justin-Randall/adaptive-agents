# Retrospective: Git Bash test environment and Windows path mismatch

- Date: 2026-07-11
- Status: Captured
- Scope: User-wide
- Session or task: Testing and dogfooding cross-platform installers

## Observation

When running `scripts/test-opencode.sh` from Git Bash, `mktemp -d` creates temp directories under `/tmp/` (the MSYS2 mount). When the test script then calls Windows-native Python (e.g., `python` from the Microsoft Store or official installer), that Python cannot see `/tmp/` paths, causing all JSON validation tests to fail with `FileNotFoundError`. The installer itself works correctly — the generated JSON is valid — but the test harness reports false negatives.

A related failure occurred when an isolated installer test set `HOME` and `USERPROFILE` to a temporary directory. A later dogfood command inherited the temporary home and successfully updated disposable configuration instead of the real user configuration. The command output looked valid until its reported config directory was checked.

## Evidence

1. `mktemp -d` in Git Bash returned paths like `/tmp/tmp.XXXXXX`.
2. Windows Python (`python --version` → Python 3.14.0) could not open `/tmp/tmp.XXXXXX/opencode.json` — `FileNotFoundError` every time.
3. When the temp dir was changed to `$LOCALAPPDATA/Temp` (e.g., `<WINHOME>/AppData/Local/Temp/...`), Python still couldn't open paths using the mixed `/` separator style.
4. Even after switching to a Windows-visible temp dir, passing the path directly into `python -c` caused `SyntaxError: (unicode error) 'unicodeescape' can't decode bytes` — because `<WINHOME>\...` contains `\U` which Python interprets as a Unicode escape in the `-c` string.
5. Fix: convert backslashes to forward slashes (`<WINHOME>/...`) before passing to Python.
6. Even with the right temp path, the instructions test failed because `REPO_ROOT` in Git Bash is `<GITBASH_ROOT>/adaptive-agents` but the installer writes `<WINHOME>/.../adaptive-agents`. The test expected the Git Bash format.
7. All 5 JSON-based tests (valid JSON, sentinel marker, instructions check, path resolution, idempotency) failed despite the config file being perfectly valid.
8. A dogfood installer run reported a temporary config directory even though the intent was to update the real user configuration.
9. Re-running with explicit real-user `HOME` and `USERPROFILE` values updated the intended configuration, and the abandoned temporary home was removed.
10. A direct post-install assertion against the real user files confirmed the import and settings entry were present exactly once.

## Impact

~45 minutes of debugging a non-issue: the installer works, the JSON is valid, the paths are correct. Only the test harness was broken due to cross-environment path mismatches. The false negatives eroded confidence and wasted time.

## Root Cause

Four independent cross-environment issues compounded:

1. **Namespace mismatch**: Git Bash (MSYS2) `/tmp/` is invisible to Windows-native Python.
2. **Unicode escape collision**: Backslash in `<WINHOME>\...` is interpreted as `\U` Unicode escape by Python's `-c` string parser.
3. **Path format mismatch**: Git Bash uses `<GITBASH_ROOT>` (drive-letter mount) but the installer uses `<WINHOME>/...` (Windows-native form with colon).
4. **Environment-state leakage**: A temporary `HOME` or `USERPROFILE` intended for an isolated test can redirect a later installer or validation command while still producing successful-looking output.

## Lesson

When writing Bash test scripts that invoke Windows-native executables (Python, Node, etc.) from Git Bash/MSYS2/Cygwin:

- Do not rely on `mktemp -d` paths — they may live in the POSIX emulation layer.
- Use a temp path that is visible from both environments: e.g., `$LOCALAPPDATA/Temp` on Windows.
- **Always** convert backslashes to forward slashes before passing paths to Python's `-c` string, or `\U`, `\L`, etc. will cause unicode escape errors.
- Be aware that Git Bash path format (`<GITBASH_ROOT>`) differs from Windows-native format (`<WINHOME>/...`). Test expectations must match the format the tool under test actually produces.
- Keep temporary `HOME` and `USERPROFILE` overrides inside a subprocess or restore them before dogfooding user-level installers.
- Treat the installer's reported destination as a verification point; fail the dogfood check if it is not the intended real-user directory.
- Verify the real target files after installation instead of relying only on a successful exit code.
- When a test failure doesn't make sense (valid JSON is "not valid JSON"), suspect a cross-environment path issue before debugging the logic.

## Proposed User-Wide Target

- `playbooks/windows-shell-selection.md` or `instructions/temp-artifact-hygiene.instructions.md` — document cross-environment path normalization and temporary-home isolation for future test scripts.

## Promotion Decision

- Status: Captured
- Decision: Pending triage
- Rationale: The combined failure is reusable across Windows installer tests, but no durable guidance change has been approved.

## Promotion Links

- None yet.
