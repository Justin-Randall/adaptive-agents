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
6. Run one final hygiene check to confirm no unintended artifacts remain outside the approved scratch location.

## Practical Notes

- Prefer predictable filenames that include intent, such as `scratch/coverage-summary.txt`.
- Avoid OS-reserved names for file outputs.
- If the task spans multiple steps, keep all temporary outputs in one scratch subfolder so cleanup is simple and explicit.

## Escalation

If the workspace has no documented scratch location, ask once for the preferred location before generating ad hoc files.
