# Backlog: Codex Total Recall Installer and Upgrade

Plan: PL-20261027-total-recall-codex-installer

Parent: [Total Recall for Session Details](../PL-20261027-total-recall.md)

Status: Completed

Readiness: Completed with limitations: the managed installer is implemented and verified on the native Windows profile; broader platform, failure-injection, and semantic-recovery work is transferred to linked follow-ups.

Test approach: Write focused failing isolated-installer tests for fresh install, upgrade, migration, rerun idempotence, dry-run, user-configuration preservation, missing prerequisites, and rollback-safe failure; then dogfood installation and upgrade from an unrelated project in fresh Codex sessions.

## Objective

Extend the Codex installation workflow so Total Recall can be installed, upgraded, health-checked, and removed or migrated safely for existing Adaptive Agents users without polluting the repository or overwriting user-authored Codex configuration.

## Problem Spec

The existing `install-codex.sh` provisions canonical Adaptive Agents guidance and a repository-scoped access grant, but Total Recall will add Python-based runtime components, session storage, and lifecycle hooks that must be installed outside tracked project content and kept compatible across upgrades. Without an explicit installer contract, users may receive stale hooks, untracked dependencies, partial upgrades, or conflicting Codex configuration.

## Scope

In scope:

- Extend `install-codex.sh` or its supported helper path to provision the Total Recall runtime and required Python environment.
- Define the global Adaptive Agents installation location for managed hooks, code, and version metadata without tracking environment-specific artifacts in this repository.
- Add upgrade detection, migration, version compatibility, rollback-safe failure behavior, and content-idempotent reruns.
- Preserve unrelated Codex instructions, permission settings, approval behavior, and user-authored files.
- Extend isolated installer tests, health checks, README guidance, and supported-platform verification for the new managed components.
- Verify an installed or upgraded integration from an unrelated project in fresh Codex sessions, including compaction recovery.

Deferred:

- Redesigning the foundation's artifact schema or recall behavior; this child consumes the foundation contract.
- Installers for other agent harnesses.
- Automated cleanup or retention of user-generated session records unless required for safe migration.

## Architectural Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Runtime ownership | Keep the managed Python environment in the global Adaptive Agents installation area, outside tracked repository content | Prevent virtual-environment files and machine-specific dependencies from entering the repository. |
| Installer boundary | Keep Codex configuration changes minimal and retain the existing canonical guidance/access contract | Total Recall should extend the current integration without creating a second Codex source of truth. |
| Upgrade safety | Detect managed versions and signatures, migrate only installer-owned artifacts, and stop before partial mutation on unsupported conflicts | Existing installer guidance requires preservation, idempotence, and safe migration. |

## Related Work

- Parent epic: [Total Recall for Session Details](../PL-20261027-total-recall.md)
- Depends on: [Codex Total Recall Foundation](PL-20261027-total-recall-codex-foundation.md)
- Existing installer: [`scripts/install-codex.sh`](../../../../scripts/install-codex.sh)
- Existing installer tests: [`scripts/test-install-codex.sh`](../../../../scripts/test-install-codex.sh)
