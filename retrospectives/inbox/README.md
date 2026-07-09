# Retrospectives Inbox

This directory stores raw observations and session learning before they become durable Adaptive Agents guidance.

Inbox notes are not instructions. They are evidence records used to decide whether a lesson should be promoted into `memory/`, `instructions/`, `skills/`, `playbooks/`, or another checked-in guidance area.

## What Belongs Here

Add a note when a session reveals:

- a repeated agent failure mode
- a useful workflow improvement
- a user preference that may recur
- a missing instruction, skill, playbook, prompt, memory, or schema
- a bootstrap, loading, routing, or validation issue
- a decision that should be remembered before becoming durable guidance

## What Does Not Belong Here

Do not use inbox notes for:

- secrets, credentials, or private client data
- large copied source code or external documentation
- project-specific facts that should live in the project repository
- durable instructions that have already been promoted

## Workflow

1. Create a note from [template.md](template.md) using the filename format `YYYY-MM-DD-short-title.md`.
2. Record evidence and impact from the session.
3. Leave the status as `Captured` until triaged.
4. Use [adaptation-cycle.md](../../playbooks/adaptation-cycle.md) when deciding whether to promote it.
5. Update the note with promotion status and links to changed files.

When in doubt, capture a retrospective instead of modifying durable guidance directly.
