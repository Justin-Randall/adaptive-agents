# PL-20261027: Codex Total Recall Installer

- Work Unit: PL-20261027-total-recall-codex-installer
- Status: Completed
- Origin: Backlog activation
- Parent Epic: [Total Recall for Session Details](../../backlog/PL-20261027-total-recall.md)
- Source Backlog: [Codex Total Recall Installer and Upgrade](PL-20261027-total-recall-codex-installer.backlog.md)
- Foundation Dependency: [Codex Total Recall Foundation](../PL-20261027-total-recall-codex-foundation/PL-20261027-total-recall-codex-foundation.sdd.md)
- Memory: [PL-20261027-total-recall-codex-installer.memory.md](PL-20261027-total-recall-codex-installer.memory.md)

## Progress

> Keep this checklist up to date as work proceeds. After each meaningful change, check off completed stages, add newly discovered work, remove eliminated work, and adjust plan-specific items so it accurately reflects what remains to deliver.

- [x] Activate the installer child and synchronize parent/child tracking.
- [x] Load the Total Recall epic, installer backlog source, and closed foundation handoff.
- [x] Preserve the foundation's runtime, graph, hook, and validator contract as the installer dependency.
- [x] Reconcile the Codex desktop dogfood boundary with the foundation handoff; do not treat Copilot work as Codex evidence.
- [x] Incorporate official Codex documentation findings for hook trust, configuration layers, permission profiles, platform surfaces, matcher behavior, and hook output limits.
- [x] Agree on a per-user Adaptive Agents runtime root, system-Python ownership, manifest-based versioning, and staged upgrade strategy.
- [x] Implement the managed runtime layout, manifest schema, stable launcher, and native user-home path resolution; Windows-native fixtures pass, while other platform profiles remain unverified.
- [x] Implement fresh installation, managed runtime upgrades, legacy hook migration, rerun idempotence, dry-run, and rollback behavior; coverage gaps remain for end-to-end upgrade and injected installer failures.
- [x] Implement narrow Codex hook/configuration and permission migration with fail-closed behavior for unsupported or user-authored state.
- [x] Add isolated installer tests and health checks for the currently supported contract.
- [x] Verify Windows Codex desktop hook dispatch, compaction lifecycle capture, graph creation, and deterministic graph validity; document that semantic retrieval was not proven.
- [x] Record the trust-review limitation and the generic hook-title limitation from the actual desktop UI and official Codex documentation.
- [x] Scan all seven local Codex session graphs and record structural, link, and semantic-breadcrumb findings.
- [x] Transfer semantic-index reliability and named-rule recovery to the existing session-index follow-up; transfer cross-platform and deeper installer-hardening gaps to a separate backlog child.
- [x] Complete the memory review and receive approval to close with limitations.

## Implementation Status

The managed runtime, stable hook launcher, installer orchestration, session-store permission grant, and `--check` path are implemented. The stable launcher verifies the active pointer, manifest, payload hashes, and interpreter before dispatching the adapter. Installer tests are isolated in temporary homes; the Windows-native integration suite passes 19 checks, the foundation adapter suite passes 13, and the runtime/permission/hook unit suites pass 7, 2, and 6 tests respectively. The launcher test also verifies canonical guidance-root propagation and hook argument delivery.

README and script inventory now describe the managed runtime, permission roots, `--check`, and current permission-profile limitation. The repository health-check script runs the new focused Python suites.

The installer is complete for the verified native Windows profile. The health check validates the managed runtime and installer-owned user configuration, but does not claim to verify Codex's effective hook-trust state or project/user configuration layers. Permission-profile configurations intentionally fail closed. Cross-platform behavior, deeper mutation-boundary and upgrade tests, matcher/output-budget checks, and broader configuration-layer validation are transferred to the installer-hardening backlog child. Intermittent semantic breadcrumb creation and named-rule retrieval are transferred to the session graph quality backlog item.

