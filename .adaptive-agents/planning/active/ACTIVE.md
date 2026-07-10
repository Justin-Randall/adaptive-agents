# PL-20260710T110000Z: Add Spec-Driven Development (SDD) Output to Planning Artifacts

- Status: Active
- Origin: Direct

## Objective

Evolve the active plan template to include structured Spec-Driven Development (SDD) sections that make feature definitions, interface contracts, and implementation plans clearer and more actionable before work begins.

## Specifications

### 1. SDD Section Structure

Each active plan SHOULD contain a `## Specifications` section (after `## Objective`, before `## Scope`) with sub-sections that define the feature or change precisely enough to drive implementation.

Standard sub-sections:

- **Problem Spec** — The pain point, gap, or opportunity being addressed. Establishes context so every subsequent spec item can be evaluated against the problem it solves.
- **Feature Specs** — What the feature does. Behavioral descriptions, user-facing behavior, expected outcomes.
- **Interface / Contract Specs** — API surfaces, function signatures, event contracts, configuration schemas, file formats. Concrete enough to write tests against.
- **Data Model Specs** — Types, structures, schemas, state machines, persistence shapes. Concrete enough to validate before writing implementation code.
- **Behavioral Specs** — Edge cases, error handling, state transitions, concurrency assumptions, ordering guarantees, idempotency requirements.

### 2. Spec-Level Acceptance

Acceptance criteria in the plan MUST map to spec items. Each `[ ]` in `## Acceptance Criteria` should trace back to a named spec rule or contract.

### 3. Template Evolution

The canonical template at `templates/project-layer/.adaptive-agents/planning/active/ACTIVE.md` MUST be updated to include:

- The `## Specifications` section as an SDD-ready placeholder with instructions for how to fill it.
- The `## Applicable Guidance` section where project rules are captured with short descriptions and links to authoritative sources.

### 4. This Plan's Own Specs

This plan serves as the first dogfood of the SDD format. The spec items below define the feature being implemented.

#### Problem Spec

Active plans lacked a structured way to define *what* a feature should do before implementation began. Requirements lived in `## Objective` (too high-level) and loose acceptance criteria. This caused ambiguity, scope creep, and inconsistent handoff. The SDD section solves this by giving a precise, repeatable specification format embedded in the plan itself.

#### Feature Specs

- The SDD `## Specifications` section MUST appear in active plans after `## Objective` and before `## Scope`.
- It MUST include at minimum a Problem Spec and Feature Specs; Interface/Contract, Data Model, and Behavioral Specs are added as the feature requires.
- The canonical template MUST include all five sub-sections as placeholder guidance.
- A `## Applicable Guidance` section MUST appear after `## Specifications` and before `## Scope`, capturing relevant project rules with short descriptions and links.

#### Interface / Contract Specs

N/A — the SDD feature is purely about planning artifact structure, not runnable code.

#### Data Model Specs

N/A — no runnable schemas or persistence.

#### Behavioral Specs

- The SDD section is a template convention, not a validation gate. Plans MAY omit sub-sections that are N/A.
- Acceptance criteria MUST trace to specific spec items — each AC should reference a named spec rule or sub-section.

## Applicable Guidance

These rules govern execution of this plan.

- `instructions/global.instructions.md` — default engineering standards: testability, injectable dependencies, small reversible changes, verification discipline, retrospective checkpoint.
- `instructions/tdd.instructions.md` — prefer test-driven development for production behavior changes: falsify first, then implement, tight red-green-refactor loop.
- `instructions/coding.instructions.md` — testable code, injectable dependencies, prefer interfaces/adapters, don't invent APIs, preserve project style.
- `instructions/repository-boundaries.instructions.md` — know which repo you're in; don't copy Adaptive Agents structure into other projects.
- `instructions/command-failure-pivot.instructions.md` — when a terminal command fails, pivot rather than repeating the same command unchanged.
- `instructions/temp-artifact-hygiene.instructions.md` — clean up temporary files and diagnostic artifacts after use.

## Scope

- Add a `## Specifications` section to the canonical active plan template (`templates/project-layer/.adaptive-agents/planning/active/ACTIVE.md`).
- Add a `## Specifications` section to this repository's dogfood `ACTIVE.md`.
- Update `planning/INDEX.md` and `active/MEMORY.md` for the new active plan.
- Define the SDD section conventions and sub-section roles.
- Dogfood the format on the current work (this plan).
- Update the canonical template MEMORY.md if needed.
- **Out of scope**: Separate `.sdd.md` files, external spec tooling, CI enforcement, or spec-to-test code generation. These may be deferred for future backlog items.

## Acceptance Criteria

- [x] `## Specifications` section exists in the canonical template's `ACTIVE.md` with SDD placeholder guidance. *(Spec §3)*
- [x] `## Specifications` section exists in this repository's dogfood `ACTIVE.md` and is populated for PL-20260710T110000Z. *(Spec §4, Feature Specs item 1)*
- [x] The `## Specifications` section has clearly documented sub-section roles (Problem Spec, Feature, Interface/Contract, Data Model, Behavioral). *(Spec §1)*
- [x] `## Applicable Guidance` section exists in the canonical template as an SDD-ready placeholder. *(Spec §3)*
- [x] `## Applicable Guidance` section exists in this repository's dogfood `ACTIVE.md` and is populated for PL-20260710T110000Z. *(Spec §4, Feature Specs item 4)*
- [x] Acceptance criteria in this plan trace to specific items in the Specifications section. *(Spec §2; Spec §4, Behavioral Specs item 2)*
- [x] The canonical template and dogfood copy are kept in sync. *(Spec §4, Feature Specs item 3)*
- [x] Repository checker passes (link reachability, planning identity). *(Spec §4, Behavioral Specs — template convention verified)*

## Progress

- [x] Draft the SDD specification structure and conventions.
- [x] Update the canonical template `ACTIVE.md` with SDD section and placeholder guidance.
- [x] Update the dogfood `ACTIVE.md` with PL-20260710T110000Z's SDD content.
- [x] Update `planning/INDEX.md` to reference PL-20260710T110000Z.
- [x] Update `active/MEMORY.md` with cross-session SDD conventions.
- [x] Add Problem Spec as the first SDD sub-section (canonical template + dogfood).
- [x] Add `## Applicable Guidance` section to the canonical template.
- [x] Add `## Applicable Guidance` section to dogfood plan, populated with project rules.
- [x] Update `manage-planning` SKILL.md with Execute Work section that captures rules into the plan.
- [x] Run repository checker to validate link reachability.

## Decisions

- SDD lives as a section inside `ACTIVE.md`, not as a separate file type — keeps plans self-contained.
- The `## Specifications` section goes between `## Objective` and `## Scope` — the objective frames the goal, specs define it precisely, scope bounds it.
- Standard SDD sub-sections begin with **Problem Spec** (establishes context), followed by Feature, Interface/Contract, Data Model, and Behavioral Specs as needed.
- Acceptance criteria trace to spec items — each AC should reference a named spec rule or sub-section.
- This plan dogfoods its own SDD format — the `## Specifications` block above IS the spec for this feature.
- Plans capture relevant project rules in a `## Applicable Guidance` section with short descriptions and links to authoritative sources, so agents executing the plan see the rules directly.

## Verification

- Repository checker: 93 passed, 0 failures, 0 warnings.
- Project Layer validator regression suite: 10 passed, 0 failures.
- Editor diagnostics: clean.

## Supporting Documents

- [Active memory](MEMORY.md)
