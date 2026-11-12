# PL-20261112: Multi-Agent Roles and Delegation

- Status: Ready for closure — implementation and validation complete
- Work Unit: PL-20261112-multi-agent-roles-and-delegation
- Origin: [Backlog](../backlog/PL-20261112-multi-agent-roles-and-delegation.md)

## Progress

- [x] Draft active plan for review.
- [x] Review plan and approve implementation.
- [x] Implement roles, planning guidance, templates and upgrade path in verified slices.
- [x] Dogfood, resolve findings, review and present completion evidence.
- [ ] Obtain separate user approval for closure.

## Objective

Deliver discoverable reusable SDLC roles, project-specific extensions, and a supervisor-led active-plan workflow with an upgrade path for existing Project Layers.

## Specifications

- Route task-relevant system-wide and project roles through appropriate entrypoints; define purpose, authority, inputs, boundaries, handoff and evidence expectations. Support domain-specific refinements such as Unreal Engine.
- Deliver coding and documentation implementation, CI, dogfooding and review roles. Coding favors TDD and 100% code coverage; surface obstacles without silently relaxing the target. CI agents must not modify code, skip tests or reduce coverage to pass. Review covers DRY and appropriate tools, code and execution complexity, design, separation of concerns, security, readability, and contextual smells including polling, spin locks and deeply nested control flow.
- Update planning instructions and templates, especially `ACTIVE.md`, so agents starting active work load applicable Adaptive Agents and project guidance. Loading guidance is distinct from creating a Project Layer.
- Define a reusable supervisor role responsible for interpreting the user's objective, writing and maintaining `ACTIVE.md`, selecting applicable roles, coordinating their work, integrating results, and remaining accountable for the final outcome.
- When the host supports subagents and its rules and the user's instructions permit delegation, the supervisor should actively delegate suitable bounded work to subagents. Decompose work by clear ownership and dependencies, parallelize independent tasks when useful, and provide each agent its objective, role and relevant guidance, scope, constraints, expected evidence and handoff. Avoid conflicting edits and do not delegate away supervisor accountability. Record assignments and dependencies in the active plan.
- The supervisor **must** define plan-specific, observable done conditions and the evidence required to satisfy each one before execution. Define the validation and review gates, correction and rerun cycle, and genuine interruption conditions for the actual work; do not substitute a generic checklist for a concrete outcome.
- The supervisor **must continue the loop**: assign or perform the work, collect and evaluate results, correct or delegate every actionable in-scope failure or finding, and rerun affected checks and reviews. Repeat until every applicable done condition is satisfied with evidence. A subagent finishing, a passing subset of checks, a progress report, or a plausible next step is not a done condition. Do not stop merely to report while authorized, useful work remains.
- Stop before completion only for a genuine blocker that cannot be resolved within scope, a required user decision or approval, or a higher-priority constraint. First exhaust safe, authorized alternatives; then record what remains, evidence, and the specific unblock action. Preserve the separate user-approval boundary for closure after implementation and validation are complete. When subagents are unavailable or prohibited, execute applicable roles directly and record the fallback.
- Existing installations and Project Layers need an upgrade path for future activations, preserving project-owned guidance and active work and respecting comparison and approval-gated merges.

## Applicable Guidance

- [Architecture](../../ARCHITECTURE.md): ownership, routing, template upgrade and validation boundaries; update for changed invariants.
- [Manage planning](../../skills/manage-planning/SKILL.md): plan execution and closure.
- User-wide testing instructions and planning conventions, via the canonical Adaptive Agents index: test-first, coverage and DRY assessment.
- User-wide update-adaptive-agents skill, via the canonical index: guidance routing and template rules.
- User-wide upgrade-project-layer skill, via the canonical index: compare and preserve project ownership.

## Test Plan

For each executable slice, write a focused falsifiable test first, run it to confirm failure, implement the smallest change, rerun it, then broaden validation. Discover existing commands and coverage tooling; enforce 100% coverage for code written with the applicable CI gate. Record missing seams or coverage obstacles before continuing.

