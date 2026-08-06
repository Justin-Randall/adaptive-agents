---
name: manage-planning
description: "Use when: reading, activating, executing, or closing a Project Layer active plan, backlog item, work-unit memory, or closed-work record."
---

# Manage Planning

Use the current Project Layer's planning router as the authoritative source for local paths, templates, validators, and project-specific conventions. This skill defines the reusable planning lifecycle; more-specific Project Layer guidance overrides it.

## Start work

1. Read the Project Layer planning index, `planning/active/ACTIVE.md`, and every linked supporting document.
2. Check whether the request conflicts with the active objective. Explain the conflict and ask whether to close, replace, or retain the current plan before changing objectives.
3. Determine whether work comes from a backlog item or an approved direct request. Do not activate work silently.
4. Assign one canonical work-unit ID using the Project Layer's naming convention. Prefer the standard `PL-YYYYMMDD-descriptive-slug` form when no more specific convention applies.
5. When activating work, create or update `ACTIVE.md` and its linked supporting memory according to the Project Layer template. Keep the active plan and planning index linked and reachable.
6. When activating a backlog item, use its Objective, Problem Spec, Scope, acceptance criteria, and test approach as source material. Do not overwrite the backlog item. Ask when required specification detail is missing.
7. Never activate an epic directly. Load its architecture context and activate one eligible child. For a child, load the parent epic and check dependencies before proceeding.
8. When reopening closed work, assign a new work-unit ID and link prior closed context without restoring or rewriting the old plan wholesale.

## Backlog and deferred work

- Record out-of-scope discoveries in the active work-unit memory while evaluating them.
- Check the backlog index for overlap before creating a new item. Present partial overlap to the user and let them choose whether to update the existing item or create a new one.
- Keep backlog entries lightweight; expand the full SDD in `ACTIVE.md` during activation.
- Do not mark an item ready until its scope, integration points, constraints, prior art, and validation approach are specific enough to execute.
- Keep plans free of private paths, credentials, client data, and other identifying details.

## Maintain active context

Keep the active plan current as work progresses:

- objective, specifications, scope, and acceptance criteria
- applicable project guidance and decisions
- per-slice test plan and DRY assessment
- progress, verification evidence, and deferred discoveries
- links to every supporting document and work-unit memory

Before each implementation slice, complete the plan's `## DRY Assessment`. The assessment is mandatory even when a full duplication scan is not. Load [jscpd](../jscpd/SKILL.md) for required or project-baseline scans, and load [dry-refactoring](../dry-refactoring/SKILL.md) only when removing detected duplication is in scope.

## Execute the plan

1. Read the active plan's Objective, Specifications, Acceptance Criteria, Scope, Test Plan, and DRY Assessment before editing.
2. Load the Project Layer's relevant instructions, skills, playbooks, and project commands. More-specific local guidance wins.
3. Resolve ambiguous specifications before implementation rather than inventing behavior.
4. Follow the project's testing contract: write the focused failing check first, confirm the failure, make the smallest change, rerun the focused check, then broaden validation when the risk warrants it.
5. Use the plan's DRY assessment to decide whether to run jscpd, and record the command, scope, result, and any intentional or deferred duplication.
6. Verify claims with source, tests, validators, compiler output, or command output where practical.
7. Keep changes small and reversible. Do not fix unrelated bugs or broken tests.

## Close work

Use the Project Layer's end-work procedure when available. Before closure:

- verify the acceptance criteria and record evidence;
- rerun the post-change jscpd scan when a duplication-reducing refactor occurred;
- update the work-unit memory with handoff-critical facts, unresolved issues, and deferred scope;
- preserve closed history rather than overwriting it;
- run the Project Layer validator and required project checks;
- ask for user approval before closing, archiving, or creating follow-up backlog work when the local workflow requires it.
