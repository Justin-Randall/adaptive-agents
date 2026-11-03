# Retrospective: Windows Git Bash Resolution

- Date: 2026-11-03
- Status: Captured
- Scope: User-wide
- Session or task: Running Python and shell validation from Windows PowerShell.

## Observation

Bare `bash` calls from PowerShell selected a WSL launcher rather than Git Bash.
Backslash-separated script arguments were consumed as Bash escapes, and WSL
could not run the CRLF shell scripts. A Python test intended to locate Git Bash
from `git.exe` also selected the wrong parent directory, so it tried to launch
a nonexistent executable. Identifying the actual launcher and checking its
derived path exposed and resolved the test's off-by-one path calculation.

## Evidence

- `bash .\scripts\...` did not preserve the Windows path. Running through WSL
  showed a `/mnt/...` working directory and failed on a CRLF script with a
  `bash\r` interpreter error. `cygpath` was unavailable in PowerShell.
- The verified Git for Windows layout placed `git.exe` under `Git\cmd` and
  `bash.exe` under `Git\bin`. The test's original `git_path.parents[2]`
  calculation pointed above the installation. Changing it to `parents[1]`
  worked with that executable location, but the full health check still failed:
  Python launched from Git Bash resolved `git.exe` under
  `Git\mingw64\bin`, so one fixed parent index was not reliable.
- Inspecting `shutil.which("git")` from both PowerShell and Git Bash exposed the
  differing executable paths. The final test walks the Git executable's
  ancestors and selects the first existing `bin\bash.exe`. The instruction-load
  budget suite then passed all 31 tests; the Project Layer validator suite
  passed 43 tests, the direct Project Layer check reported zero failures, and
  the focused Markdown dogfood suite passed seven tests.
- The complete Adaptive Agents health check passed 278 checks with zero
  failures and one existing Claude Code entrypoint warning.
- A similar but distinct Bash-wrapper failure is recorded in
  [the October 24 retrospective](2026-10-24-project-layer-validator-bash-wrapper-failure.md);
  its cause was not established by this session.

## Impact

Using an unidentified shell can turn a valid check into a misleading launch or
path failure. Retrying equivalent commands wastes time, while bypassing a
wrapper can leave shell integration unverified. Confirm the executable before
running Bash-oriented checks, and verify any path derived from `git.exe` exists
before a Python subprocess test relies on it.

## Scope Decision

- Candidate: User-wide
- Rationale: The user reports this class of shell-selection problem across
  projects and explicitly requested a system-level capture. A related
  user-wide Bash-wrapper observation is already in the inbox.
- Project Layer considered: The current Project Layer instruction change is
  project-specific; it does not cover command-shell selection across unrelated
  repositories.

## Proposed User-Wide Target

- `instructions/command-failure-pivot.instructions.md` — review whether the
  existing Windows shell-selection guidance should be surfaced before the
  first Bash invocation, and whether Python shell-test helpers need a reusable
  verified-path pattern.

## Promotion Decision

- Status: Captured
- Decision: Capture only; no durable guidance promotion was approved.
- Rationale: The local test-path defect is fixed, but broader guidance changes
  should be considered during triage alongside the existing related note.

## Promotion Links

- None yet.

## Resolution

- Status: Pending verification
- Evidence: The test now discovers Git Bash across both observed Git for
  Windows executable layouts, all 31 instruction-load budget tests pass, and
  the complete repository health check passes. Cross-project guidance has not
  been triaged or changed.

---

*After triage, move this note to `promoted/`, `deferred/`, or `rejected/` and update its status and promotion links.*
