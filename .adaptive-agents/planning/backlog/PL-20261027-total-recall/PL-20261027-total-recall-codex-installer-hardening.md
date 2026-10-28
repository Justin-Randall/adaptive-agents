# Backlog: Codex Total Recall Installer Hardening

Plan: PL-20261027-total-recall-codex-installer-hardening

Parent: [Total Recall for Session Details](../PL-20261027-total-recall.md)

Status: Backlog

Depends on: [Codex Total Recall Installer and Upgrade](PL-20261027-total-recall-codex-installer.md)

Readiness: Needs Review: define supported platform profiles, configuration-layer observability, and failure-injection boundaries before activation.

Test approach: Exercise native Windows, macOS, Linux, and WSL profiles where available; inject failures at each installer mutation boundary and verify rollback or explicit recovery, session-record preservation, end-to-end upgrade behavior, and accurate diagnostics for supported and unsupported configuration states.

## Objective

Close the portability, transactional-safety, and configuration-validation gaps identified during completion of the Codex Total Recall installer.

## Problem Spec

The installer is implemented and verified on a native Windows profile, but macOS/Linux/WSL behavior, end-to-end upgrades, shell mutation-boundary failure recovery, and several health-check cases remain unverified. Codex hook trust is a separate user review decision, and the installer must not claim effective activation from configuration-file presence alone. The parent epic also has a separate session-index follow-up for semantic maintenance and named-rule recovery.

## Scope

In scope:

- Define and verify the supported native Windows, macOS, Linux, and WSL path and permission profiles; document unsupported profiles explicitly.
- Exercise full upgrades and injected failures at each installer mutation boundary, including restoration or explicit recoverability of installer-owned state and preservation of user session records.
- Expand isolated configuration and health-check tests for supported legacy settings, unsupported permission profiles, duplicate user/project/inline hook sources, changed/untrusted hook definitions where observable, and invalid event matchers.
- Measure synchronous timeout and model-visible output budgets, and document enforced limits and diagnostics.
- Ensure health checks report only trust and effective configuration facts that Codex exposes through a supported interface.

Deferred:

- Semantic breadcrumb reliability and named-rule post-compaction retrieval, tracked by [Total Recall Session Graph Quality and Index Contract](PL-20261027-total-recall-session-graph-quality.md).
- Automating user-hook trust approval or adding per-hook review titles through undocumented mechanisms.
- Automatically converting unsupported permission configurations.
