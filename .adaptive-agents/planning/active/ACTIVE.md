# PL-20261027: Codex Total Recall Installer Hardening

- Status: Active
- Work Unit: PL-20261027-total-recall-codex-installer-hardening
- Origin: Backlog activation
- Parent Epic: [Total Recall for Session Details](../backlog/PL-20261027-total-recall.md)
- Source Backlog: [Codex Total Recall Installer Hardening](../backlog/PL-20261027-total-recall/PL-20261027-total-recall-codex-installer-hardening.md)
- Dependency: [Codex Total Recall Installer and Upgrade](../closed/PL-20261027-total-recall-codex-installer/PL-20261027-total-recall-codex-installer.sdd.md)
- Memory: [PL-20261027-total-recall-codex-installer-hardening.memory.md](PL-20261027-total-recall-codex-installer-hardening.memory.md)

## Progress

> Keep this checklist current as work proceeds. After each meaningful change, check off completed stages, add newly discovered work, remove eliminated work, and adjust plan-specific items so it accurately reflects what remains.

- [x] Activate the installer-hardening child with user approval and verify its installer dependency is completed.
- [x] Synchronize the child, parent epic, backlog index, and planning router.
- [x] Repair existing Project Layer planning-link validation failures before installer implementation.
- [ ] Define supported platform profiles, inline-hook conflict handling, configuration observability, and installer mutation boundaries from source-supported behavior.
- [ ] Add focused failing tests for inline `config.toml` hooks, `hooks.json` conflicts, preservation, and failure-before-mutation behavior.
- [ ] Harden the installer and health checks for supported profiles, transactional upgrades, configuration conflicts, matcher validation, and output/timeout diagnostics.
- [ ] Exercise `scripts/install-codex.sh` directly in isolated temporary Codex homes for fresh install, upgrade, rerun, dry-run, conflict, and rollback scenarios.
- [ ] Dogfood the actual installer and upgrade in a fresh ChatGPT Codex desktop session from an unrelated project; verify the reported inline-hook scenario, configuration and session-record preservation, `--check`, trust review, and compaction recovery.
- [ ] Run focused and repository validation, record evidence, and complete the review before requesting closure.

## Objective

Close the portability, transactional-safety, and configuration-validation gaps identified during completion of the Codex Total Recall installer, including a supported and verified path for running the installer when Codex user configuration already defines inline hooks.

## Specifications

### Problem Spec

The managed installer is implemented and verified on a native Windows profile, but macOS/Linux/WSL behavior, end-to-end upgrades, shell mutation-boundary failure recovery, and several health-check cases remain unverified. Codex hook trust is a separate user review decision, and the installer must not claim effective activation from configuration-file presence alone. The installer currently stops when `config.toml` defines inline hooks, asking the user to preserve them and resolve the conflict before it writes `hooks.json`. The hardening work must define and verify a safe supported path for this configuration without silently discarding user-authored hooks.

### Feature Specs

- Define and verify supported native Windows, macOS, Linux, and WSL path and permission profiles; document profiles that cannot be verified or supported.
- Exercise full upgrades and injected failures at installer mutation boundaries, proving restoration or explicit recoverability of installer-owned state and preservation of user session records.
- Validate supported legacy settings, unsupported permission profiles, duplicate user/project/inline hook sources, changed or untrusted hook definitions where observable, and invalid event matchers.
- Measure synchronous timeout and model-visible output budgets and document the enforced limits and diagnostics.
- Ensure health checks report only trust and effective-configuration facts exposed through supported Codex interfaces.
- Make the `scripts/install-codex.sh` entry point an explicit test and dogfood surface, not merely an untested wrapper around helper tests.
- Preserve unrelated Codex configuration and user-authored inline hooks. Select the conflict/migration behavior only after verifying Codex's supported configuration semantics; fail before mutation with actionable diagnostics where coexistence or migration is unsupported.

### Interface / Contract Specs

