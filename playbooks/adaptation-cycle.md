# Adaptation Cycle

Use this playbook to turn session learning into reviewable, durable Adaptive Agents guidance.

The goal is controlled adaptation: capture useful observations quickly, promote only lessons with evidence, and keep durable guidance small, discoverable, and versioned.

## Lifecycle

```text
session observation
  -> scope decision: Project Layer | User-wide | Undetermined
  -> scoped retrospectives/inbox note
  -> scoped triage
  -> target-type decision within that scope
  -> focused update
  -> routing update if needed
  -> validation
```

## 1. Capture

Create a retrospective note when a session reveals a reusable lesson, failure mode, preference, or workflow improvement.

Choose scope before choosing a target type:

- `Project Layer`: use `.adaptive-agents/retrospectives/inbox/` when behavior is intended only for the current project or closely related work.
- `User-wide`: use this repository's `retrospectives/inbox/` only when evidence or explicit user intent supports behavior across unrelated projects.
- `Undetermined`: when a Project Layer exists, capture there by default and record what evidence would justify user-wide escalation. Without a Project Layer, ask the user where the uncertain note should live.

Use [retrospectives/inbox/template.md](../retrospectives/inbox/template.md) for new notes. Keep the note factual, sanitized, and evidence-based; do not treat it as durable guidance yet.

Do not include private project names, repository names, people, clients, paths, proprietary outputs, secrets, or raw copied logs in checked-in retrospectives. Generalize private details unless the user explicitly says they are safe to include.

Good retrospective candidates include:

- a repeated agent mistake
- a workflow that clearly improved outcomes
- a loading or routing failure mode
- a user preference that is likely to recur
- a missing skill, instruction, playbook, prompt, memory, or schema

### Autonomous Capture Triggers

Agents should not wait for the user to propose every retrospective. During normal work, create or propose a sanitized `Captured` retrospective when there is concrete evidence of:

- repeated agent correction, rollback, or patch revision after user feedback
- a failed implementation or diagnostic approach that required a meaningful retry
- a discarded hypothesis that consumed enough work to reveal a reusable process lesson
- a tool, shell, editor, model, or workflow behavior that blocked progress or required a reusable workaround
- a user preference or collaboration pattern that is likely to recur
- durable guidance, README content, routing, or checker behavior drifting from repository reality
- a successful workflow that should be reused in future sessions
- a validation, checker, or prompt failure that revealed missing guidance

When already working in the Adaptive Agents repository, distinguish this repository's tracked Project Layer from its canonical user-wide guidance. Project-specific lessons go to `.adaptive-agents/retrospectives/inbox/`; cross-project lessons go to `retrospectives/inbox/`. In another repository with a Project Layer, prefer its local inbox unless user-wide scope is established.

Autonomous capture stops at `Captured`. Do not triage, promote, apply patches, or update durable guidance without an explicit user approval step.

At the completion-time checkpoint, process-friction evidence requires a user-visible prompt even if the task eventually succeeded. Summarize the failed approach, retry, discarded hypothesis, rollback, correction, or workaround in one sentence and ask whether the user wants it captured. Do not silently create the note or suppress the prompt because the final validation passed.

Use these confidence tiers when deciding what to do:

- **High confidence**: concrete evidence shows a repeated or consequential failure mode, workflow workaround, preference, or guidance drift. For process-friction evidence, prompt the user to capture it; for other triggers, propose or create a sanitized `Captured` retrospective while respecting repository boundary rules.
- **Medium confidence**: evidence suggests a reusable lesson, but the impact or recurrence is uncertain. Ask one concise clarifying question before capture.
- **Low confidence**: there is no concrete reusable evidence. Do not create a retrospective; briefly state why no capture is warranted if reporting completion.

High-confidence trigger examples include:

- a failed solution or diagnostic hypothesis that required a meaningful change of approach
- repeated equivalent command, tool, or patch attempts after the first meaningful failure indicates a different diagnostic path is needed
- repeated user correction about the same agent behavior or workflow assumption
- violation of the active workspace's temp-artifact, scratch, or cleanup policy after local instructions have been loaded
- a validation, checker, or prompt failure that exposes missing or misleading guidance
- explicit user feedback that agent process quality should be improved for future sessions

## 2. Triage

Before promotion, decide whether the observation is durable.

Re-evaluate scope before selecting the target type. Promotion remains within the capture scope by default. Moving a project lesson to user-wide guidance is a separate escalation decision requiring cross-project evidence, sanitization, a proposed patch, and explicit approval.

Promote only when the lesson is:

- reusable across future sessions or projects
- specific enough to guide behavior
- supported by evidence from the session
- not already covered by existing guidance

If uncertain, leave it in `retrospectives/inbox/` and record what evidence would make it promotable.

### Triage-to-Apply Handoff (Mandatory)

Triage and review are proposal-only steps. They must stop at recommendation + proposed patch and wait for explicit user approval.

Use this decision rule:

- No explicit apply approval: do not edit files.
- Explicit apply approval for a specific proposed patch: apply only that patch.
- Ambiguous approval: ask one concise clarifying question before any edits.

## 3. Choose the Target

After scope is established, use the narrowest durable destination within that scope:

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

For `Project Layer`, these paths are relative to `.adaptive-agents/`. For `User-wide`, they are relative to this canonical repository.

When modifying Adaptive Agents guidance, load [Update Adaptive Agents](../skills/update-adaptive-agents/SKILL.md).

## 4. Promote

Promotion should be a small, focused change.

- Prefer editing the owning file over duplicating guidance elsewhere.
- Prefer creating a narrow new file over expanding broad entrypoints.
- Use Markdown links when referencing other checked-in guidance files.
- Generalize the durable lesson; do not promote private project specifics, names, paths, or proprietary session details into reusable guidance.
- Do not make the user-wide repository the target merely because it has more artifact types. Project-owned behavior belongs in the Project Layer.
- Treat Project Layer to user-wide escalation as a new, separately approved promotion proposal.
- Update `INDEX.md` when discovery changes.
- Keep tool-native adapters as disposable wiring rather than sources of durable guidance.

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
