# Retrospective: Project-layer dogfood instructions were present but not enforced

- Date: 2026-08-27
- Status: Promoted
- Scope: User-wide
- Session or task: User-facing provider-management regression

## Observation

A user-facing change was reported as fixed after automated frontend and backend tests passed, but the project layer's required deployment and live-browser dogfood gate had not been followed. The relevant project instructions were present and explicit, but they were not loaded before implementation and were not enforced before the completion claim.

## Evidence

- The project layer contains a development workflow that requires deployment through the production path and testing at the deployed application endpoint.
- Its completion gate explicitly says that tests, builds, diagnostics, and source inspection cannot substitute for deployed dogfooding.
- The project layer also defines the dogfood workspace, model, deployment command, and evidence that must be recorded.
- A later user question exposed that the live workflow had not been exercised, despite the implementation and automated tests being reported as complete.
- In a subsequent cancellation-regression session, the agent again claimed the bug was fixed after package tests passed and the full CI run reported passing tests, without exercising the deployed browser workflow; the user then explicitly asked whether the claim had been dogfooded.
- The failure therefore has two contributing points: project-layer discovery was not completed during task routing, and completion reporting did not require a machine-checkable or agent-visible dogfood checkpoint.

## Impact

Project-specific quality gates can be bypassed even when the implementation is correct and automated validation is green. This produces completion claims that are stronger than the available evidence and leaves user-facing regressions undiscovered until the user tests them.

## Scope Decision

- Candidate: User-wide
- Rationale: The failure mode is applicable to any project with layered instructions, local acceptance gates, or deployment-specific validation. It concerns agent routing and evidence discipline rather than one product's provider workflow.
- Project Layer considered: The immediate project-layer retrospective already records the local incident. A separate user-wide note is justified because the routing and completion-reporting failure can recur in unrelated repositories with their own local gates.

## Proposed User-Wide Target

Where this might belong if promoted:

- `instructions/` for a default requirement to discover and load applicable project-local instructions before implementation.
- `playbooks/` for a pre-completion gate that requires explicit evidence for user-facing workflows and distinguishes automated validation from deployed dogfood.
- `prompts/` or session-start tooling if discovery must be made visible and deterministic at task start.

## Promotion Decision

- Status: Promoted
- Decision: Add a user-wide fallback for selecting runtime dogfood when no project-specific or stack-specific validation guidance applies.
- Rationale: Global instructions route agents through Project Layer guidance, the canonical Project Layer workflow requires user-facing runtime validation, and a cross-project fallback now covers user-facing work without applicable runtime instructions.

## Promotion Links

- [Coding instructions](../../instructions/coding.instructions.md) — defines the evidence-based runtime dogfood fallback and when to ask the user or leave validation pending.
- [Global instructions](../../instructions/global.instructions.md) — routes agents to project-local instructions and planning context.
- [Project Layer planning skill](../../templates/project-layer/.adaptive-agents/skills/manage-planning/SKILL.md) — requires runtime scenarios and evidence for user-facing changes.

---

*After triage, move this note to `promoted/`, `deferred/`, or `rejected/` and update its status and promotion links.*
