# PL-20260731: Make Tests Part of Planning Guidance

- Status: Active
- Work Unit: PL-20260731-make-tests-part-of-planning
- Origin: Direct

## Objective

Make tests a first-class part of planning guidance: a lean user-wide test contract, a required `## Test Plan` in active plans (validator-enforced), a one-line `Test approach` in backlog items, and test-first + CI-ask behavior in the manage-planning skill — across the canonical template and the live Project Layer, with deterministic verification.

## Specifications

### Problem Spec

The planning chain (backlog format, ACTIVE.md SDD template, planning-conventions.md, manage-planning skill, epic template) never requires or mentions defining tests at planning time; TDD guidance only governs implementation. Graph analysis confirms zero links between planning artifacts and testing guidance. Result: tests are discovered mid-implementation instead of planned up front, so testability, seams, and failure paths surface too late.

### Feature Specs

1. NEW lean `instructions/testing.instructions.md` — authoritative test contract: falsifiable proof, failure paths, tests before feature work (surfacing seams/mocks/DI early), 100% coverage of code written, fast tests, language-appropriate methodology (discovered, not prescribed), CI with ask-if-missing. One rule per line, deeper context behind links, est. < ~800 tokens.
2. `ACTIVE.md` template gains `## Test Plan` (between `## Applicable Guidance` and `## Scope`); `check-project-layer.sh` (both copies) requires it for active plans ("No Active Plan" placeholder exempt).
3. Backlog items carry a one-line `Test approach` (research items: "research — no tests"); activation expands it into the Test Plan.
4. `manage-planning` skill (live + template): write Test Plan at activation from the backlog line; check Current project for CI and ask if absent; define focused failing tests first and record surfaced testability issues in `## Decisions`.
5. Routing: `instructions/INDEX.md` gains rows for `testing.instructions.md` and `planning-conventions.md`; `global.instructions.md` read list gains `testing.instructions.md`; `instruction-load-routes.json` `non_trivial_coding` profile gains `testing.instructions.md`; baseline regenerated.
6. `tdd.instructions.md` gets a pointer to the contract plus one planning-time line. `planning-conventions.md` gains a short `## Test Planning` section.
7. Template sync: template `manage-planning` copy synced to live (epic-split step) as part of the edit; `template.json` bumped 0.5.1 → 0.5.2.

### Interface / Contract Specs

- Validator contract: active plans (non-"No Active Plan") MUST include a heading matching `^## Test Plan\b` in `planning/active/ACTIVE.md`. Research plans keep the section with "research — no tests".
- Routes manifest: `instructions/testing.instructions.md` added to `non_trivial_coding` profile, classification `profile`, adjacent to `tdd.instructions.md`.

### Data Model Specs

N/A — no runnable schemas or persistence.

### Behavioral Specs

- Every edited guidance file stays lean: rule + link, no tool enumeration (discovery over prescription).
- CI ask-if-missing is behavioral (manage-planning), not a validator gate.
- Research plans carry the Test Plan section with exemption text — no special validator exemption logic.
- Backlog `Test approach` lines for the 7 existing items: all research → "research — no tests".

## Test Plan

Methodology: TDD — focused failing validator tests first via `scripts/test-project-layer.sh` (reuse `new_fixture`/`expect_failure`). What they falsify: (a) bootstrapped ACTIVE.md with Test Plan passes; (b) Test Plan section stripped → validator fails with "ACTIVE.md must include a ## Test Plan section"; (c) "No Active Plan" placeholder passes. Regression: `scripts/test-instruction-load-budget.py`. Coverage: the changed production surface (check-project-layer.sh + routes) is covered by these tests; CI gate is the repo's existing `static-validation.yml`.

## Applicable Guidance

- `instructions/testing.instructions.md` — the test contract this plan dogfoods (created by this plan).
- `instructions/global.instructions.md` — user-wide engineering standards, verification discipline.
- `instructions/tdd.instructions.md` — focused failing tests before production changes.
- `instructions/coding.instructions.md` — small reversible changes; preserve project style.
- `instructions/planning-conventions.md` — planning conventions and test-planning section (updated by this plan).
- `skills/update-adaptive-agents/SKILL.md` — durable guidance edits, promotion rules, validation.
- `skills/manage-planning/SKILL.md` — activation lifecycle, ACTIVE.md maintenance.

