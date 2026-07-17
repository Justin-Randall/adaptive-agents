# Adaptive Agents Architecture

This document defines the project-specific boundaries and invariants that should guide consequential changes to the Adaptive Agents repository. It describes ownership and routing, not a complete file inventory.

## System Purpose

Adaptive Agents is a versioned user-wide knowledgebase for coding agents. It stores reusable instructions, skills, memory, prompts, playbooks, retrospectives, schemas, agents, and integration adapters. It is not an application runtime and must not leak its user-wide content into unrelated project repositories.

## Entrypoints And Routing

`AGENTS.md` is the canonical agent entrypoint and stable statement of repository role and boundaries. `INDEX.md` is the user-wide routing map. Agents start at the entrypoint, follow the index, and load only the guidance relevant to the current task.

`instructions/global.instructions.md` is the default engineering-guidance router. Detailed rules belong in focused instruction files, skills, or playbooks rather than accumulating in entrypoints.

## Guidance Ownership

The repository root owns reusable user-wide guidance. Raw observations begin in `retrospectives/inbox/`; durable guidance is promoted only through explicit review and approval.

`.adaptive-agents/` is this repository's dogfood Project Layer. It owns project-specific instructions, planning, memory, retrospectives, skills, and playbooks. Its guidance may be more specific than user-wide guidance, but it must not silently become a user-wide rule.

`templates/project-layer/` is the canonical source for newly bootstrapped Project Layers. The dogfood layer and existing installed layers are project-owned instances, not generated mirrors. Template upgrades require an explicit comparison and approval-gated merge.

## Integration Boundary

Tool integrations are adapters from each tool's native instruction-discovery, lifecycle, and access mechanisms to canonical routed guidance. They may install minimal pointers, hooks, settings, or commands required by the tool, but they must not copy the guidance corpus or create competing sources of truth. Deterministic lifecycle hooks should inject canonical file contents directly rather than instructing a model to load or execute mandatory startup behavior.

Installers must preserve unrelated user configuration, deduplicate managed values, support safe repeated execution, and verify behavior through fresh sessions or equivalent tool-native checks. A successful file write or installer exit is not sufficient proof that a tool loaded the guidance.

## Adaptation Lifecycle

The learning flow is capture, triage, review, and approved promotion. Project-specific observations remain in the Project Layer. Cross-project guidance belongs at the repository root only when broader intent or evidence supports it. Raw retrospectives are evidence, not active instructions.

Planning artifacts coordinate work but do not override checked-in instructions or architectural invariants. Each active task has one canonical `PL-YYYYMMDD-descriptive-slug` work-unit identity. Its plan and curated memory preserve that identity through closure; reopened work receives a new identity and links to immutable prior context rather than rewriting it. Active plans should reference the specifications and supporting context needed for implementation without duplicating durable guidance.

## Validation Boundary

Deterministic scripts validate repository structure, routing, links, metadata, installer behavior, and Project Layer contracts. Focused tests should falsify the changed behavior first; the repository health checker provides broad completion validation.

Generated files and temporary diagnostics are disposable outputs. Canonical guidance, templates, schemas, and validators are reviewed source artifacts.

## Architectural Invariants

- Keep one canonical user-wide entrypoint: `AGENTS.md`.
- Route discovery through indexes; do not require eager loading of the full repository.
- Keep user-wide and project-specific ownership separate.
- Keep canonical templates separate from installed Project Layer instances.
- Prefer tool-native references to generated copies of guidance.
- Preserve user configuration and same-version idempotency in installers.
- Require explicit approval before promoting retrospective evidence into durable guidance.
- Keep validation deterministic, read-only where practical, and scoped to observable contracts.

## Change Rule

Update this document in the same change when repository ownership, canonical routing, integration boundaries, lifecycle stages, template ownership, or validation responsibilities change. Implementation details and file inventories belong in their owning documents unless they establish a durable architectural boundary.

## Non-Goals

This document does not replace `AGENTS.md`, `INDEX.md`, user-facing setup documentation, task plans, detailed instruction files, or implementation tests. It should remain concise enough to read before consequential project changes.
