# Retrospectives Inbox

This directory stores sanitized observations and session learning before they become durable Adaptive Agents guidance.

Inbox notes are not instructions. They are reviewable decision records used to decide whether a lesson should be promoted into `memory/`, `instructions/`, `skills/`, `playbooks/`, or another checked-in guidance area.

Inbox notes are intended for source control, but they must not preserve private raw session details. Generalize personal project names, repository names, people, clients, paths, and exact proprietary outputs unless those details are necessary and safe to share.

If private evidence is needed temporarily, keep it outside source control, such as under ignored `retrospectives/private/` or in a `*.local.md` note. Do not link durable guidance to private scratch notes as evidence.

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
- personal project names, repository names, people, client names, private paths, or other identifying details unless explicitly safe to share
- large copied source code or external documentation
- project-specific facts that should live in the project repository
- durable instructions that have already been promoted

## Workflow

1. Create a note from [template.md](template.md) using the filename format `YYYY-MM-DD-short-title.md`.
2. Record sanitized evidence and impact from the session.
3. Leave the status as `Captured` until triaged.
4. Use [adaptation-cycle.md](../../playbooks/adaptation-cycle.md) when deciding whether to promote it.
5. Update the note with promotion status and links to changed files.

When in doubt, capture a retrospective instead of modifying durable guidance directly.
