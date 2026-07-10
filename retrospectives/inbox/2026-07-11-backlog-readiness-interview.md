# Retrospective: Backlog item added without sufficient detail/interview

- Date: 2026-07-11
- Status: Captured
- Scope: User-wide
- Session or task: Adding and activating OpenCode backlog item (PL-20260710)

## Observation

When asked to add a feature to the backlog, I wrote a brief description and marked it "Ready" without interviewing the user for more detail first. The user had to prompt me twice — once to flesh out the implementation plan, and once to remove PII and generalize path references — before the item was genuinely ready for activation.

## Evidence

1. Initial backlog item was sparse (Objective, Problem Spec, 6-line Scope) and lacked detail about how OpenCode config works, specific files to create/modify, and implementation mechanics.
2. User prompted: "Think about the plan and go into greater detail about how it will be implemented, which files will be changed or created, etc." — I then researched OpenCode docs and produced a detailed plan.
3. User prompted: "Let's not get too specific about the install directories... You need to be clear about that in the examples" — I then generalized path references.
4. User prompted: "I also meant not using my name or my drive or any PII" — I then removed personal paths.

## Impact

Extra iteration cycles that could have been avoided. The user had to act as QA/reviewer for plan quality rather than reviewing the plan on its merits.

## Root Cause

The backlog item was set to "Ready" status prematurely. The manage-planning skill says "Keep backlog items lightweight" which was interpreted as "brief is sufficient" rather than "detailed enough to activate." The skill should emphasize interviewing the user before marking Ready.

## Lesson

When asked to add a backlog item with only a brief description:

1. Interview the user for more detail before writing: What files need to change? What are the integration points? Any design constraints? Any prior art to reference?
2. Research the domain (docs, existing code patterns, standards) to produce concrete file-level detail.
3. Only mark the item "Ready" when it contains enough specificity to write an SDD without reopening basic questions.
4. Never include PII in plans.

## Proposed Project Target

- `skills/manage-planning/SKILL.md` — add to backlog creation guidance: "Before setting a backlog item to Ready, interview the user for scope detail, research the domain, and ensure file-level specificity. Do not include PII."