- Keep automated installer tests isolated in temporary Codex homes and configuration directories; they must never touch the real user configuration.
- Exercise the installer entry point for fresh install, upgrade, same-version rerun, dry-run, missing prerequisites, supported and unsupported configuration, and injected rollback/failure conditions.
- A conflict discovered during preflight must not leave partial installer mutations. Existing user session records must remain byte-identical across install, upgrade, rollback, and migration.
- Installer health checks must distinguish managed configuration presence from Codex hook trust and effective configuration when the latter cannot be observed through a supported interface.
- Real dogfood must use ChatGPT Codex desktop from an unrelated project and record the Codex surface/version, installer invocation and result, `--check`, relevant configuration preservation, hook review, session graph validation, and post-compaction recovery evidence.

### Behavioral Specs

- Treat native Windows desktop/CLI and WSL as distinct profiles unless the user explicitly configures them to share state.
- Do not silently convert legacy sandbox settings to permission profiles or bypass Codex's hook trust review.
- Do not delete, overwrite, or migrate user-authored inline hooks merely to make `hooks.json` installation succeed.
- Do not claim successful activation solely because managed files or hook definitions are present.
- Where a platform or Codex configuration state cannot be supported safely, fail before mutation and explain the supported recovery path.

## Applicable Guidance

- [Manage Planning](../../skills/manage-planning/SKILL.md) — keep active evidence and child/parent status synchronized; activation does not imply closure.
- [Project Layer instructions](../../instructions/project.instructions.md) — follow this repository's project-specific architecture and boundaries.
- [Project instruction index](../../instructions/INDEX.md) — route to the project-specific instructions governing this work.
- [Planning router](../INDEX.md) — authoritative project planning guidance and lifecycle.
- [Branch workflow](../../instructions/branch-workflow.md) — use a plan-specific branch and do not publish until ready.
- [Installer completion packet](../closed/PL-20261027-total-recall-codex-installer/PL-20261027-total-recall-codex-installer.sdd.md) — preserve verified Windows behavior and transferred limitations.
- [Installer Hardening backlog source](../backlog/PL-20261027-total-recall/PL-20261027-total-recall-codex-installer-hardening.md) — authoritative source scope and test approach.

## Test Plan

Use focused test-first slices. For each behavior, add a failing isolated test, run it to confirm the defect, implement the smallest change, rerun the focused test, then broaden validation. Use the existing Python and Bash tooling; do not add test dependencies unless an existing command demonstrates they are missing.

1. **Inline-hook conflict and preservation:** Extend `scripts/test-codex-hooks-config.py` and the isolated installer suite with fixtures containing user inline hooks in `config.toml`, existing `hooks.json`, and both representations. Prove the selected supported behavior, preservation of user-authored entries, actionable unsupported-state diagnostics, and no mutation on preflight failure.
2. **Installer entry-point coverage:** Extend `scripts/test-install-codex.sh` so it invokes `scripts/install-codex.sh` itself against temporary Codex homes for fresh installation, upgrade, rerun idempotence, dry-run, inline-hook conflict, missing prerequisites, and configuration preservation. Compare relevant files and user session records before and after each scenario.
3. **Upgrade and transaction recovery:** Add focused tests for complete version upgrades and injected failure at each installer-owned mutation boundary. Prove rollback or documented recoverability for the runtime pointer, launcher, configuration, permissions, and other installer-owned state, without rewriting session records.
4. **Platform and permission profiles:** Test path and configuration fixtures for native Windows, macOS, Linux, and WSL; separately verify effective OS permissions on profiles available to CI or dogfood. Record unavailable profiles as unverified, not passed.
5. **Health and hook contract:** Test diagnostics for legacy and unsupported permission settings, duplicate hook layers, trust/changed-hook states where observable, invalid event matchers, missing or incompatible runtime, synchronous timeout, and oversized model-visible output.
6. **Manual desktop dogfood:** Run the actual `scripts/install-codex.sh` for the relevant fresh-install and upgrade paths in the native Codex profile, including the state that reproduced the inline-hook error. From a fresh Codex desktop session rooted in an unrelated project, verify `--check`, preservation of inline hooks and unrelated configuration, no session-record changes, required manual trust review, hook dispatch, deterministic graph validation, and meaningful post-compaction retrieval. Do not substitute Copilot or CLI-only results for desktop evidence.
7. **Broader validation:** Run the focused installer/configuration suites, applicable platform CI checks, and `bash .adaptive-agents/scripts/check-project-layer.sh`. Run the repository health check when implementation and platform changes are complete.

