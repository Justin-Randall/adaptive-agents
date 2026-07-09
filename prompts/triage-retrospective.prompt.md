---
description: "Triage an Adaptive Agents retrospective and propose next action without applying changes."
agent: "agent"
argument-hint: "Path to retrospective note"
---

# Triage Retrospective

Triage one captured retrospective and recommend what should happen next. Do not apply changes unless the user explicitly asks you to after reviewing the proposal.

Use these references:

- [Adaptive Agents index](../INDEX.md)
- [Adaptation cycle](../playbooks/adaptation-cycle.md)
- [Retrospectives inbox](../retrospectives/inbox/README.md)
- [Update Adaptive Agents](../skills/update-adaptive-agents/SKILL.md)

## Input

The user should provide the path to one retrospective note in `retrospectives/inbox/`.

If the user does not provide a path, ask one concise clarifying question for the retrospective path.

## Rules

- Triage exactly one retrospective note.
- Do not edit durable guidance.
- Do not edit the retrospective unless the user explicitly asks you to apply the proposed update.
- Check whether existing guidance already covers the lesson before proposing durable changes.
- Prefer `Deferred` when evidence is plausible but not yet durable.
- Prefer `Promoted to existing guidance` when the lesson is already covered by durable guidance.
- Prefer `Promote with proposed patch` only when a focused durable update is justified.
- Check whether the retrospective contains private project names, repository names, people, clients, paths, proprietary outputs, secrets, or raw logs; if so, recommend sanitizing the retrospective before promotion.
- Do not propose durable guidance patches that include private specifics. Generalize the lesson into reusable behavior.
- Use repository-relative Markdown links only, such as `[INDEX.md](../INDEX.md)` or `[coding.instructions.md](../instructions/coding.instructions.md)`.
- Do not use `vscode-file://`, `file://`, or VS Code internal workbench URLs.
- If section 5 says any file should be updated, section 6 must include a patch for that update.
- If proposing a patch, return it in a fenced `diff` block using plain repository-relative file paths.
- Write `No patch recommended.` only when section 5 says no file should be updated.

## Decision Set

Choose exactly one:

- `Deferred`
- `Rejected`
- `Promoted to existing guidance`
- `Promote with proposed patch`

## Output

Return these sections:

1. Triage decision
2. Rationale
3. Existing guidance that already covers it, if any
4. Proposed durable target, if any
5. Whether the retrospective itself should be updated
6. Exact patch you would apply, but do not apply it

## Patch Format

When a patch is recommended, section 6 must use this shape:

```diff
*** Begin Patch
*** Update File: retrospectives/inbox/YYYY-MM-DD-short-title.md
@@
- old text
+ new text
*** End Patch
```

Use plain repository-relative file paths in patch headers. Do not put Markdown links in patch headers.

If no patch is recommended, write `No patch recommended.` for section 6.
