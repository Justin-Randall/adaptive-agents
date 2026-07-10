---
description: "Capture a session observation as an Adaptive Agents retrospective without promoting it."
agent: "agent"
argument-hint: "Observation or lesson to capture"
---

# Capture Retrospective

Capture the user's observation in the narrowest appropriate retrospective inbox.

Use these references:

- [Retrospectives inbox](../retrospectives/inbox/README.md)
- [Retrospective template](../retrospectives/inbox/template.md)
- [Adaptation cycle](../playbooks/adaptation-cycle.md)
- [Update Adaptive Agents](../skills/update-adaptive-agents/SKILL.md)
- When present, `.adaptive-agents/skills/manage-retrospectives/SKILL.md`

## Rules

- Create exactly one retrospective note.
- Decide scope before target type.
- Use `.adaptive-agents/retrospectives/inbox/` when the behavior is intended only for the current project.
- Use `retrospectives/inbox/` in the canonical Adaptive Agents repository only when cross-project evidence or explicit user intent establishes user-wide scope.
- If scope is uncertain and a Project Layer exists, capture there with `Scope: Undetermined`; otherwise ask one concise scope question.
- Use the filename format `YYYY-MM-DD-short-title.md`.
- Set `Status: Captured`.
- Record scope, scope rationale, the observation, concrete evidence, impact, and proposed target within that scope.
- Generalize private project names, repository names, people, clients, local paths, proprietary outputs, and raw logs unless the user explicitly says they are safe to include.
- Do not include secrets, credentials, or private client data.
- Do not edit durable guidance files.
- Do not update `INDEX.md`.
- Do not promote the retrospective.
- If the observation lacks enough evidence, ask one concise clarifying question instead of creating a vague note.

## Output

After creating the note, report:

- the file path
- the selected scope and rationale
- the captured observation in one sentence
- why it remains `Captured`
- the suggested dogfood check
