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

Tool integrations are adapters from each tool's native instruction-discovery, lifecycle, and access mechanisms to canonical routed guidance. They may install minimal pointers, hooks, settings, or commands required by the tool, but they must not copy the guidance corpus or create competing sources of truth. Deterministic lifecycle hooks should inject canonical file contents directly rather than instructing a model to load or execute mandatory startup behavior. The VS Code/GitHub Copilot adapter uses the Copilot harness's version-1 camelCase hook contract and shares the Markdown Total Recall ledger model with Codex through a provider-specific session namespace.

Installers must preserve unrelated user configuration, deduplicate managed values, support safe repeated execution, and verify behavior through fresh sessions or equivalent tool-native checks. A successful file write or installer exit is not sufficient proof that a tool loaded the guidance.

### Script Tree

The root `scripts/` directory owns stable public installer, health-check, browser
and lifecycle entrypoints. Application implementations belong under
`scripts/codex/`, `scripts/vscode/` and `scripts/browser/`, routed by focused
indexes. Application tests live beneath their owning area; shared repository and
installer tests live in `scripts/tests/`.

Preserve installed command paths rather than requiring users to migrate hook
configuration for a source-tree cleanup. Thin root entrypoints forward to the
single implementation; the legacy browser import and three public README test
commands retain compatibility bridges. Other internal/test callers use canonical
area paths. Historical closed plans and evidence retain their original commands.
The installed Codex adapter remains self-contained in its versioned runtime;
moving checkout sources must not invalidate an existing installed reader or
rewrite session history. Tests cover outside-checkout invocation, default root
discovery, copied-repository fixtures and installed-reader independence.

On Windows, staged public runtime payloads must inherit the managed parent's access rules when promoted; Python 3.13+ owner-only temporary-directory ACLs must not become the installed reader's access policy. Host hook execution and sandboxed model tool execution are separate permission boundaries. Interpreter read/execute access requires its own evidence and explicit approval for any permission changes; never substitute sandbox bypass or a different sandbox implementation as proof.

## Adaptation Lifecycle

The learning flow is capture, triage, review, and approved promotion. Project-specific observations remain in the Project Layer. Cross-project guidance belongs at the repository root only when broader intent or evidence supports it. Raw retrospectives are evidence, not active instructions.

Planning artifacts coordinate work but do not override checked-in instructions or architectural invariants. Each active task has one canonical `PL-YYYYMMDD-descriptive-slug` work-unit identity. Its plan and curated memory preserve that identity through closure; reopened work receives a new identity and links to immutable prior context rather than rewriting it. Active plans should reference the specifications and supporting context needed for implementation without duplicating durable guidance.

Parent epics maintain a synchronized execution-status view of their children, separate from backlog readiness. Implementation complete but awaiting closure is an explicit state; approved closure and verified archival establish the final disposition. The canonical lifecycle vocabulary and synchronization rules live in the user-wide Planning Conventions; generated workflows route to that contract.

## Validation Boundary

Deterministic scripts validate repository structure, routing, links, metadata, installer behavior, and Project Layer contracts. Focused tests should falsify the changed behavior first; the repository health checker provides broad completion validation.

Total Recall keeps complete received hook payload values, including tool-result contents, in one authoritative append-only `ledger.md`. Deterministic hooks produce framed, checksummed records with stable event and text-part anchors; the model never authors evidence. A model-authored `INDEX.md` and purposeful topical subindexes provide semantic navigation; generated event copies, automatic context packets, archival hierarchies, and a JSONL mirror are not required. A bounded reader retrieves selected payload slices directly from the ledger. Capture cannot recover provider-truncated or unobserved output.

Hook wire input is strict UTF-8, independent of locale or pipe encoding. Tests cross the raw-byte and installed-launcher boundaries with long non-ASCII payloads; already-decoded objects and ASCII-escaped JSON cannot establish wire fidelity. Bare/backticked source references receive actionable formatting errors rather than false link coverage.

Rendered session roots must give a directly executable, shell-quoted source reader. The managed installation manifest owns the absolute interpreter and stable launcher paths; generated roots add only their session-specific path and must not embed a version-specific adapter path. Recall must not depend on Python command discovery, a particular working directory, or reconstructing installation paths after compaction. Verify the emitted command with an empty PATH and from outside the checkout, including after a runtime upgrade.

JSON/JSONL recall sessions are deprecated, not a compatibility target. Nothing is released: runtime 1.2 has no migration, legacy reader, dual writer or native-transcript repair path. Legacy capture/read attempts fail explicitly and direct the user to start a fresh session. Installation does not delete or rewrite historical sessions, reports or previous runtime directories.

Maintained seed templates own the model-facing graph contract, and adapters preserve model-authored navigation without rewriting existing roots. Minimal manifests, identity maps and locks support identity and concurrent capture without creating another history store. Corruption and interrupted appends fail visibly rather than silently truncating or repairing evidence.

Capture completeness is independent of topical coverage. Ordinary Stop hooks capture the received response without auditing all-event reachability or blocking conversation for missing breadcrumbs. The model maintains selective subjects while context is available or during deliberate curation; compaction must not trigger exhaustive cataloguing. Capture and execution failures remain explicit.

Post-compaction SessionStart context must fit its configured hook limit, identify the selective root and source discovery tools, and allow the user's task to continue. PostToolUse context supplies actual captured result handles, never inferred topics. Bounded literal ledger search provides fallback discovery for unindexed details, returning anchors, read-compatible offsets, excerpts and explicit continuation. A complete short excerpt can establish evidence; read further source context when needed. Search absence is not semantic absence. No duplicate payload store or background model service is required.

Deterministic validation proves source identity and declared-link validity, not topical completeness; legacy coverage CLI options are removed. A single tool result may warrant several topical routes or none. Acceptance requires both indexed and intentionally unindexed source-backed retrieval with the original corpus unavailable, plus measured foreground overhead and compact topical navigation at realistic scale. Hooks must not launch another model session; separate threads are an explicit test fixture only.

Template 12 remains at its original path for already-installed runtimes that resolve shared templates from the checkout. Runtime 1.2 uses the separate `markdown-session-index.md` template (version 14), so editing the new contract does not silently alter the old live installation. The version-13 JSONL template remains historical, not a supported current runtime path.

Recall-provenance evidence must retain observable ordering: the model receives topical index context before searching or reading retained source, then answers from the returned evidence. A citation or unordered list of commands is insufficient. An adequate search excerpt does not require a redundant read. Distinguish facts absent from inspectable context and failed no-tools recall from claims about opaque provider compaction state; encrypted state cannot be certified absent by searching its serialized bytes.

Routine temporary diagnostics are disposable outputs, but user-requested acceptance evidence is retained at its original paths, including failed runs. Supplied failed sessions are read-only diagnostic sources, never targets for manual index repair or reconstructed acceptance evidence. An isolated test report is not a substitute for an installed-hook session's original index, ledger and native transcript. Canonical guidance, templates, schemas, and validators are reviewed source artifacts.

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
