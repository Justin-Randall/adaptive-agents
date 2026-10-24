# PL-20260711: ChatGPT Codex Support

- Work Unit: PL-20260711-chatgpt-codex-support
- Origin: Backlog ([PL-20260711-chatgpt-codex-support.backlog.md](PL-20260711-chatgpt-codex-support.backlog.md))
- Memory: [PL-20260711-chatgpt-codex-support.memory.md](PL-20260711-chatgpt-codex-support.memory.md)
- Activated: 2026-10-24
- Closed: 2026-10-24
- Status: Closed — Completed

## Progress

- [x] Activate the approved backlog item and preserve its source
- [x] Record verified Codex client, configuration, and permission facts
- [x] Review this active-plan specification before implementation
- [x] Verify the global entrypoint loads canonical `AGENTS.md` content without copies or a prose-only pointer
- [x] Verify the narrow persistent read/write grant contract from official configuration guidance
- [x] Implement the Codex installer, health check, isolated regression tests, and documentation
- [ ] Repository owner dogfoods from an unrelated project in fresh Windows desktop sessions and verifies routed write-back
- [x] Run focused and repository validation, then record completion or deferred work

## Objective

Provide one idempotent user-wide integration for local ChatGPT Codex clients (desktop app, CLI, and IDE extension) across supported operating systems. A fresh session in an unrelated project must load canonical Adaptive Agents `AGENTS.md` content, access the routed guidance and planning files without repeated prompts, and be able to write approved artifacts back to the Adaptive Agents repository.

## Problem Spec

Codex loads global guidance from its Codex home and layers project instructions, and the desktop app, CLI, and IDE extension share the local Codex agent configuration. The Windows app and native CLI use `%USERPROFILE%\\.codex` by default; WSL defaults to a separate Linux Codex home. A Windows native CLI runtime probe confirmed that a symlink at the global `AGENTS.md` path loads the canonical repository content; the desktop app's fresh-session behavior still needs owner dogfooding. Filesystem access is controlled separately by `sandbox_workspace_write.writable_roots`; project trust controls loading project-local `.codex/config.toml` and is not a grant to the external Adaptive Agents repository. The integration must bridge these surfaces while preserving existing user configuration and normal approval boundaries.

## Specifications

### Native Global Entrypoint

- Verify current official guidance and runtime behavior for global instruction discovery and precedence across the local desktop app, CLI, and IDE extension.
- Establish the smallest supported user-wide mechanism that loads the canonical repository `AGENTS.md` content into Codex context. A prose directive that merely names the file is insufficient. Do not assume a symlink imports content; prove it on the supported platforms and clients before relying on it.
- If no supported single-source mechanism can be verified, stop before implementing an alternate copy or prompt-only workaround and bring the evidence and options back for review.
- Preserve existing user-authored Codex instructions and any override behavior. Never overwrite or remove user-authored files.

### Local Client and Path Resolution

- Treat the ChatGPT desktop app, CLI, and IDE extension as one integration where they share Codex configuration; do not create separate client installers without evidence that their native configuration differs.
- Resolve `CODEX_HOME` when set and otherwise use the platform's documented Codex home. Account for the distinct default home used by WSL.
- Give the umbrella installer an explicit `codex` target and detect local Codex using verifiable native signals. Keep the standalone installer directly runnable for environments where automatic client detection is unavailable.

### Filesystem Permission Grant

- Verify the active Codex sandbox and permission-profile behavior for the local clients and platforms in scope.
- Grant read/write access only to the Adaptive Agents repository using Codex's narrowest persistent user-level mechanism. Preserve the user's active sandbox and approval policy; do not switch to full access or disable approvals globally.
- Preserve unrelated `config.toml` content and user settings. Handle existing permission profiles and incompatible legacy sandbox settings without silently replacing them; if a safe merge cannot be established, stop and report the exact configuration decision needed.
- Do not treat project trust or a project-local `.codex/config.toml` as the external repository access grant.

### Installer, Health Check, and Rollout

- Add an idempotent Codex installer that supports dry-run, resolves the repository root from its script location, and preserves unrelated settings. No prior Codex installer artifacts existed to migrate.
- Add Codex integration validation to `scripts/check-adaptive-agents.sh`, checking the effective entrypoint and permission contract for the current installation path.
- Add the Codex installer to `scripts/install.sh` and document supported clients, platforms, configuration paths, permissions, and verification in `README.md`.
- Pin the Codex app/client version and OS/sandbox mode used for live validation in the memory file; re-verify after major client changes.

## Scope

In scope:

- One user-wide integration for local ChatGPT Codex desktop, CLI, and IDE clients.
- Platform-aware Codex home resolution, including `CODEX_HOME` and the Windows/WSL distinction.
- A native global instruction entrypoint, a narrow persistent read/write permission grant, installer, umbrella detection, health check, isolated tests, and README guidance.
- Fresh-session validation from an unrelated local project, including a content-proof probe and a routed write-back.

Deferred:

- Separate per-client integrations unless runtime evidence proves a shared configuration path is insufficient.
- Any copied guidance corpus, duplicate sentinel, or prose-only loading workaround.

## Test Plan

