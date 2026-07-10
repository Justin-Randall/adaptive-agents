---
name: manage-retrospectives
description: "Use when: capturing, triaging, or promoting a lesson that may belong only to this Project Layer rather than user-wide Adaptive Agents."
---

# Manage Retrospectives

Use [Project retrospectives](../../retrospectives/INDEX.md) for learning owned by this project.

## Choose Scope First

Before choosing instructions, skills, playbooks, memory, or another target, decide the lesson's scope:

- `Project Layer`: the requested behavior, convention, workflow, or fact is intended only for this project or closely related work.
- `User-wide`: evidence shows the behavior should apply across unrelated projects.
- `Undetermined`: the recurrence boundary is unclear. Capture in this Project Layer by default and record what evidence would justify user-wide escalation.

Project-specific evidence must not be promoted user-wide merely because a user-wide target type exists.

## Capture

1. Create one note under `retrospectives/inbox/` from `retrospectives/inbox/template.md`.
2. Add a brief link under `Captured Notes` in `retrospectives/inbox/README.md` so the note is reachable from the root index.
3. Record scope, scope rationale, evidence, impact, and the proposed target within this Project Layer.
4. Set `Status: Captured` and do not edit durable guidance.
5. Respect this layer's source-control policy. Never include secrets, credentials, or private client data.

## Triage And Promote

1. Re-evaluate scope before target type.
2. Check existing project instructions, skills, playbooks, and memory before proposing additions.
3. Keep promotion within `.adaptive-agents/` by default.
4. Stop at a proposed patch and request explicit approval.

## Escalate User-Wide

Escalation is a separate promotion decision:

1. Require evidence that the lesson recurs or should apply across unrelated projects.
2. Remove project names, paths, proprietary details, and project-only assumptions.
3. Propose the user-wide target and sanitized patch separately.
4. Ask for explicit approval before editing the canonical Adaptive Agents repository.
5. Preserve a link or summary in the project retrospective when both repositories can reference it safely.

Run `bash .adaptive-agents/scripts/check-project-layer.sh` after retrospective structure or status changes.