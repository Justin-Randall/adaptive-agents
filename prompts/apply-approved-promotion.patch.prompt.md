---
description: "Apply a user-approved Adaptive Agents promotion patch with bounded validation."
agent: "agent"
argument-hint: "Approved patch text or triage response"
---

# Apply Approved Promotion Patch

Apply a promotion patch only after the user explicitly approves it. This prompt executes the safety boundary after triage: triage proposes, the user approves, this prompt applies.

Use these references:

- [Adaptive Agents index](../INDEX.md)
- [Adaptation cycle](../playbooks/adaptation-cycle.md)
- [Adaptive automation roadmap](../playbooks/adaptive-automation-roadmap.md)
- [Update Adaptive Agents](../skills/update-adaptive-agents/SKILL.md)

## Input

The user should provide either:

- an approved patch from a triage response, or
- a triage response plus a clear approval phrase such as `approved`, `apply this patch`, or equivalent.

If approval is ambiguous, ask one concise clarifying question before editing.

Approval must be specific to the patch being applied in the current context. If approval references an older or different patch, stop and ask for reconfirmation.

## Rules

- Apply only the user-approved patch.
- Re-read each target file before editing.
- Do not expand the scope beyond the approved patch.
- Use repository-relative paths only.
- Require every patch hunk to include an explicit repository-relative file path in its `*** Update File:` header.
- Do not infer target files from basename, prior conversation, active editor, or surrounding context.
- Do not apply patches that reference `vscode-file://`, `file://`, VS Code internal workbench URLs, or ambiguous file labels.
- Do not apply patches that add private project names, repository names, people, clients, private paths, proprietary outputs, secrets, or raw copied logs unless the user explicitly says those details are safe to include.
- If a patch appears to promote private specifics into durable guidance, stop and ask one concise clarification question instead of applying it.
- If the patch no longer matches current file contents, stop and explain the mismatch instead of improvising.
- If the approved patch updates durable guidance, also update the retrospective status and promotion links only when that update is included in the approved patch or explicitly approved by the user.
- After applying the approved patch, run `bash scripts/check-adaptive-agents.sh` when the script exists.
- If the checker fails, report the failures and ask the user whether to approve a corrective patch, adjust the promotion, or leave the repository as-is for now. Do not auto-fix checker failures without user approval.
- Validate the completed edit slice once, then stop and report.
- Treat these as explicit apply approvals: `approved`, `apply this patch`, `apply section 6 patch`, `ship this exact patch`, or equivalent unambiguous phrasing.
- Treat these as not sufficient by themselves: `do a full retrospective`, `continue`, `sounds good`, `go ahead` without clear apply intent tied to a patch.
- If apply approval is missing or ambiguous, ask one concise question and do not edit files.

## Validation

After applying the patch:

- read each changed file once
- run diagnostics for changed Markdown files when available
- run `bash scripts/check-adaptive-agents.sh` when available
- report whether validation passed
- if the checker reports failures, surface them as the next user decision point instead of applying unapproved fixes
- do not rerun equivalent readback, diagnostics, listing, or status checks unless a new issue appears

## Output

Return:

1. Applied files
2. Validation result
3. Any skipped or mismatched patch hunks
4. Next dogfood check
