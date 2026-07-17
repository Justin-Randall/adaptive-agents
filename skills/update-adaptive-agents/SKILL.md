---
name: update-adaptive-agents
description: "Use when: updating the Adaptive Agents repository, promoting retrospectives into durable guidance, creating or revising instructions, skills, memories, playbooks, prompts, agents, schemas, or INDEX.md routing."
---

# Update Adaptive Agents

Use this skill when the user asks to update the Adaptive Agents repository itself or promote session learning into durable user-wide guidance.

Before selecting a target type, confirm that the lesson is user-wide. Project-specific lessons belong in the current `.adaptive-agents/` Project Layer and should use its `manage-retrospectives` skill. If scope is uncertain and a Project Layer exists, keep the capture local until broader evidence supports a separately approved escalation.

For the end-to-end adaptation lifecycle, follow [adaptation-cycle.md](../../playbooks/adaptation-cycle.md).

## First Checks

1. Confirm the current repository is the Adaptive Agents repository by checking for `AGENTS.md` and `INDEX.md` at the root.
2. Read `AGENTS.md` for repository boundary rules.
3. Read `INDEX.md` for current routing and existing guidance areas.
4. Read any existing target file before editing it.
5. Preserve project-local instructions and user edits unless the user explicitly asks to change them.

## Choose the Target

First choose scope:

- `Project Layer`: stop using this user-wide maintenance skill and route to `.adaptive-agents/skills/manage-retrospectives/SKILL.md`.
- `User-wide`: continue below only with cross-project evidence or explicit user intent.
- `Undetermined`: do not update canonical guidance; prefer project-local capture when available.

Use the narrowest durable location that fits the lesson:

| Need | Target |
| --- | --- |
| Raw observation, uncertain lesson, or session note | `retrospectives/inbox/` |
| Durable cross-project preference or recurring lesson | `memory/` |
| Default or broadly applicable agent behavior | `instructions/` |
| Task-specific workflow or domain process | `skills/` |
| Repeatable operational or engineering procedure | `playbooks/` |
| Reusable task starter or prompt template | `prompts/` |
| Specialized role or subagent definition | `agents/` |
| Structured metadata or validation contract | `schemas/` |
| Reusable bootstrap source tree | `templates/` |
| Discovery, routing, or entrypoint change | `INDEX.md` |

If the lesson is not clearly durable, add or propose a retrospective instead of changing permanent guidance.

Use the autonomous capture triggers in [adaptation-cycle.md](../../playbooks/adaptation-cycle.md) when a session reveals a recurring lesson, failure mode, user preference, workflow improvement, guidance drift, or validation/checker failure. Autonomous action stops at creating or proposing a sanitized `Captured` retrospective; triage and promotion still require user approval.

Use the adaptation-cycle confidence tiers consistently:

- High confidence process friction: name the evidence and ask the user whether to create a sanitized `Captured` retrospective, even if the task ultimately succeeded.
- Other high confidence triggers: create or propose a sanitized `Captured` retrospective.
- Medium confidence: ask one concise clarifying question before capture.
- Low confidence: do not capture; briefly state the no-capture reason when reporting completion.

For non-trivial Adaptive Agents maintenance work, include a completion-time retrospective checkpoint in the final report so capture decisions are visible rather than implicit. Treat a failed approach, meaningful retry, discarded hypothesis, rollback, user correction, or reusable workaround as process-friction evidence that requires the user-facing capture question.

## Promotion Rules

- Prefer small, focused files over expanding broad entrypoints.
- Keep `instructions/global.instructions.md` short; it should route to more specific instruction files rather than contain all guidance.
- Keep tool-native adapters minimal and disposable; canonical guidance belongs in routed repository files.
- Do not duplicate the same rule across many files unless repeated intentionally for discovery.
- Use Markdown links when referencing other checked-in guidance files.
- Keep checked-in retrospectives and durable guidance sanitized: do not include private project names, repository names, people, clients, paths, proprietary outputs, secrets, or raw copied logs unless the user explicitly says they are safe to include.
- When promoting a retrospective, generalize from private session evidence into reusable behavior and leave private specifics out of durable guidance.
- Update `INDEX.md` whenever a new durable guidance file or skill needs to be discoverable.
- Keep frontmatter valid YAML and quote descriptions that contain colons.
- Use `applyTo: "**"` only for instructions that truly must be always-on.

## Retrospective Promotion Flow

When promoting a retrospective:

1. Identify the durable lesson in one sentence.
2. Decide whether it belongs in `memory/`, `instructions/`, `skills/`, or `playbooks/`.
3. Check for existing guidance that already covers it.
4. Add the smallest update to the owning file or create a focused new file.
5. Add Markdown links from entrypoints or routing tables only where discovery improves.
6. Leave the original retrospective intact unless the user asks to archive, move, or delete it.

### Retrospective Approval Gate Checklist

Before editing any file for retrospective promotion:

1. Confirm triage/review output exists with a proposed patch.
2. Confirm explicit user approval to apply that patch.
3. If approval is ambiguous, ask one concise clarifying question and stop.
4. Apply only through the approved-patch flow.

## Validation

After edits:

- Read each changed guidance file to check wording, links, and frontmatter.
- Confirm new files are reachable from `INDEX.md` or an appropriate entrypoint.
- Confirm generated/bootstrap files do not become the source of truth for durable guidance.
- After applying a user-approved promotion patch, run `bash scripts/check-adaptive-agents.sh` when available and use any failures as the next user approval point.
- Run lightweight repository checks when available, such as listing new files or checking git status.
- Run each validation category once for the current completed edit slice. If diagnostics are clean, routing is confirmed, and no requested work remains, stop and report the result. Do not rerun equivalent `get_errors`, `git status`, readback, or listing checks unless a new issue appears, the next unfinished step needs its own validation, or the user asks for more detail.
