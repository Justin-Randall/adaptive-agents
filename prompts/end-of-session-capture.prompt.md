---
description: "Review the session for reusable Adaptive Agents learning and capture one retrospective only when evidence is concrete."
agent: "agent"
argument-hint: "Optional session summary or learning to consider"
---

# End-of-Session Capture

Review the current session for reusable Adaptive Agents learning. Capture one retrospective only when there is enough concrete evidence.

Use these references:

- [Retrospectives inbox](../retrospectives/inbox/README.md)
- [Retrospective template](../retrospectives/inbox/template.md)
- [Adaptation cycle](../playbooks/adaptation-cycle.md)
- [Capture retrospective prompt](capture-retrospective.prompt.md)

## Rules

- Do not edit durable guidance files.
- Do not update `INDEX.md`.
- Do not promote a retrospective.
- Create at most one retrospective note.
- Create a note only for a concrete, reusable lesson, failure mode, workflow improvement, or user preference with evidence from the session.
- Treat a failed implementation or diagnostic approach, meaningful retry, discarded hypothesis, rollback, user correction, or reusable workaround as process-friction evidence even when the task ultimately succeeded.
- When process-friction evidence exists, summarize it in one sentence and ask whether the user wants it captured. Do not create the note until the user answers.
- Use the confidence tiers from [Adaptation cycle](../playbooks/adaptation-cycle.md): high confidence creates or proposes capture, medium confidence asks one concise clarifying question, and low confidence reports no capture.
- If there is no concrete reusable lesson, report that no retrospective was captured and explain why in one sentence.
- If the evidence is promising but incomplete, ask one concise clarifying question instead of creating a vague note.
- If creating a note, use `retrospectives/inbox/YYYY-MM-DD-short-title.md`.
- If creating a note, set `Status: Captured`.
- If creating a note, record observation, sanitized evidence, impact, proposed durable target, and a dogfood check.
- Generalize private project names, repository names, people, clients, local paths, proprietary outputs, and raw logs unless the user explicitly says they are safe to include.
- Do not include secrets, credentials, or private client data.
- Use repository-relative Markdown links for file references.
- Do not use `vscode-file://`, `file://`, `vscode://`, or `workbench.html` links in the report.

## Output

If a retrospective is created, report:

1. Created file
2. Captured lesson in one sentence
3. Why it remains `Captured`
4. Suggested dogfood or triage check

If no retrospective is created, report:

1. No retrospective captured
2. Reason
3. What evidence would justify capture later

For lightweight wrap-up use, prefer this compact form:

- Retrospective Check: Triggered/Not triggered
- Evidence or reason: one sentence
- Next action: capture question, captured, proposed, clarifying question, or no action
