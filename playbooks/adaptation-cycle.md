# Adaptation Cycle

Use this playbook to turn session learning into reviewable, durable Adaptive Agents guidance.

The goal is controlled adaptation: capture useful observations quickly, promote only lessons with evidence, and keep durable guidance small, discoverable, and versioned.

## Lifecycle

```text
session observation
  -> retrospectives/inbox note
  -> triage
  -> durable target decision
  -> focused update
  -> routing update if needed
  -> validation
```

## 1. Capture

Create a retrospective note when a session reveals a reusable lesson, failure mode, preference, or workflow improvement.

Use [retrospectives/inbox/template.md](../retrospectives/inbox/template.md) for new notes. Keep the note factual, sanitized, and evidence-based; do not treat it as durable guidance yet.

Do not include private project names, repository names, people, clients, paths, proprietary outputs, secrets, or raw copied logs in checked-in retrospectives. Generalize private details unless the user explicitly says they are safe to include.

Good retrospective candidates include:

- a repeated agent mistake
- a workflow that clearly improved outcomes
- a loading or routing failure mode
- a user preference that is likely to recur
- a missing skill, instruction, playbook, prompt, memory, or schema

## 2. Triage

Before promotion, decide whether the observation is durable.

Promote only when the lesson is:

- reusable across future sessions or projects
- specific enough to guide behavior
- supported by evidence from the session
- not already covered by existing guidance

If uncertain, leave it in `retrospectives/inbox/` and record what evidence would make it promotable.

## 3. Choose the Target

Use the narrowest durable destination:

| Lesson type | Target |
| --- | --- |
| Durable cross-project preference or recurring lesson | `memory/` |
| Default or broadly applicable agent behavior | `instructions/` |
| Task-specific workflow or domain process | `skills/` |
| Repeatable operational or engineering procedure | `playbooks/` |
| Reusable task starter or prompt template | `prompts/` |
| Specialized role or subagent definition | `agents/` |
| Structured metadata or validation contract | `schemas/` |
| Discovery or routing change | `INDEX.md` |

When modifying Adaptive Agents guidance, load [Update Adaptive Agents](../skills/update-adaptive-agents/SKILL.md).

## 4. Promote

Promotion should be a small, focused change.

- Prefer editing the owning file over duplicating guidance elsewhere.
- Prefer creating a narrow new file over expanding broad entrypoints.
- Use Markdown links when referencing other checked-in guidance files.
- Generalize the durable lesson; do not promote private project specifics, names, paths, or proprietary session details into reusable guidance.
- Update `INDEX.md` when discovery changes.
- Keep generated files, especially `vscode/user-wide.instructions.md`, as disposable bootstrap wiring.

## 5. Validate

After promotion:

- Read every changed guidance file.
- Confirm frontmatter is valid where present.
- Confirm new durable files are reachable from `INDEX.md` or an appropriate entrypoint.
- Confirm the retrospective still explains the original observation and promotion status.

## Promotion Status

Retrospective notes should use one of these statuses:

- `Captured`: recorded but not triaged
- `Deferred`: plausible but not enough evidence
- `Promoted`: durable guidance was updated
- `Rejected`: not useful or not reusable

Do not delete rejected or deferred notes unless the user asks; they preserve decision history.
