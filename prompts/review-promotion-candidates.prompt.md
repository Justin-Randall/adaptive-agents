---
description: "Review captured and deferred retrospectives for likely promotion candidates without editing files."
agent: "agent"
argument-hint: "Optional focus, such as docs, prompts, validation, or stale notes"
---

# Review Promotion Candidates

Review `retrospectives/inbox/` for captured and deferred lessons that may be ready for promotion into durable Adaptive Agents guidance. Report candidates and next actions without editing files or proposing patches.

Use these references:

- [Adaptive Agents index](../INDEX.md)
- [Adaptation cycle](../playbooks/adaptation-cycle.md)
- [Adaptive automation roadmap](../playbooks/adaptive-automation-roadmap.md)
- [Retrospectives inbox](../retrospectives/inbox/README.md)
- [Update Adaptive Agents](../skills/update-adaptive-agents/SKILL.md)
- [Triage retrospective prompt](triage-retrospective.prompt.md)

## Rules

- Do not edit files.
- Do not propose or include patches.
- Read the inbox index and the retrospective notes needed for the report.
- Focus on notes with status `Captured` or `Deferred`.
- Mention `Promoted` notes only when they show existing coverage or prevent duplicate promotion.
- Check whether each candidate is sanitized enough for source-controlled durable guidance.
- Do not repeat private project names, repository names, people, clients, private paths, proprietary outputs, secrets, or raw logs in the report.
- Prefer the narrowest likely durable target: `memory/`, `instructions/`, `skills/`, `playbooks/`, `prompts/`, `README.md`, or `INDEX.md`.
- Distinguish candidate review from triage: recommend which note to triage next, but leave the final decision and patch proposal to [triage-retrospective.prompt.md](triage-retrospective.prompt.md).
- Use repository-relative Markdown links for file references.
- Do not use `vscode-file://`, `file://`, `vscode://`, or `workbench.html` links in the report.
- Keep the report concise and actionable.

## Candidate Readiness

Classify each reviewed note as one of:

- `Ready for triage`: concrete evidence, reusable lesson, plausible durable target, and no obvious privacy blocker.
- `Needs cleanup first`: useful lesson, but the note needs sanitization, clearer evidence, a narrower target, or status cleanup before triage.
- `Defer`: plausible but not enough evidence, too project-specific, already waiting on more dogfood, or lower priority than other candidates.
- `Already covered`: durable guidance already appears to cover the lesson; recommend linking or closing rather than creating new guidance.

## Output

Return these sections:

1. Top recommendation
2. Candidate table with note, readiness, likely durable target, and reason
3. Already-covered or duplicate lessons
4. Privacy or sanitization concerns
5. Suggested next command or prompt to run
6. Files that should not be changed

If there are no promotion candidates, say so clearly and recommend the next queue-maintenance action.