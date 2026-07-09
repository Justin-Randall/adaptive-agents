# Retrospective: Prompt discovery path

- Date: 2026-07-09
- Status: Promoted
- Session or task: Building the first assisted retrospective capture prompt

## Observation

Checked-in prompt files are useful as durable Adaptive Agents source files, but they need an explicit invocation or discovery path before they can serve as a reliable dogfood test in VS Code.

## Evidence

While planning `prompts/capture-retrospective.prompt.md`, the VS Code prompt reference showed that prompt discovery is strongest for `.github/prompts/*.prompt.md` and user-profile prompts. The Adaptive Agents repository uses `prompts/` as checked-in source of truth, so simply creating a prompt there may not make it available as a slash command in every VS Code chat context.

## Impact

If prompt source files are not paired with a clear test path, agents may think automation is ready while users still cannot easily invoke it. The adaptation workflow needs to distinguish checked-in prompt source from VS Code runtime discoverability.

## Proposed Durable Target

- `playbooks/`
- `prompts/`
- `scripts/`
- `INDEX.md`

## Promotion Decision

- Status: Promoted
- Decision: Promote with proposed patch.
- Rationale: The observation is durable because it applies to future checked-in prompt workflows. The durable guidance should live in the automation roadmap, which owns prompt dogfooding and staged automation readiness.

## Promotion Links

Add Markdown links to changed durable guidance files if promoted.

- [Adaptive automation roadmap](../../playbooks/adaptive-automation-roadmap.md)
