---
description: "Review the Adaptive Agents retrospective inbox and report queue status without editing files."
agent: "agent"
argument-hint: "Optional focus, such as status, stale notes, or promotion links"
---

# Review Retrospective Inbox

Review `retrospectives/inbox/` as a queue. Report status and issues without editing files.

Use these references:

- [Retrospectives inbox](../retrospectives/inbox/README.md)
- [Retrospective template](../retrospectives/inbox/template.md)
- [Adaptation cycle](../playbooks/adaptation-cycle.md)
- [Adaptive automation roadmap](../playbooks/adaptive-automation-roadmap.md)

## Rules

- Do not edit files.
- Read the retrospective inbox files needed for the report.
- Group notes by status: `Captured`, `Deferred`, `Promoted`, `Rejected`, and `Unknown`.
- Flag filenames that do not match `YYYY-MM-DD-short-title.md`, except `README.md` and `template.md`.
- Flag promoted notes that do not include at least one promotion link.
- Flag captured or deferred notes that appear ready for triage or re-triage.
- Use repository-relative Markdown links for file references.
- Do not use `vscode-file://`, `file://`, `vscode://`, or `workbench.html` links in the report.
- Keep the report concise and actionable.

## Output

Return:

1. Queue summary by status
2. Issues found
3. Suggested next action
4. Files that should not be changed

If no issues are found, say so clearly.