## Scope

- Create `instructions/testing.instructions.md`; update `tdd.instructions.md`, `global.instructions.md`, `instructions/INDEX.md`, `planning-conventions.md`, `instruction-load-routes.json`, `instruction-load-baseline.json`.
- Update `templates/project-layer/.adaptive-agents/planning/active/ACTIVE.md`, `.../scripts/check-project-layer.sh`, `.../skills/manage-planning/SKILL.md`, `templates/project-layer/template.json`.
- Update `.adaptive-agents/skills/manage-planning/SKILL.md`, `.adaptive-agents/scripts/check-project-layer.sh`, `.adaptive-agents/planning/backlog/*.md`.
- Add validator cases to `scripts/test-project-layer.sh`.

Out of scope: repo-health-level Test Plan check (`check-adaptive-agents.sh`), SDD schema, graphify refresh (user decision on derived artifact).

## Acceptance Criteria

- [x] `## Test Plan` required for active plans by both `check-project-layer.sh` copies; "No Active Plan" placeholder exempt; regression tests cover all three cases.
- [x] Testing contract exists in `instructions/testing.instructions.md`, lean (355 est. tokens, < ~800 target), and is routed (global read list, instructions/INDEX.md, routes manifest).
- [x] Backlog items and ACTIVE.md template carry test-planning fields; manage-planning skill (both copies, synced) has test-first + CI-ask behavior.
- [x] Template version bumped 0.5.2; instruction-load baseline regenerated; full verification suite passes.

## Progress

- [x] Confirm the initial implementation steps.
- [x] Perform the work.
- [x] Record verification evidence.

## Decisions

- New dedicated lean `testing.instructions.md` (vs folding into `tdd.instructions.md`) — routing stability + discoverability; INDEX already anticipated a testing instruction.
- CI ask-if-missing is behavioral, not a validator gate — CI config is project-specific, lives in the Current project repo.
- Lean-footprint principle: guidance carries only enough detail to instruct; deeper context behind links; instruction-load gate is the enforcement.
- Template copy synced to live copy (existing drift: epic-split step) as part of the edit.
- Activating a plan requires adding its work-unit memory to the `adaptive_agents_planned_change` profile in `instruction-load-routes.json` (pre-existing contract enforced by `_validate_active_memory`).
- **Backward compatibility (post-review addition)**: the `## Test Plan` validator check is version-gated (`templateVersion >= 0.5.2`), so older layers adopting the new validator keep validating; documented in `skills/upgrade-project-layer/SKILL.md`; live layer bumped to 0.5.2.
- **Anchored empty-plan detection (post-review addition)**: the upgrade inspector and both validators now detect an empty plan via `active_text.startswith("# No Active Plan")` instead of a substring check — quoted prose like "No Active Plan" in an active plan no longer misdetects it as empty.

## Verification

- `bash scripts/test-project-layer.sh` — 20 passed, 0 failures (includes 3 Test Plan cases + 2 backward-compat cases: 0.5.1-no-TestPlan passes, missing-version passes).
- `bash scripts/check-instruction-load-budget.sh --check` — passed; `--report` shows `testing.instructions.md` at 355 est. tokens; startup 4,407/32,768 (13.4%).
- `python scripts/test-instruction-load-budget.py` — 31 tests OK.
- `bash scripts/check-adaptive-agents.sh --verbose` — 180 passed, 0 failures, 3 pre-existing environment warnings (CLAUDE.md/GEMINI.md imports, permissions dialog).
- `bash .adaptive-agents/scripts/check-project-layer.sh` — 0 failures (live layer at 0.5.2).
- `bash scripts/inspect-project-layer-upgrade.sh --target .` — correct: installed 0.5.2, real active plan detected (PL-20260731 work-unit memory in review list, no PL-19700101 placeholder).
- Template and live `manage-planning` SKILL.md copies diff-clean (in sync).

## Supporting Documents

- [PL-20260731-make-tests-part-of-planning memory](PL-20260731-make-tests-part-of-planning.memory.md)
