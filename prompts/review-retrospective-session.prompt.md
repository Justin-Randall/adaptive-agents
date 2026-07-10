---
description: "Run a guided retrospective review session that prepares a user decision without applying changes."
agent: "agent"
argument-hint: "Optional focus or path to a retrospective note"
---

# Review Retrospective Session

Run the review side of the Adaptive Agents learning loop. Select or review one retrospective, prepare a recommendation, and stop for the user's approve, adjust, or deny decision. Do not edit files.

Use these references:

- [Adaptive Agents index](../INDEX.md)
- [Adaptation cycle](../playbooks/adaptation-cycle.md)
- [Adaptive automation roadmap](../playbooks/adaptive-automation-roadmap.md)
- [Retrospectives inbox](../retrospectives/inbox/README.md)
- [Update Adaptive Agents](../skills/update-adaptive-agents/SKILL.md)
- [Review promotion candidates](review-promotion-candidates.prompt.md)
- [Triage retrospective](triage-retrospective.prompt.md)
- [Apply approved promotion patch](apply-approved-promotion.patch.prompt.md)

## Input

The user may provide:

- a path to one retrospective note,
- a focus such as docs, prompts, validation, checker failures, or stale notes, or
- no argument, in which case review the inbox and choose the best `Captured` or `Deferred` candidate.

## Rules

- Do not edit files.
- Do not apply patches.
- Determine whether the review concerns the current Project Layer, user-wide Adaptive Agents, or both.
- Review the scoped inbox selected by the user's path or intent. If no scope is provided and a Project Layer exists, ask which inbox to review rather than silently mixing queues.
- Select exactly one candidate unless the user provided a specific retrospective path.
- Prefer `Captured` or `Deferred` notes with concrete evidence, reusable lessons, and a plausible durable target.
- Mention other candidates only briefly when explaining why the selected note is first.
- Respect the retrospective's own promotion decision, rationale, and dogfood check. If the note explicitly says more validation or evidence is needed before promotion, call that out as a decision factor; do not silently override it.
- Check whether existing guidance already covers the lesson before recommending durable changes.
- Re-evaluate scope before target type and search existing guidance in that scope first.
- Keep project-scoped promotion under `.adaptive-agents/` unless a separate sanitized user-wide escalation is justified and approved.
- Check whether the note is sanitized enough for source-controlled durable guidance.
- Do not repeat private project names, repository names, people, clients, private paths, proprietary outputs, secrets, or raw logs in the report.
- Use repository-relative Markdown links for file references.
- Do not use `vscode-file://`, `file://`, `vscode://`, or `workbench.html` links.
- If recommending promotion, include a proposed patch in a fenced `diff` block, but do not apply it.
- If recommending an update to the retrospective status or promotion links, include that update in the proposed patch.
- Do not treat the user's decision to defer the recommendation as approval to change the retrospective's status to `Deferred`. Only propose or apply status changes when the user explicitly approves that status change.
- The patch must use apply-patch style headers with explicit repository-relative paths: `*** Add File:` for new files and `*** Update File:` for existing files.
- Do not use `/dev/null`, `--- a/path`, `+++ b/path`, or line-number hunk headers in proposed patches.
- End by asking the user to choose one of: approve, adjust, deny, or defer.
- Hard stop: this review step is proposal-only and must not edit files under any wording.
- Treat requests like "do a full retrospective" as review/triage scope unless the user explicitly approves applying a specific proposed patch.
- If the user wants immediate changes, respond with the proposed patch and request explicit apply approval first.

## Decision Set

Choose exactly one recommendation:

- `Deferred`
- `Rejected`
- `Promoted to existing guidance`
- `Promote with proposed patch`

## Output

Return these sections:

1. Selected retrospective
2. Scope decision and rationale
3. Why this one is next
4. Recommendation
5. Existing guidance checked in that scope
6. Proposed durable target
7. Proposed patch, or `No patch recommended.`
8. User decision needed

For section 8, ask: `Approve, adjust, deny, or defer this recommendation?`

If the user approves a patch later, use [apply-approved-promotion.patch.prompt.md](apply-approved-promotion.patch.prompt.md) or the same approved-patch rules, then run the validator for the modified scope.

## Patch Format

When a patch is recommended, section 6 must use this shape:

```diff
*** Begin Patch
*** Add File: playbooks/example-new-playbook.md
+# Example New Playbook
*** Update File: retrospectives/inbox/YYYY-MM-DD-short-title.md
@@
- old text
+ new text
*** End Patch
```

Use plain repository-relative file paths in patch headers. Do not put Markdown links in patch headers.