Method: TDD for installer and health-check behavior. Use isolated temporary `CODEX_HOME` and config paths for automated tests; never read or write real user configuration from the test suite. The repository owner will perform the live dogfood manually in the Windows desktop app.

- Entry point: prove the supported global mechanism loads content from the canonical `AGENTS.md`; falsify this with an unrelated project and a content-proof question that cannot be answered by a stale or copied sentinel.
- Permission merge: test fresh install, existing `config.toml` with unrelated settings, an existing grant, duplicate grants, custom/legacy sandbox configuration, and unsupported or malformed config. Verify only the intended repository access is added and existing approval policy is preserved.
- Lifecycle: test repeated install is byte-stable, dry-run writes nothing, and conflicting user-authored global instructions are preserved without partial changes. There are no prior Codex installer artifacts to migrate.
- Platform paths: test explicit `CODEX_HOME`, native Windows defaults, Unix defaults, and WSL's separate default with injected paths/environment; verify Windows path serialization and TOML parsing.
- Health check: test valid and invalid entrypoint, missing repository permission grant, malformed config, and configuration/profile conflict diagnostics.
- Live dogfood (repository owner): from an unrelated project in a fresh Windows desktop app session, verify the sentinel, canonical-content proof, routing through the Project Layer, and an approved write-back to an Adaptive Agents planning artifact.
- Run the focused Codex installer suite first, then `bash .adaptive-agents/scripts/check-project-layer.sh` and `bash scripts/check-adaptive-agents.sh`; ensure the existing CI workflow covers the changed scripts.

## Applicable Guidance

- [Manage Planning](../../../skills/manage-planning/SKILL.md): activation, active-context maintenance, testing, and closure workflow.
- [Project instructions](../../../instructions/project.instructions.md): project-specific architecture contract requirements.
- [Architecture contract](../../../ARCHITECTURE.md): one canonical user-wide source, minimal adapters, and fresh-session verification.
- Follow the repository's inherited coding and testing instructions for verified behavior, reversible changes, and focused falsifiable checks.
- [Branch workflow](../../../instructions/branch-workflow.md): this task remains on `main` under the user's explicit direction.
- [Cross-tool integration contract](../../backlog/INDEX.md): native entrypoint plus narrow read/write grant, isolated tests, health check, and three-part dogfood proof.

## Acceptance Criteria

- [x] A verified native global entrypoint loads canonical Adaptive Agents `AGENTS.md` content for supported local Codex clients, with no copied guidance and no prose-only pointer.
- [x] The installer grants the Adaptive Agents repository read/write access while retaining the existing sandbox and approval policy; isolated tests verify the generated configuration.
- [x] One installer handles `CODEX_HOME` and platform defaults, preserves user configuration, supports dry-run, and is content-idempotent.
- [x] `install.sh`, the repository health check, and README document and validate the same Codex integration contract.
- [x] Isolated regression tests cover configuration preservation, permission edge cases, idempotence, dry-run, and conflicts; they never touch real user configuration.
- [ ] Repository owner completes fresh-session dogfood from an unrelated project and proves the sentinel, canonical content, routing, and write-back.
- [ ] CI passes on Ubuntu and Windows; the local focused tests, Project Layer validation, and repository health validation pass. The verified client/platform versions are recorded in memory.

## Decisions

| Decision | Choice | Rationale |
| --- | --- | --- |
| Integration identity | One local “ChatGPT Codex” integration across desktop, CLI, and IDE clients | Official guidance says these surfaces share Codex agent configuration; platform paths and sandbox enforcement are the differences to validate. |
| Canonical content | Keep the Adaptive Agents repository as the only guidance source | Avoid stale copies and sentinel false positives; native loading semantics must be proven before implementation. |
| Permissions | Add only the persistent repository-scoped read/write grant and preserve the active approval policy | Instructions and project trust do not grant filesystem access; full access would exceed the requested boundary. |
| WSL | Treat its default Codex home as distinct unless `CODEX_HOME` is configured to share | Windows desktop and WSL use different default homes. |

## DRY Assessment

- Status: Required
- Decision: Reuse established installer, health-check, and isolated-test patterns. Reassess TOML parsing and Codex path helpers before implementation; introduce shared abstractions only if an existing seam supports them without coupling tool-specific behavior.

## Related Work

- [Source backlog item](PL-20260711-chatgpt-codex-support.backlog.md)
- [Claude Code integration](../PL-20260711-claude-code-support/PL-20260711-claude-code-support.sdd.md)
- [OpenCode installer rework](../PL-20260711-opencode-installer-rework/PL-20260711-opencode-installer-rework.sdd.md)

## Closure

- Disposition: Completed, with user-approved closure after the owner reported the integration active in the Windows Codex desktop app.
- Local evidence: focused installer tests and repository validation were recorded as passing in the active plan; the global entrypoint was verified with the native Windows Codex CLI probe described in memory.
- Not claimed as verified: the recorded unrelated-project routed write-back acceptance check remains unchecked; CI on Ubuntu and Windows was not recorded as passing. The owner indicated they would perform manual dogfood after restarting Codex.
- Deferred work: no new backlog item was approved. Remaining validation is documented as a limitation, not represented as a pass.