1. **Discovery:** Extend relevant validation tests, starting with `scripts/tests/test-project-layer.sh`, to check fresh bootstrap, required role routes, and broken or missing links; demonstrate failure cases.
2. **Upgrade:** Use isolated old-layer fixtures in relevant bootstrap/upgrade tests. Verify comparison, approved application, new-plan use, preservation of customized guidance and active plans, repeat-run idempotence, and failure paths. Identify exact tests and coverage commands before changes.
3. **Planning:** Test mechanically enforceable startup, handoff, and done-condition contracts; static checks alone cannot prove model behavior. Run focused suites, `bash .adaptive-agents/scripts/check-project-layer.sh`, and `bash scripts/check-adaptive-agents.sh` after changes.
4. **Behavioral dogfood:** Retain isolated fixtures and evidence for a realistic coding and documentation plan. Verify the supervisor selects and actually delegates suitable work when supported, assigns bounded ownership and dependencies, and integrates the results. Give it a fixable test failure and review finding and observe whether it continues without a new user prompt, corrects both, reruns affected checks, and stops only after its stated done conditions have evidence. Separately exercise a genuine blocker and verify an actionable handoff. Exercise subagent startup from bounded handoffs, CI failure reporting and its non-mutation/no-skipping boundaries, review of a known smell, no-subagent fallback, and activation on an upgraded old layer. Retain prompts, observable ordering, reports, diffs, commands and outcomes. An unavailable capability is a proof gap, not a pass.

## User-Facing Surface

- Surface: agent discovery, Project Layer activation and upgrade, and active-plan execution.
- Runtime scenario: fresh and upgraded isolated layers and supported agent sessions.
- Endpoint or runtime: Pending.

## User-Facing Validation

- Agent proof: Complete for local and supported-host scenarios; see Verification for retained evidence and limitations.
- Evidence: retain fixture paths, prompts, reports, observed behavior and validation output.
- User handoff: Pending.

## DRY Assessment

- Guidance/template slices: assessed existing authoritative rules and focused role links. Documentation-only changes do not require a scan; repeated template and dogfood-layer planning guidance is intentional and project-owned.
- Regression-test slice: jscpd 5.4.1, `npx --yes jscpd@5 --reporters console scripts/tests/test-project-layer.sh`: one Bash file, 664 lines, zero clones, exit 0. Existing fixture helpers are reused; preservation is asserted at the merge boundary. No executable production script was changed. This scan was performed during completion review, not before editing.

## Scope

- Implement the linked backlog scope, including templates, upgrade support, documentation and validation.
- Coordinate with [entrypoint reconciliation](../backlog/PL-20261027-adaptive-agents-entrypoint-reconciliation.md); do not redesign the overall entrypoint contract.
- Do not assume hosts provide subagents or overwrite existing project-owned layers.

## Acceptance Criteria

- [x] System and project role discovery, contracts and guidance layering cover the specified SDLC roles.
- [x] A supervisor role explicitly directs suitable subagent delegation when supported and permitted, bounded handoffs, coordination and integration; active-plan guidance covers startup, assignments, iterative correction, evidence-based completion, blockers and fallback.
- [x] Dogfood demonstrates that the supervisor continues the correction-and-verification loop without another user prompt until each plan-specific done condition has evidence, and stops early only for a genuine blocker or required approval with an actionable handoff.
- [x] Fresh and upgraded layers support new activations, preserve customizations and active work, and demonstrate repeatable upgrades.
- [x] Coding coverage, CI boundaries and review requirements match the specifications.
- [x] Focused tests, applicable validators, coverage gate and dogfood pass with retained evidence; proof gaps are explicit.
- [x] Each slice has a DRY assessment; resolve actionable in-scope findings and repeat affected checks.
- [ ] Obtain user approval before closure; completion review is recorded in memory.

## Decisions and Review Questions

