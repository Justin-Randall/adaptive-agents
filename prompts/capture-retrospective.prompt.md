---
description: "Capture a session observation as an Adaptive Agents retrospective without promoting it."
agent: "agent"
argument-hint: "Observation or lesson to capture"
---

# Capture Retrospective

Capture the user's observation as a new retrospective note in `retrospectives/inbox/`.

Use these references:

- [Retrospectives inbox](../retrospectives/inbox/README.md)
- [Retrospective template](../retrospectives/inbox/template.md)
- [Adaptation cycle](../playbooks/adaptation-cycle.md)
- [Update Adaptive Agents](../skills/update-adaptive-agents/SKILL.md)

## Rules

- Create exactly one retrospective note.
- Use the filename format `YYYY-MM-DD-short-title.md`.
- Set `Status: Captured`.
- Record the observation, sanitized concrete evidence, impact, and proposed durable target.
- Generalize private project names, repository names, people, clients, local paths, proprietary outputs, and raw logs unless the user explicitly says they are safe to include.
- Do not include secrets, credentials, or private client data.
- Do not edit durable guidance files.
- Do not update `INDEX.md`.
- Do not promote the retrospective.
- If the observation lacks enough evidence, ask one concise clarifying question instead of creating a vague note.

## Output

After creating the note, report:

- the file path
- the captured observation in one sentence
- why it remains `Captured`
- the suggested dogfood check
