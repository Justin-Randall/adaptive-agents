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

## Test Plan

Define the tests that prove this plan's specs, written before implementation per the `instructions/testing.instructions.md` test contract:

- Methodology and tooling for the project's language (discovered, not prescribed).
- Focused tests written first — each falsifiable, covering happy and failure paths.
- Coverage: 100% of the code written to satisfy the tests, enforced by a CI coverage gate.
- Run command for the focused loop.
- Research plans: `research — no tests`.

## User-Facing Surface

- Browser surface: `<affected browser workflow or N/A>`
- Playwright scenario: `<deployed user workflow or N/A with reason>`
- Deployment endpoint: `Not run`

## Browser Dogfood

- Agent proof: `Pending`
- Evidence: `<URL, scenario, observed result, and artifacts when available>`
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
