# Retrospective: Handle missing file paths appropriately

- Date: 2026-07-17
- Status: Promoted
- Scope: User-wide
- Session or task: Implementing `scripts/session-start/check-upgrade.sh`

## Observation

Code referenced a path derived from a cache directory but did not validate that the parent directory exists before attempting to read the file. The error was silently swallowed by a shell `|| true` guard, but the pattern assumes a path that no part of the code ensures exists. The directory is only created later by a different part of the system (the agent writing a decline hash) — on first run, it does not exist.

This is not a shell-specific problem. The same mistake appears in any language when code reads from a computed path without first checking whether the path (or its parent directory) actually exists, or handling the absence explicitly.

## Evidence

1. Code set a derived path variable and immediately tried to read from it. No check that the parent directory exists.
2. The only guard was a language-level "suppress error" operator (`|| true` in shell), which silently swallows all failure modes.
3. First-run behavior worked only by accident (the read failed, the code continued), but the assumption was invisible — a future refactor removing the guard would break on systems without the directory.
4. The oversight was caught during review: "I do not see anywhere the CACHE_DIR is validated or created."
5. The same pattern appears across languages — `File.ReadAllText(path)` without `File.Exists(path)`, `open(path)` without `os.path.exists(path)`, `cat path` without checking the parent first.

## Impact

This specific case happened to work due to a `|| true` guard, but the pattern is a general programming fragility. Code that reads from a derived path should validate whether the path exists first, then handle the absence in a way that is appropriate for the task — whether that means creating it, skipping the read, returning a default, or reporting an error. The right behavior depends on the context; the mistake is not considering the question at all. This applies equally to shell scripts, Python, TypeScript, Go, Rust, and any other language that interacts with the file system.

For example, if a tool needs to write to a directory and it does not exist, it might be appropriate to create that directory first. If a tool reads from a cache that may not have been populated yet, skipping the read silently is likely correct. The error is not the choice — the error is writing code that assumes a path exists without ever checking.

## Scope Decision

- Candidate: User-wide
- Rationale: File-read safety — validating paths before reading and handling absence appropriately — is a general programming practice that applies across all languages, tools, and platforms.
- Project Layer considered: The failure is a general coding practice, not specific to any project or tool.

## Promoted User-Wide Target

`instructions/coding.instructions.md` — the existing coding standards could add a rule about validating file paths before reading and handling missing paths appropriately for the context.

## Promotion Decision

- Status: Promoted
- Decision: Promoted to existing guidance
- Rationale: The lesson is concrete, cross-language, and fills a gap in the existing coding standards. The same pattern recurs — a companion retrospective captures the related silent-suppression case.

## Promotion Links

- [Coding instructions](../../instructions/coding.instructions.md)