- Standalone work unit, delivered in verifiable slices; no epic split assumed.
- Delegation default: proactively delegate suitable work when supported and permitted by host rules and user instructions; otherwise use the documented fallback.
- Roles live under user-wide `agents/`, with project refinements routed by the Project Layer. Existing layers adopt the template through reviewed, approved merges rather than wholesale copying. Fixtures and commands are recorded under Verification.

## Delegation

- Roles worker: own `agents/` role files; hand off changed paths, role contracts and link-validation evidence. Supervisor integrates before review.
- Upgrade investigator: read-only inspection of bootstrap, upgrade and tests; hand off path-specific upgrade strategy and evidence; no dependency on roles worker.
- Test worker: own `scripts/tests/test-project-layer.sh`; test fresh and upgraded fixtures, preservation and subsequent activation; hand off commands and results. Integrates with supervisor-owned template changes.
- Reviewer: read-only review of the diff and evidence; report actionable findings with paths and consequences. Supervisor corrects and requests re-review as needed.
- Supervisor: own planning and discovery integration, upgrade guidance, validation and behavioral dogfood; avoid overlapping worker edits.

## Done Conditions and Execution Loop

- Role and routing gate: each planned role is linked from the system index; project role routing works in fresh and approved upgraded layers; independent review reports no unresolved actionable in-scope findings.
- Upgrade gate: retained old-layer fixture shows reviewed application preserves customized instructions, active plan and memory, validates, and uses new guidance when a later plan is activated; repeat application and inspection are safe.
- Verification gate: focused tests and validators pass; coverage for any changed executable production code is measured at 100% with a gate, or a concrete unresolved obstacle is reported without claiming success.
- Behavioral gate: retained actual-session evidence shows bounded delegation, loading guidance, continuation after a fixable failure and review finding without another user prompt, corrections and reruns, CI boundaries, fallback and upgraded-layer activation. Report unavailable capability as a proof gap.
- Continue assigning, correcting and repeating affected checks until all gates are evidenced. Stop early only for a genuine blocker, required approval or higher-priority constraint after exhausting safe authorized alternatives; provide the specific unblock action. Closure remains separately approval-gated.

## Verification

- Repository health check: 278 passed, 0 failures, 1 Claude Code import warning; Git Bash with installed Python. Project Layer regression suite: 52 passed, including a simulated approved upgrade and future activation. No executable production code was changed; no new production coverage result is claimed.
- `integrated-proof/` in the session visualization workspace retains a fresh Project Layer, fixture and ordered host-ledger manifest. Parent-session subagents reported initial CI failure and independent review findings, then a bounded coding fix, full CI rerun (five tests, 100% statement and branch coverage), and clean re-review without another user prompt. The configured workflow commands passed locally; hosted CI was not run. A separate ephemeral CLI supervisor reported fresh-context delegation, but its event stream omits subagent handoffs, so that run's delegation is self-reported only.
- `dogfood-fresh/` retains an independently verified local configured CI gate covering both fixture production modules: six tests and 100% statement/branch coverage; an intentionally incomplete validation run failed the threshold at 38%. Hosted CI was not run.
- A read-only review found the upgrade test could erase a customization inside `Start Work`; the supervisor delegated a fix, the focused suite passed 52 checks, and the reviewer confirmed resolution. A separate blocker probe reported missing fixture CI configuration and requested a provider, run, revision and authorized evidence; it did not claim local tests proved external CI.
- `dogfood-old-upgrade/` retains a synthetic old layer, reviewed fixture-only patch, preserved active plan and guidance, and a subsequently authored new plan. A fresh agent used that layer's fallback and stopped with an evidence-backed blocker. The actual wrapper validator subsequently passed on the host; the dogfood agent itself ran only its embedded Python. Repeat inspection was stable and repeat application was demonstrated by the separate regression fixture.
- The evidence-review agent verified host event ordering and the local gate, distinguishing subagent reports from independent command transcripts. Hosted CI and the ephemeral CLI's internal handoffs remain unproven, not prerequisites for the local supported-host proof.

## Supporting Documents

- [Work-unit memory](PL-20261112-multi-agent-roles-and-delegation.memory.md)
