# Retrospective: Git Bash temp dir path mismatch with Windows Python

- Date: 2026-07-11
- Status: Captured
- Scope: User-wide
- Session or task: Implementing and testing scripts/test-opencode.sh

## Observation

When running `scripts/test-opencode.sh` from Git Bash, `mktemp -d` creates temp directories under `/tmp/` (the MSYS2 mount). When the test script then calls Windows-native Python (e.g., `python` from the Microsoft Store or official installer), that Python cannot see `/tmp/` paths, causing all JSON validation tests to fail with `FileNotFoundError`. The installer itself works correctly — the generated JSON is valid — but the test harness reports false negatives.

## Evidence

1. `mktemp -d` in Git Bash returned paths like `/tmp/tmp.XXXXXX`.
2. Windows Python (`python --version` → Python 3.14.0) could not open `/tmp/tmp.XXXXXX/opencode.json` — `FileNotFoundError` every time.
3. When the temp dir was changed to `$LOCALAPPDATA/Temp` (e.g., `<WINHOME>/AppData/Local/Temp/...`), Python still couldn't open paths using the mixed `/` separator style.
4. Even after switching to a Windows-visible temp dir, passing the path directly into `python -c` caused `SyntaxError: (unicode error) 'unicodeescape' can't decode bytes` — because `<WINHOME>\...` contains `\U` which Python interprets as a Unicode escape in the `-c` string.
5. Fix: convert backslashes to forward slashes (`<WINHOME>/...`) before passing to Python.
6. Even with the right temp path, the instructions test failed because `REPO_ROOT` in Git Bash is `<GITBASH_ROOT>/adaptive-agents` but the installer writes `<WINHOME>/.../adaptive-agents`. The test expected the Git Bash format.
7. All 5 JSON-based tests (valid JSON, sentinel marker, instructions check, path resolution, idempotency) failed despite the config file being perfectly valid.

## Impact

~45 minutes of debugging a non-issue: the installer works, the JSON is valid, the paths are correct. Only the test harness was broken due to cross-environment path mismatches. The false negatives eroded confidence and wasted time.

## Root Cause

Three independent cross-environment issues compounded:

1. **Namespace mismatch**: Git Bash (MSYS2) `/tmp/` is invisible to Windows-native Python.
2. **Unicode escape collision**: Backslash in `<WINHOME>\...` is interpreted as `\U` Unicode escape by Python's `-c` string parser.
3. **Path format mismatch**: Git Bash uses `<GITBASH_ROOT>` (drive-letter mount) but the installer uses `<WINHOME>/...` (Windows-native form with colon).

## Lesson

When writing Bash test scripts that invoke Windows-native executables (Python, Node, etc.) from Git Bash/MSYS2/Cygwin:

- Do not rely on `mktemp -d` paths — they may live in the POSIX emulation layer.
- Use a temp path that is visible from both environments: e.g., `$LOCALAPPDATA/Temp` on Windows.
- **Always** convert backslashes to forward slashes before passing paths to Python's `-c` string, or `\U`, `\L`, etc. will cause unicode escape errors.
- Be aware that Git Bash path format (`<GITBASH_ROOT>`) differs from Windows-native format (`<WINHOME>/...`). Test expectations must match the format the tool under test actually produces.
- When a test failure doesn't make sense (valid JSON is "not valid JSON"), suspect a cross-environment path issue before debugging the logic.

## Proposed Project Target

- `playbooks/windows-shell-selection.md` or `scripts/test-opencode.sh` — document the cross-environment path pattern so future test scripts don't hit this.
