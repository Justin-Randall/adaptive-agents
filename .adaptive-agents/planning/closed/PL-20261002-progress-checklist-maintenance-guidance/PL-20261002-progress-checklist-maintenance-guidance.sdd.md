# PL-20261002: Progress Checklist Maintenance Guidance

- Work Unit: PL-20261002-progress-checklist-maintenance-guidance
- Source: [Prior closed plan](../PL-20261002-active-plan-conformance-migration/PL-20261002-active-plan-conformance-migration.sdd.md)
- Memory: [PL-20261002-progress-checklist-maintenance-guidance.memory.md](PL-20261002-progress-checklist-maintenance-guidance.memory.md)

## Progress

> Keep this checklist up to date as you work. After each meaningful change, check off completed stages, add newly discovered work, remove eliminated work, and adjust plan-specific items so it accurately reflects what remains to deliver.

- [x] Reopen follow-up work from the preserved closed plan
- [x] Add the maintenance instruction to the canonical template
- [x] Add focused regression coverage
- [x] Add upgrade-inspection regression coverage
- [x] Run full Project Layer and repository validation
- [x] Verify the upgrade inspection and preserve the follow-up as active

## Objective

Ensure every newly generated active plan tells the responsible model to keep its progress checklist current throughout execution.

## Specifications

### Active-Plan Contract

- The canonical `## Progress` section must contain a direct instruction to keep the checklist current as work proceeds.
- The instruction must require adding newly discovered work and removing eliminated work so the checklist reflects what remains to deliver.
- The instruction must remain inside the progress/checklist section, adjacent to its task items.
- The instruction must distinguish meaningful work changes from detailed implementation notes while allowing plan-specific checklist items.

### Compatibility

- Existing Project Layers remain upgradeable through the review-based workflow.
- The refinement is documentation-only and must not weaken the validator or change legacy version-gating behavior.

## Scope

- Update the canonical active-plan template and template version.
- Synchronize the dogfood Project Layer version.
- Add focused regression coverage for the generated instruction.
- Preserve the prior closed plan and its deferred idempotence follow-up.

## Acceptance Criteria

- [x] Bootstrapped active plans contain the maintenance instruction inside `## Progress`.
- [x] Focused and full validation pass.
- [x] Existing closed packet and deferred backlog work remain unchanged.
- [x] Upgrade inspection confirms installed and canonical template version `0.7.2` with no missing canonical paths.

## Applicable Guidance

- [Manage planning](../../../skills/manage-planning/SKILL.md): active context, testing, validation, and closure workflow.
- [Upgrade Project Layer skill](https://github.com/Justin-Randall/adaptive-agents/blob/main/skills/upgrade-project-layer/SKILL.md): review-based upgrades and preservation of project-owned plans.
- [Testing instructions](https://github.com/Justin-Randall/adaptive-agents/blob/main/instructions/testing.instructions.md): focused failing check before implementation and broadened validation after the slice passes.
- [Prior closed plan](../PL-20261002-active-plan-conformance-migration/PL-20261002-active-plan-conformance-migration.sdd.md): preserved contract and deferred idempotence boundary.

## Test Plan

- Run `bash scripts/test-project-layer.sh` and verify the generated template contains the maintenance instruction.
- Run `bash .adaptive-agents/scripts/check-project-layer.sh`.
- Run `bash scripts/check-adaptive-agents.sh`.
- Run `bash scripts/inspect-project-layer-upgrade.sh --target .` and verify the version change is reported without overwriting project-owned content.

## DRY Assessment

- Status: Required
- Scope: canonical and dogfood active-plan templates plus the focused bootstrap fixture.
- Decision: The canonical template and dogfood copy are intentionally synchronized; the test assertion validates the public bootstrap result rather than introducing a shared abstraction.

## Closure

- Disposition: Completed
- Verification: Focused suite `34/34`; Project Layer validator `0` failures; full health check `241 passed, 0 failures, 0 warnings`.
- Upgrade readiness: A `0.7.1` layer reports reviewable changes to `ACTIVE.md` and `project-layer.json` with zero missing canonical paths.
- Deferred continuation: The original backlog item remains open for repeat-migration idempotence, which is outside this documentation-only refinement.

## Decisions

- Keep the instruction in the visible `## Progress` section so it is available at the point where the model updates the checklist.
- Version the additive template refinement as `0.7.2`.
- Preserve the prior closed plan as historical context and do not reopen or rewrite it.

## Related Work

- [Prior closed plan](../PL-20261002-active-plan-conformance-migration/PL-20261002-active-plan-conformance-migration.sdd.md)
- [Deferred backlog item](../../backlog/PL-20261002-active-plan-migration-validation.md)
