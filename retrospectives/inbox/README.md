# Retrospectives Inbox

This directory stores sanitized, user-wide observations and session learning awaiting initial triage. Once triaged, notes are moved to a sibling directory matching their disposition.

| Directory | Status | Purpose |
| --- | --- | --- |
| [inbox/](./) | Captured | Awaiting initial triage (here) |
| [promoted/](../promoted/) | Promoted | Lesson applied to durable guidance |
| [deferred/](../deferred/) | Deferred | Set aside for later re-evaluation |
| [rejected/](../rejected/) | Rejected | Considered and declined |

Inbox notes are not instructions. They are reviewable decision records used to decide whether a lesson should be promoted into `memory/`, `instructions/`, `skills/`, `playbooks/`, or another checked-in guidance area.

Inbox notes are intended for source control, but they must not preserve private raw session details. Generalize personal project names, repository names, people, clients, paths, and exact proprietary outputs unless those details are necessary and safe to share.

Choose scope before using this inbox. If a lesson is intended only for a project with an Adaptive Agents Project Layer, capture it under `.adaptive-agents/retrospectives/inbox/` instead. If scope is uncertain and a Project Layer exists, prefer project-local capture until cross-project evidence supports escalation.

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
2. Record `Scope: User-wide` and the cross-project evidence or explicit intent supporting that scope.
3. Record sanitized evidence and impact from the session.
4. Leave the status as `Captured` until triaged.
5. Use [adaptation-cycle.md](../../playbooks/adaptation-cycle.md) when deciding whether to promote it.
6. After triage, move the note to the matching sibling directory (`promoted/`, `deferred/`, or `rejected/`) and update its status and promotion links.

When in doubt, capture a retrospective instead of modifying durable guidance directly.