The real Windows Codex profile passed dry-run, was installed with the user's authorization, and passed `install-codex.sh --check`. The full repository health check ran 257 checks but ended with two unrelated planning/link-validation failures and one Claude Code warning. The failures concern the already-dirty Total Recall backlog/Project Layer and existing closed-foundation links to missing or external session/temp artifacts; those user-owned changes were left untouched. All Codex installer, foundation, and Codex integration checks passed.

The first desktop launch displayed ten new hooks for review with generic `Hook 1`-style titles. These are the ten expected Total Recall event registrations. The installer already provisions the repository and session-store filesystem grants automatically; those are separate from hook trust. Official Codex documentation confirms that non-managed hooks must be reviewed and trusted against their exact definition hash, and new or changed definitions are skipped until trusted. There is no supported user-level setting or installer API to pre-approve that trust. Automatic trust is available only through managed policy sources (system/MDM, cloud, or enterprise-managed `requirements.toml`); the documented cloud-managed hook path is not available to personal accounts. The CLI `--dangerously-bypass-hook-trust` option is for one-off automation and is not a persistent desktop-install solution. The documented hook schema has no per-handler display-title field; its optional `statusMessage` is for execution status, not the review list. Do not add an unsupported `name` property or use a trust bypass as an installer workaround. Sources: [Codex hook trust and schema documentation](https://learn.chatgpt.com/docs/hooks) and [advanced configuration](https://learn.chatgpt.com/docs/config-file/config-advanced).

Desktop dogfood from the user-provided session graph confirmed lifecycle capture, including `PreCompact` and `PostCompact` (17 ledger events), and the deterministic graph validator passed. However, the root `INDEX.md` still contains the generated semantic-breadcrumb instructions and the placeholder stating that no model-authored breadcrumbs were accepted. This proves event capture and graph integrity only; it does not satisfy semantic indexing, recovery retrieval, or named-rule application acceptance. The adapter's `UserPromptSubmit` output asks the model to maintain breadcrumbs, while the deterministic writer only preserves model-authored content; no reliable automatic semantic-maintenance mechanism has been validated.

A subsequent read-only scan of all seven local Codex session graphs found all seven structurally valid, zero broken Markdown links (including links in Markdown files outside the root's reachable set), and zero orphan Markdown files. Three roots contain one, one, and two model-authored semantic breadcrumbs; their labels were checked against their linked source prompts and are broadly relevant. Four roots retain the no-breadcrumb placeholder. In particular, the compacted dogfood session still has captured events but no semantic breadcrumb. The stable bootstrap/retrieval instructions and breadcrumb contract are intentionally retained boilerplate; the no-breadcrumb placeholder is expected only until the model replaces it with actual breadcrumbs. This supports installer event capture and graph integrity, while semantic indexing remains an intermittent foundation behavior and the full post-compaction named-rule criterion remains open.

## Objective

Extend the Codex installation workflow so Total Recall can be installed, upgraded, health-checked, and migrated safely for existing Adaptive Agents users without polluting the repository or overwriting user-authored Codex configuration.

## Specifications

- Extend `scripts/install-codex.sh` or a supported helper path to provision the foundation runtime and required Python environment.
- Keep managed Python code, dependencies, version metadata, and hook entrypoints in the global Adaptive Agents installation area, outside tracked repository content.
- Define a stable managed layout for the runtime and user-scoped Codex session namespace; do not move or rewrite user-generated session records during ordinary upgrades.
- Detect managed versions and signatures, migrate only installer-owned artifacts, and stop safely before partial mutation on unsupported conflicts.
- Preserve unrelated Codex instructions, permission settings, approval behavior, and user-authored files.
- Provision exact read/write access needed for the managed hook runtime and session namespace without broadening unrelated permissions.
- Make fresh install, upgrade, migration, dry-run, and same-version rerun behavior content-idempotent and observable.
- Add health checks that parse the effective managed configuration and report missing, stale, conflicting, or unsafe installation state.
- Verify the installed or upgraded integration from an unrelated project in a fresh Codex session, including forced or observed compaction recovery.

## Acceptance Criteria

### Verified for the installer child

- [x] The managed runtime layout, version metadata, Python ownership, and session-artifact boundary are implemented and documented without tracked environment-specific files; native Windows integration is verified.
- [x] Fresh installation provisions the runtime, hook adapter, hook configuration, and narrow required permissions while preserving unrelated configuration in the tested Windows profile.
- [x] Managed upgrades, migration, same-version idempotence, dry-run, and rollback behavior are implemented; the tested installer suite covers the supported paths and conflict behavior.
- [x] Health checks validate the managed runtime and installer-owned user configuration, including runtime/version and permission contracts.
- [x] Focused isolated installer, foundation-adapter, runtime/launcher, permission, and hook-configuration tests pass; the real Windows Codex profile passed installation and `--check`.
- [x] User-approved hooks dispatched in Codex desktop and produced a graph with `PreCompact` and `PostCompact` lifecycle events; the supplied graph validated. A scan of seven local Codex session graphs found all seven structurally valid with no broken Markdown links or orphan Markdown files.

### Deferred by the approved closure

- Semantic breadcrumb reliability and post-compaction retrieval/application of named rules are not established. Three of seven scanned indexes had model-authored breadcrumbs and four retained the no-breadcrumb placeholder. This work is transferred to [Total Recall Session Graph Quality and Index Contract](../../backlog/PL-20261027-total-recall/PL-20261027-total-recall-session-graph-quality.md).
- Native macOS/Linux/WSL coverage, end-to-end upgrade and mutation-boundary failure injection, session-record-preservation tests, broader trust/configuration-layer checks, matcher validation, and timeout/output-budget checks are not complete. These are transferred to [Codex Total Recall Installer Hardening](../../backlog/PL-20261027-total-recall/PL-20261027-total-recall-codex-installer-hardening.md).
- Codex requires explicit review/trust for non-managed user hooks; the installer does not pre-approve trust. The documented hook schema has no per-handler review title, so the UI's generic titles cannot be customized through a supported field. These product constraints are documented and were not bypassed.

## Scope

In scope: `install-codex.sh`, its supported Python/helper path, global runtime provisioning, versioning, migration, Codex hook/configuration updates, exact permission handling, isolated installer tests, health checks, documentation, and installer-enabled Codex dogfood.

Deferred: semantic-index reliability and named-rule recovery (transferred to the session-index follow-up); cross-platform and deeper installer-hardening coverage (transferred to the installer-hardening follow-up); redesigning the foundation artifact schema beyond that follow-up; installers for other harnesses; automatic cleanup or retention of user-generated session records unless required for safe migration.

## R&D Workstreams

1. Implement the approved per-user runtime root at `~/.adaptive-agents/codex/total-recall/`, resolving the native user home on Windows, macOS, Linux, and WSL. Use the existing system Python at its resolved absolute path; require Python 3.11 or newer, validate it on install and health check, and do not create a venv or bundle an interpreter unless a dependency or compatibility finding justifies that change.
2. Define the manifest schema and managed signatures: record manifest schema version, Total Recall runtime version, minimum Python version, selected interpreter path, and hashes for installer-managed payload files. Keep versioned payloads separate from a stable hook launcher where Codex's hook contract permits; never use a top-level description alone as proof that every hook entry is installer-owned.
3. Resolve Codex-home and session-namespace permission behavior on supported Windows-native, macOS, Linux, and WSL surfaces without broad approval-policy changes. Preserve the existing permission model and add only the exact required access when that configuration is supported; do not silently convert legacy sandbox settings to permission profiles. Fail closed with an actionable diagnostic on unsupported or ambiguous configurations. Treat Windows desktop/CLI and WSL Codex homes as separate profiles unless explicitly configured to share state.
4. Implement a staged upgrade transaction: preflight all conflicts and prerequisites, stage and validate the new version, apply supported permissions and configuration with prior state recoverable, switch the active version only after validation, and retain the prior version for rollback. Never move or rewrite user-generated session records. Inject failures at each mutation boundary and assert the resulting managed state is either restored or explicitly recoverable.
5. Verify effective hook configuration and health-check parsing for fresh installs, legacy configurations, conflicts, duplicate `hooks.json`/inline `config.toml` definitions, and upgrades.
6. Define the hook trust/review workflow: changed hook definitions are hash-tracked and skipped until trusted, so installation and upgrades must report the required review state rather than claiming activation from file presence alone.
7. Validate event-specific matcher behavior and reject misleading configuration, including matchers on events that ignore them and invalid source/trigger patterns.
8. Measure synchronous hook timeout, serialization, and model-visible output budgets. Keep correctness-critical capture synchronous; do not depend on background hooks for ordered ledger updates because they can finish out of order or be cancelled.
9. Run the deferred named-rule compaction dogfood using the installed runtime in the actual ChatGPT Codex desktop app—not merely CLI or Copilot—and preserve transcript, graph, and validator evidence. Prove retrieval and application of canonical `AGENTS.md`, epic, and active-child rules; a delivered graph pointer or fact recall alone is insufficient. If desktop hooks or required state access cannot be exercised, record the blocker instead of claiming equivalent evidence from another surface.

## Test Plan

For each implementation slice, add or extend the focused isolated test first, run it to confirm failure, make the smallest implementation change, rerun that test, then broaden validation. Use `scripts/test-install-codex.sh` for installer orchestration and filesystem/configuration migration, `scripts/test-codex-hooks-config.py` for hook ownership and rendering, and `scripts/test-codex-total-recall.py` for foundation-contract regression. Run the Python tests with Python 3.11+ and the installer suite with Bash.

- Runtime/manifest slice: test fresh staged install, exact manifest contents and hashes, absolute interpreter selection, missing/incompatible interpreter, interrupted staging, and health-check rejection of missing or modified payload files.
- Hook/configuration slice: test a stable launcher definition across payload upgrades, trust-review reporting when the definition changes, preservation of extra user-authored hook entries or fail-before-mutation behavior, and duplicate/conflicting user/project/inline sources.
- Permission slice: test each supported legacy/profile configuration fixture for exact path additions, preserved approval behavior and unrelated settings, and fail-before-mutation for unsupported or mixed configurations. Validate effective OS permissions on the declared platform profiles separately from fixture-only config tests.
- Upgrade/rollback slice: test version migration, byte-stable reruns, dry-run with a full before/after filesystem and configuration comparison, and injected failures at each mutation boundary proving rollback or explicit recovery.
- Health-check slice: assert diagnostics and exit behavior for every enumerated missing, stale, untrusted, conflicting, disabled, malformed, incompatible, and permission-denied state.
- Desktop dogfood: after install and upgrade, use the actual ChatGPT Codex desktop app from an unrelated project; preserve surface/version, rollout transcript, graph, deterministic validator output, and post-compaction named-rule retrieval/application evidence.

- Keep automated tests entirely in temporary fixture directories and never mutate the real user Codex configuration.
- Include byte-stability checks for same-version reruns and explicit preservation checks for unrelated hooks, instructions, permissions, and session records.
- Exercise malformed configuration, unsupported version, missing Python/runtime, permission denial, interrupted copy, and incomplete migration fixtures.
- Exercise untrusted/changed hook definitions, duplicate user/project hook layers, both `hooks.json` and inline `config.toml`, legacy sandbox settings, permission-profile settings, invalid matchers, synchronous timeout, and oversized recovery output.
- Run the repository's existing static validation workflow where supported; document Bash-host limitations when local execution is unavailable.
- Record installed version, effective paths, permissions, hook payloads, Codex version/surface, compaction evidence, and graph validation output in memory.

## Applicable Guidance

- `skills/manage-planning/SKILL.md`: preserve the backlog source, keep progress/acceptance criteria/verification in `ACTIVE.md`, activate one child at a time, and require a completion review before closure.
- `instructions/testing.instructions.md`: write focused failing tests before implementation and broaden validation only after focused checks pass.
- `instructions/repository-boundaries.instructions.md`: keep managed user-wide runtime artifacts outside the tracked repository and preserve the repository boundary.
- `instructions/branch-workflow.instructions.md`: continue on the dedicated Total Recall branch and do not publish until ready.
- Backlog-wide installer contract in `planning/backlog/INDEX.md`: migrate rather than accumulate, preserve unrelated configuration, use isolated tests, validate effective configuration, and record tool-version evidence.

## Decisions

- Consume the closed foundation contract; do not redesign the Markdown graph or deterministic validator in this installer child.
- Install managed runtime code under the per-user Adaptive Agents root `~/.adaptive-agents/codex/total-recall/`, outside the repository and project-local `.adaptive-agents/` content, and separate from Codex's configuration home and session-record namespace.
- Use the existing system Python resolved to an absolute executable path; require Python 3.11+ and validate the selected interpreter. Do not add a venv or bundled Python unless dependency or compatibility evidence warrants the extra ownership burden.
- Use versioned runtime payloads and an explicit manifest for schema/runtime versions, minimum Python, selected interpreter, and managed-file hashes. Use a stable launcher across payload versions where supported, so internal runtime upgrades need not change Codex's hook definition.
- Upgrade by staging and validating new payloads before switching active state; retain the prior payload for rollback and do not include session records in install, migration, or rollback.
- Treat Codex's user state/configuration and user-generated session records as protected boundaries; modify only installer-owned configuration and explicitly required permission surfaces.
- Preserve the existing Codex permission model, adding only exact required access when its configuration is supported. Do not silently convert legacy sandbox configuration to permission profiles; fail closed on unsupported or ambiguous states. Keep the approval policy unchanged.
- The installer initially owned Codex-home permission repair and named-rule compaction dogfood deferred by the foundation child. Permission repair was implemented; semantic recovery remains a parent-epic requirement and is transferred to the session-index follow-up.
- Fail closed on unrelated existing hook configuration unless ownership/signature proves it is safe to migrate.
- Treat Copilot and Codex desktop as separate applications. Running the installer from this Copilot session may modify the installer-owned Codex runtime/configuration and required permission surfaces as part of dogfood; preserve unrelated user-authored configuration and session records. Copilot/CLI observations alone are not desktop behavior evidence.

## Installer Baseline at Plan Start

The following bullets record the pre-implementation state and are historical, not descriptions of the completed installer.

- At plan start, `scripts/install-codex.sh` installed the global instruction redirect and repository-scoped workspace-write grant, then configured hooks to invoke `scripts/codex_total_recall.py` directly from the checkout using the selected system Python. It did not provision a managed global runtime.
- The foundation adapter writes session data under the user-scoped `~/.adaptive-agents/sessions/codex` namespace, but the current installer configuration path does not provision the exact required access to that namespace.
- `scripts/codex_hooks_config.py` treats the file-level Adaptive Agents description as ownership and renders the whole expected `hooks.json`; it fails closed for a differently described file, but does not preserve additional hook entries placed in an Adaptive Agents-described file. Installer migration must not mistake the marker for proof that every entry is installer-owned; add isolated tests proving extra user-authored entries are preserved or that the installer stops before mutation with a clear conflict.
- These are observations of the existing foundation wiring, not a requirement to preserve the current repository-local runtime layout. The installer child must replace it with a managed global runtime while retaining the foundation adapter contract.

## Verification Baseline

- Foundation dependency is closed and preserved at [PL-20261027-total-recall-codex-foundation](../PL-20261027-total-recall-codex-foundation/PL-20261027-total-recall-codex-foundation.sdd.md).
- Foundation tests passed: 13 adapter tests and 2 hook-provisioning tests with the bundled Python runtime.
- Foundation dogfood artifacts remain user-inspectable under the paths recorded in the closed foundation SDD.
- The foundation dogfood environment could not write Codex's state database; permission-sensitive desktop dogfood remains open. This Copilot session is not the target Codex environment, so installer-enabled desktop validation must be a separate, user-assisted run.
- Initial installer inspection confirmed repository-local adapter execution, system-Python selection, no installer-provisioned session-namespace grant, and whole-file replacement of Adaptive Agents-described hooks configuration; see `## Installer Baseline at Plan Start`.
- Official Codex research now adds installer gates for hook trust/hash review, layered hook-source conflicts, legacy-versus-profile permission migration, Windows-native versus WSL state separation, event-specific matcher validation, synchronous ordering, and hook output limits; sources and follow-up tests are recorded in the active memory.
