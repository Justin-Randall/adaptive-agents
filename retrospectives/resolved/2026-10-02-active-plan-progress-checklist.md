# Retrospective: Active Plans Need Progress Checklists

- Date: 2026-10-02
- Status: Resolved
- Scope: User-wide
- Session or task: Activating a backlog item and preparing its active implementation plan

## Observation

An active plan was created with metadata, objective, implementation slices, acceptance criteria, and a test plan, but no progress checklist immediately after the metadata. The user identified that an active plan should make completed, pending, and later execution work scannable near the top.

## Evidence

- The active plan initially placed its objective directly after the metadata.
- The plan contained detailed implementation and validation sections but did not distinguish plan-authoring completion from review, implementation, validation, and delivery status.
- A progress checklist was added after the metadata once the gap was identified.

## Impact

Without a top-level progress checklist, active-plan status requires parsing the full document and can blur the boundary between planning completion and implementation progress. A consistent checklist would improve handoffs and make review state visible across projects.

## Scope Decision

- Candidate: User-wide
- Rationale: The user explicitly identified this as an Adaptive Agents-layer issue, and the missing convention can affect active plans across unrelated projects.
- Project Layer considered: Project-local guidance would not address the reusable active-plan activation convention.

## Proposed User-Wide Target

- `skills/`

Update the planning or active-plan activation guidance to require a short progress checklist immediately after active-plan metadata. The checklist should cover planning, review, implementation, focused/full validation, and delivery or dogfooding as applicable.

## Design Constraints

- Track lifecycle stages rather than repeating acceptance criteria or the detailed test plan.
- Do not require a percentage-complete field; checked stages provide sufficient status without false precision.
- Allow plan-specific stages and mark inapplicable stages as `N/A` or omit them, especially for research and maintenance work.
- Keep the checklist scannable and separate from detailed implementation tasks.
- Define completion stages distinctly so implementation completion does not imply validation or delivery completion.
- Do not add document-level provenance or bookkeeping solely for validation.
- Older or unversioned documents must either be semantically migrated by the responsible model to the current contract or fail validation; there is no indefinite advisory-conformance state.
- Validator failures should identify the missing structural requirement clearly enough for the model to repair the document and rerun validation.

## Promotion Decision

- Status: Captured
- Decision: Await triage and explicit approval before changing durable guidance.
- Rationale: The convention is supported by this workflow, but existing active-plan variants should be reviewed before selecting the exact template or skill change.

## Promotion Links

- None yet.

## Resolution

- Status: Resolved
- Verification: The canonical and dogfood Project Layers require the `## Progress` checklist at template version `0.7.2`; the checklist instructs models to keep it current, add newly discovered work, and remove eliminated work.
- Evidence: [Completed maintenance packet](../../.adaptive-agents/planning/closed/PL-20261002-progress-checklist-maintenance-guidance/PL-20261002-progress-checklist-maintenance-guidance.sdd.md), preserving the [original migration packet](../../.adaptive-agents/planning/closed/PL-20261002-active-plan-conformance-migration/PL-20261002-active-plan-conformance-migration.sdd.md).
- Validation: `bash scripts/test-project-layer.sh` — 34 passed; the focused Project Layer validator passes with 0 failures; full repository validation passes with 241 passed, 0 failures, and 0 warnings.

---

*After triage or implementation verification, move the note to `promoted/`, `deferred/`, `rejected/`, or `resolved/` and update its status and evidence.*
