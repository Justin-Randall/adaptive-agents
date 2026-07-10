---
description: "Use when: running commands that produce intermediate files, diagnostics, coverage outputs, or ad hoc artifacts."
---

# Temporary Artifact Hygiene Instructions

Route intentional intermediate outputs to the active workspace's approved scratch or temporary-output location, then clean them up once they are no longer needed.

## Output Location Rules

- Never write ad hoc artifacts into source directories when a workspace scratch/temp policy exists.
- Prefer paths inside the workspace-approved scratch location (for example `Scratch/` when that is the local convention).
- Use filenames that cannot be confused with reserved device names on the current OS.

## Cleanup Rules

- Delete temporary artifacts created for diagnostics, parsing, coverage inspection, or one-off transformation as soon as they have served their purpose.
- Before wrapping up a task, ensure ad hoc artifacts are not left in source directories.
- If a temporary artifact must remain briefly for a follow-up step, keep it in the approved scratch area and remove it when the follow-up is complete.

## Validation

- Perform one final hygiene check before completion (for example, verify the working tree does not contain unintended temp artifacts).
- If a project-local rule is stricter than this instruction, follow the project-local rule.