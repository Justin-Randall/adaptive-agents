# PL-0001: Implement the Project Layer

- Status: Active
- Origin: Direct

## Objective

Implement, document, validate, and dogfood an Adaptive Agents Project Layer that provides project-owned guidance and indexed planning without requiring ordinary root integration files.

## Scope

- Maintain a canonical reusable template under `templates/project-layer/`.
- Provide model-led bootstrap and upgrade skills backed by deterministic Bash mechanics.
- Discover `.adaptive-agents/INDEX.md` through installed user-wide guidance.
- Validate link reachability, planning identity, active support documents, and lifecycle layout.
- Track this repository's dogfood Project Layer as a shared example.

## Acceptance Criteria

- [x] The canonical Project Layer template and project-local skills area exist.
- [x] Bootstrap works in tracked, clone-local exclude, and repository-wide ignore modes.
- [x] Upgrade inspection is read-only and reports a fresh layer as an exact match.
- [x] Negative validator cases reject structural and lifecycle defects.
- [x] Generated VS Code bootstrap content includes Project Layer discovery.
- [x] Full repository and dogfood validation succeeds.
- [x] Retrospective capture chooses Project Layer or user-wide scope before target type.
- [x] Project Layers provide routed local retrospectives, memory, skills, instructions, and playbooks.

## Progress

- [x] Create and validate the canonical template graph.
- [x] Add bootstrap skill and deterministic script.
- [x] Add upgrade inspection and approval-gated workflow.
- [x] Update user-wide discovery, boundaries, routing, and documentation.
- [x] Bootstrap and expose this repository's dogfood layer for source control.
- [x] Add focused negative validator tests.
- [x] Validate generated installer content and complete final checks.
- [x] Add scope-aware retrospective capture, triage, promotion, and validation.

## Decisions

- The feature is named Adaptive Agents Project Layer and uses `.adaptive-agents/`.
- Installed Adaptive Agents is required; bootstrap does not add root `AGENTS.md` or editor settings.
- The canonical template includes routed instructions, skills, planning, lifecycle playbooks, and validation.
- One `PL-####` namespace spans backlog, active, and closed work.
- This repository's dogfood layer is tracked and shared.
- Project-specific retrospective learning remains in the Project Layer by default; user-wide escalation is separate, sanitized, evidence-backed, and approval-gated.

## Verification

- Canonical template validator: passed.
- Bootstrap persistence fixtures: passed after correcting clone-local Git path resolution.
- Upgrade inspection fixture: passed with zero differences.
- Project Layer validator regression suite: 10 passed, 0 failed.
- Generated VS Code bootstrap fixture: passed with additive settings preserved.
- Fresh Project Layer `0.2.0` bootstrap and upgrade comparison: passed with zero differences.
- Canonical repository checker: 93 passed, 0 failed, 0 warnings.
- Editor diagnostics: clean.

## Supporting Documents

- [Active memory](MEMORY.md)
