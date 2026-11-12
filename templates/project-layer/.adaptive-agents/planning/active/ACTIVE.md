# {{ACTIVE_PLAN_ID}}: {{ACTIVE_PLAN_TITLE}}

- Status: Active
- Work Unit: {{ACTIVE_WORK_ID}}
- Origin: Direct

## Progress

> Keep this checklist up to date as you work. After each meaningful change, check off completed stages, add newly discovered work, remove eliminated work, and adjust plan-specific items so it accurately reflects what remains to deliver.

- [ ] Confirm the initial implementation steps.
- [ ] Perform the work.
- [ ] Record verification evidence.

## Objective

Establish the initial approved work for this Project Layer.

## Specifications

Spec-Driven Development (SDD): Define the feature or change precisely enough to drive implementation. Use the sub-sections below as needed; omit any that are not relevant to this plan.

### Problem Spec

The pain point, gap, or opportunity being addressed. Establishes context so every subsequent spec item can be evaluated against the problem it solves.

### Feature Specs

What the feature does. Behavioral descriptions, user-facing behavior, expected outcomes.

### Interface / Contract Specs

API surfaces, function signatures, event contracts, configuration schemas, file formats. Concrete enough to write tests against.

### Data Model Specs

Types, structures, schemas, state machines, persistence shapes. Concrete enough to validate before writing implementation code.

### Behavioral Specs

Edge cases, error handling, state transitions, concurrency assumptions, ordering guarantees, idempotency requirements.

## Applicable Guidance

Reference the project rules that govern execution of this plan. List each with a short description and path to its authoritative source (instruction, skill, playbook, etc.). Omit this section if no project-specific rules apply beyond the default user-wide guidance.

- `path/to/rule` — one-line description of what it requires.

## Supervision and Delegation

Before work begins, ensure the installed Adaptive Agents entrypoint, its index, and applicable project guidance are in context. Discover the supervisor and relevant reusable and project roles. Loading an existing installation is not authorization to bootstrap a Project Layer.

When the host and user instructions permit, delegate suitable bounded work to subagents. Record role, scope, ownership, dependencies, relevant guidance, expected evidence, and handoff for each assignment; parallelize independent work when useful. The supervisor integrates results and remains accountable. If delegation is unavailable or prohibited, record the fallback and perform the relevant roles directly.

## Done Conditions and Execution Loop

Define observable plan-specific outcomes and evidence for each gate before execution, including applicable implementation, tests, coverage, dogfood, and review. The supervisor must repeat assignment, implementation, validation, review, correction, and affected reruns until all applicable conditions are met with evidence. Subagent completion, partial checks, and progress reports are not completion; do not stop while useful authorized work remains.

Stop early only for a genuine blocker, required user decision or approval, or higher-priority constraint. Exhaust safe in-scope alternatives first, then record the outstanding work, evidence, and specific action required. Follow the separate closure approval process after work is complete.

## Test Plan

Define the tests that prove this plan's specs, written before implementation per the `instructions/testing.instructions.md` test contract:

- Methodology and tooling for the project's language (discovered, not prescribed).
- Focused tests written first — each falsifiable, covering happy and failure paths.
- Coverage: 100% of the code written to satisfy the tests, enforced by a CI coverage gate.
- Run command for the focused loop.
- Research plans: `research — no tests`.

## User-Facing Surface

- Surface: `<affected user workflow or N/A>`
- Runtime scenario: `<user workflow in the project's actual runtime or N/A with reason>`
- Endpoint or runtime: `Not run`

## User-Facing Validation

- Agent proof: `Pending`
- Evidence: `<endpoint or runtime, scenario, observed result, and artifacts when available>`
- User handoff: `Pending`

## DRY Assessment

Record one assessment for every implementation slice before editing it. Follow the user-wide Planning Conventions for scan triggers and the distinction between a mandatory assessment and a risk-based jscpd scan.

- Status: `Required` | `Not required` | `Existing baseline`
- Scope: path or implementation slice being assessed.
- Command: the project-approved jscpd command, if a scan is run.
- Decision: why a scan is required or not required.
- Result: clone summary, verification result, or reason deferred.
- Intentional/deferred duplication: explain any reported duplication that remains.

Research plans may record `DRY assessment — not applicable` when no implementation code is modified.

## Scope

- Define the bounded work to perform.
- Keep newly discovered out-of-scope work separate from this plan.

## Acceptance Criteria

- [ ] The approved objective is complete.
- [ ] Relevant validation succeeds.
- [ ] Every implementation slice has a recorded DRY assessment.
- [ ] Required duplication scans were run with the project-approved command, and accepted or deferred duplication is documented.
- [ ] Deferred discoveries have been proposed for backlog handling.

## Decisions

- None yet.

## Verification

- Not run.

## Supporting Documents

- [{{ACTIVE_WORK_ID}} memory]({{ACTIVE_WORK_ID}}.memory.md)
