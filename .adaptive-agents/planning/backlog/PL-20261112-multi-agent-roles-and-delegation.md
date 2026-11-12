# Backlog: Multi-Agent Roles and Delegation

Plan: PL-20261112-multi-agent-roles-and-delegation

Status: Ready for closure

Readiness: Ready: implementation and local verification complete; closure approval pending.

Test approach: Verify role discovery, active-plan startup guidance, and delegation handoffs across system-wide and generated Project Layer guidance, including unavailable-subagent fallback and applicable validators; define focused checks during planning.

## Objective

Make Adaptive Agents useful to lead agents and delegated agents by delivering discoverable, reusable SDLC roles and supporting project-specific agent guidance.

## Problem Spec

Existing guidance primarily addresses an agent working directly with the user. Explicit subagent requests work in the user's Codex experience, but the guidance graph does not yet define a cohesive way to discover roles, convey relevant context and boundaries to delegated agents, or integrate their results. The system-wide agents directory exists, while the Project Layer template has no agent routing. Planning templates could also make delegation and loading Adaptive Agents guidance more explicit when an active plan is executed.

## Scope

In scope:

- Explore focused system-wide roles and project-specific roles or behaviors, including their precedence and discovery through appropriate entrypoints.
- Define a delegation and handoff approach, including task context, authority, verification, and behavior when subagents are unavailable.
- Explore planning-template changes, especially for `ACTIVE.md`, that make delegation explicit and instruct agents starting active work to ensure Adaptive Agents guidance is loaded and applicable project guidance is in context. Account for both lead agents and delegated agents.
- Distinguish loading an existing installation from creating a Project Layer, which requires its own approved bootstrap workflow.
- Provide an upgrade path for existing installations and Project Layers so newly activated plans can use updated templates and instructions; preserve existing project-owned guidance and active work.
- Deliver reusable implementation roles starting with coding and documentation, alongside CI execution, dogfooding, and change-review roles. Define how an orchestrating supervisor plans and coordinates their iterative implementation-and-feedback loop in `ACTIVE.md`.
- Coding implementation guidance should prefer TDD and target 100% code coverage, reflecting the user's established requirement; define how to surface and handle genuine obstacles without silently relaxing the target.
- CI agents must not modify code, skip tests, or reduce coverage to obtain a passing result; report failures and evidence to the supervisor.
- Review agents should assess DRY design using available tools such as jscpd where appropriate, code and execution complexity, separation of concerns, security, readability, and smells such as polling, spin locks, and deeply nested arrow-shaped control flow, considering context.
- Establish extensible general SDLC practices and a way to layer domain- or project-specific implementation guidance (for example Unreal Engine) onto generic roles without duplicating them.
- Update planning guidance and templates so the model defines plan-specific, evidence-based completion and loop exit conditions when writing `ACTIVE.md`. Direct the supervisor to continue resolving in-scope findings and rerunning relevant checks until those conditions are met, while identifying genuine blockers and required approval boundaries rather than stopping for routine progress reports.
- Define the supervisor role and proactive delegation of suitable bounded work when host capabilities, host rules, and user instructions permit, with a fallback when subagents are unavailable or prohibited.
- Assess template, upgrade, documentation, and validation implications; split into independently actionable work if needed.

Deferred:

- Assuming a specific host's agent API or guaranteeing that subagents are available.
- Activating a plan as part of creating this backlog item.

## Related Work

- [Entrypoint reconciliation](PL-20261027-adaptive-agents-entrypoint-reconciliation.md) addresses the broader authority and routing contract; coordinate any overlapping entrypoint changes.
