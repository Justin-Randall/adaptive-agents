# Temporary Artifact Hygiene Playbook

Use this playbook when a task needs temporary files for diagnostics, command output capture, parsing, or manual inspection.

## Goal

Keep source trees clean by routing intermediate outputs to the approved scratch location and removing them once no longer needed.

## Procedure

1. Identify the workspace's approved scratch or temporary-output location from local instructions.
2. Before running a command that emits ad hoc files, choose an explicit path under that scratch location.
3. Perform the diagnostic or transformation work using only those scratch paths.
4. Consume the output (inspect, parse, summarize, or extract what is needed).
5. Delete the temporary artifacts immediately after they stop being useful.
6. Before creating temporary folders or files under a project root, inspect existing `.gitignore` coverage. If no suitable rule exists, propose a narrowly scoped rule before creating them; use an approved external scratch location until the path is covered.
7. For harness-generated session state, prefer the harness or user-wide session directory. If a project-local fallback is used, verify that its narrow path is ignored before generation.
8. Run one final hygiene check to confirm no unintended artifacts remain outside the approved scratch location and that generated paths are not tracked by Git.

## Practical Notes

- Prefer predictable filenames that include intent, such as `scratch/coverage-summary.txt`.
- Avoid OS-reserved names for file outputs.
- If the task spans multiple steps, keep all temporary outputs in one scratch subfolder so cleanup is simple and explicit.

## Escalation

If the workspace has no documented scratch location, create and gitignore `./.tmp` at the project root and use it as the default temp directory rather than source directories. Optionally ask once for a preferred location, but do not block on it.
