---
applyTo: "**"
---

# Adaptive Agents Instructions

## Dogfood Workspace Hygiene

Keep temporary dogfood workspaces available while their reports, transcripts, or
generated files may still be needed for analysis. Do not delete them
automatically when a run completes. Initialize a workspace as a Git repository
only when Git-specific behavior is part of the test; otherwise leave generated
fixtures outside nested repositories to avoid unnecessary IDE source-control
noise.

When closing an active plan or backlog item that retains temporary dogfood workspaces, ask the user whether those workspaces should be cleaned up. Preserve them until the user decides; do not infer that the end of a run or plan authorizes deletion.

Before changing repository behavior, structure, templates, schemas, installers, validators, or integration boundaries, read the [Architecture contract](../ARCHITECTURE.md).

Update the architecture contract in the same change when an architectural invariant, ownership boundary, canonical route, or validation responsibility changes. Do not load it for read-only questions or changes limited to planning status, retrospective capture, or editorial wording that does not alter documented behavior.

Add other focused rules only after confirming they are specific to this project and do not duplicate an existing authoritative project document.