## User-Facing Surface

- Surface: `scripts/install-codex.sh`, its managed runtime/configuration migration, and installer health checks.
- Runtime scenario: install or upgrade Total Recall for Codex when user-level configuration already contains hooks, then use Total Recall in a fresh desktop session.
- Endpoint or runtime: Not run.

## User-Facing Validation

- Agent proof: Pending
- Evidence: Pending isolated installer tests and user-approved Codex desktop dogfood.
- User handoff: Pending

## DRY Assessment

- Status: Not required
- Scope: Planned installer hardening across the existing configuration helper, installer orchestration, and their tests.
- Decision: Keep configuration ownership and conflict decisions in the existing helper and installation sequencing in the existing script; no parallel installer or duplicated production path is planned. Reassess if implementation reveals a second behavior implementation or repeated logic.
- Result: Initial planning assessment only; review again during implementation.
- Intentional/deferred duplication: None identified.

## Scope

- Verify supported platform and permission behavior, configuration conflict handling, transactional upgrades and recovery, health checks, matchers, and timeout/output budgets.
- Include direct `scripts/install-codex.sh` invocation in isolated automated tests and real Codex desktop dogfood.
- Preserve unrelated Codex configuration and user-generated session records.
- Do not automate hook trust approval, add undocumented hook fields, convert unsupported permission profiles, or expand Total Recall semantic graph scope.

## Acceptance Criteria

- [ ] Supported native Windows, macOS, Linux, and WSL profiles and their path/permission behavior are explicit; unavailable or unsupported profiles are accurately identified.
- [ ] The inline `config.toml` hook case that currently blocks installation has a documented, source-verified supported outcome that preserves user-authored hooks, or fails before mutation with an actionable diagnostic where support is impossible.
- [ ] Automated isolated tests invoke `scripts/install-codex.sh` for fresh install, upgrade, rerun, dry-run, conflict, and rollback/failure scenarios.
- [ ] Full upgrade and mutation-boundary failure tests prove installer-owned state is restored or recoverable and user session records are preserved.
- [ ] Health checks and focused tests cover supported legacy settings, unsupported permission profiles, duplicate hook sources, observable trust state, invalid matchers, and timeout/output budgets without claiming unsupported Codex observability.
- [ ] Manual dogfood runs the actual installer in the native Codex desktop profile from an unrelated project, including the reproduced inline-hook setup and an upgrade path; `--check` passes and user configuration/session records are preserved.
- [ ] Desktop dogfood records required hook review and proves hook dispatch, valid session graph, and meaningful post-compaction retrieval without claiming automatic compaction-threshold coverage unless observed.
- [ ] Focused tests, applicable CI checks, Project Layer validation, and required quality review pass; remaining platform limitations and deferred work are recorded.

## Decisions

- The completed installer child remains immutable; this work continues only its documented portability, configuration, transaction, and validation gaps.
- Preserve user-authored inline hooks and Codex approval behavior. Do not select a migration or coexistence strategy until supported Codex semantics are verified.
- The actual installer script must be exercised in both temporary fixtures and user-approved desktop dogfood; helper-only tests are insufficient.
- Codex hook trust is an explicit user decision; no undocumented setting or trust bypass is in scope.
- Keep user session records out of installer mutation and rollback paths.

## Verification

- `bash .adaptive-agents/scripts/check-project-layer.sh` — 0 failures after repairing existing planning links.
- `git diff --check` — passed.
- No installer implementation or installer validation has been run for this plan yet.

## Supporting Documents

- [PL-20261027-total-recall-codex-installer-hardening memory](PL-20261027-total-recall-codex-installer-hardening.memory.md)
- [Source backlog item](../backlog/PL-20261027-total-recall/PL-20261027-total-recall-codex-installer-hardening.md)
- [Parent Total Recall epic](../backlog/PL-20261027-total-recall.md)
- [Completed installer dependency](../closed/PL-20261027-total-recall-codex-installer/PL-20261027-total-recall-codex-installer.sdd.md)
