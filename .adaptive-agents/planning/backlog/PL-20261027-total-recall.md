# Backlog: Total Recall for Session Details

Plan: PL-20261027-total-recall

Status: Epic

Readiness: Needs Review: session artifact boundaries, retention, and cross-harness invariants need refinement.

Test approach: Each child defines falsifiable foundation or installer checks, including deterministic graph-completeness and reachability validation plus fresh-session compaction dogfood that proves provider compaction, reconciliation, Adaptive Agents guidance, and session-graph discovery survive recovery; the epic itself is not activated directly.

## Objective

Define and deliver a harness-independent Total Recall capability that preserves all session details through compaction, keeps Adaptive Agents active, and makes the complete session history discoverable through a hierarchical, incrementally expandable Markdown graph. The model is responsible for deciding how to organize the graph semantically through Markdown links to session details, while deterministic capture and validation code maintains the graph's correctness and discoverability.

## Problem Spec

Compaction reduces the active context available to an agent, but important instructions, decisions, recent turns, and earlier technical evidence may still be needed later in the same session. A summary alone can omit details or lose the path to the original user message, assistant response, tool call, or tool result. A valid post-compaction state must restore both the Adaptive Agents operating instructions that keep the guidance system active and the session graph's root index plus instructions for consulting it. Total Recall should persist the session as a navigable, multi-level Markdown graph: a compact root `INDEX.md` may link directly to detail records for small sessions or delegate to progressively narrower topic, time-range, session-phase, or event-type indexes as detail grows. The model should be able to retrieve deeper detail only when needed, but context reduction must never orphan, discard, or make retained session details undiscoverable.

## Scope

Semantic navigation is a first-class requirement: the graph must contain meaningful breadcrumbs—not merely event-type categories—for important instructions, decisions, requirements, unresolved questions, preferences, milestones, evidence, and artifacts. Each breadcrumb must link to stable source detail or a narrower semantic index; event-type and chronological indexes remain fallback accounting/navigation only.

In scope:

- Define the session-record, index, breadcrumb, and link-graph concepts that make all retained session details discoverable.
- Define a common user-scoped session store with one root `INDEX.md` per session beneath a harness namespace, independent of the current project and harness-private session storage.
- Define how each harness resolves a provider session identity or creates and persists an opaque Adaptive Agents session UUID without inferring identity from project location alone.
- Define an authoritative event ledger in which every retained session event receives a stable identifier and at least one reachable path from the session root index.
- Define a fast deterministic validator that proves graph completeness, reachability, link and anchor validity, and safe graph updates without relying on the model's claims of correctness.
- Preserve prompt instructions, recent-turn context, and semantically important middle-of-session material across compaction.
- Define a post-compaction recovery bootstrap that restores Adaptive Agents prompting and explicitly identifies the session graph root index and retrieval behavior.
- Define a common compaction adapter contract: capture a pre-compaction checkpoint when available, preserve provider compaction output with provenance when it is exposed (otherwise preserve compaction lifecycle provenance), reconcile available provider state with the Total Recall graph through a separate model query when supported, and run deterministic validation before accepting graph changes.
- Establish how an agent is instructed to consult the session index when the current context indicates that historical detail is needed.
- Prove that post-compaction recovery restores enough guidance for the model to retrieve and follow important Adaptive Agents, epic, and active-child rules, with transcript evidence of both injected recovery context and successful rule retrieval/compliance.
- Require semantic breadcrumbs in the graph so the model can navigate by meaning; event-type and chronological indexes alone are insufficient.
- Implement the first harness-specific version for ChatGPT Codex through the linked children.
- Establish extension points so additional agent harnesses can provide equivalent recall behavior without redefining the capability.

Deferred:

- Implementations for Claude Code, VS Code/Copilot, OpenCode, and other harnesses beyond the Codex children.
- A graphical session browser or search UI.
- A final retention, pruning, archival, or privacy policy until storage volume and session-lifecycle evidence are available.
- Cross-session memory unrelated to the active conversation.

## Architectural Decisions

These are proposed directions for review, not final implementation commitments.

| Decision | Proposed choice | Rationale |
|---|---|---|
| Authoritative session record | Keep complete session details in an inspectable, append-only event ledger—preferably JSONL where the harness supports it—while using Markdown indexes and context packets as semantic navigation and retrieval views | The ledger preserves exact captured events; Markdown remains portable, reviewable, linkable, and optimized for model-guided retrieval without replacing the authoritative evidence. |
| Session storage and identity | Store sessions under a user-scoped root such as `~/.adaptive-agents/sessions/<harness>/<adaptive-session-uuid>/`, with a manifest recording provider identity when available; provide the session root explicitly during recovery | A common location avoids dependence on project layers or private harness stores, while harness namespacing and adapter-owned identity prevent collisions and unreliable session inference. |
| Discovery model | Use a stable root `INDEX.md` with an incrementally expandable hierarchy of sub-indexes and detail records; keep the graph flat for small sessions and introduce layers as detail grows | A hierarchical graph keeps high-level navigation compact while preserving discoverable paths to arbitrarily detailed session evidence. |
| Graph correctness | Treat reachability and non-orphaning as hard invariants; context budgets may trigger rebalancing but may never justify dropping or unlinking retained details | Total Recall fails if details cannot be found, regardless of how small the active index becomes. |
| Semantic navigation | Require a semantic breadcrumb layer alongside the authoritative event ledger; breadcrumbs name meaningful session elements and link to source records or narrower semantic indexes, while event-type indexes remain deterministic fallback navigation | Event categories account for records but do not tell the model why a detail matters or where a decision, instruction, requirement, or evidence is located. |
| Semantic authority | Let the model propose breadcrumb labels, topics, and relationships, but require each declared breadcrumb to cite stable source identifiers and pass deterministic link/reachability validation | Meaning is model-supplied, while executable checks prove that semantic claims point to real retained details and cannot orphan the underlying record. |
| Event accounting | Assign every retained user message, assistant message, tool call, tool result, instruction, and other retained event a stable identifier and preserve a deterministic fallback path when semantic classification is incomplete | Model-directed organization must not make capture completeness depend on successful semantic interpretation. |
| Validation authority | Let the model propose semantic groupings and cross-links, but let hooks and deterministic code prove identifiers, link resolution, reachability, and update safety | The model supplies meaning; executable checks provide falsifiable evidence that the graph remains real and correct. |
| Compaction recovery bootstrap | Restore both the active Adaptive Agents guidance and an explicit session-graph discovery instruction pointing to the root index | Retaining the graph is useless if compaction leaves the model unaware of either the operating guidance or the graph's existence. |
| Compaction adapter contract | Treat provider compaction as an external transformation: preserve its output with provenance when exposed, otherwise preserve the lifecycle evidence that compaction occurred; reconcile available provider state with the Total Recall graph through a separate model query when supported, and accept only deterministically validated graph changes | Provider bookkeeping may contain important optimization and context state, but a harness may expose only lifecycle metadata. Total Recall must preserve what is available without making provider state the sole source of truth or allowing it to orphan session details. |
| Recall boundary | Treat the active session as the first-class recall scope | The immediate problem is surviving compaction within a conversation; broader memory should remain a separate concern. |
| Harness boundary | Keep the capability contract in the epic and put lifecycle/hook mechanics in harness-specific children | Different agents expose different events, storage locations, and prompt-injection mechanisms. |
| Cross-harness catalog | Do not require a global cross-harness session index for active recall; treat cataloging as optional future functionality | Active recovery only needs the current session root, avoiding unnecessary privacy, locking, and unbounded-growth concerns. |

## Related Work

- [Completed ChatGPT Codex integration](../closed/PL-20260711-chatgpt-codex-support/PL-20260711-chatgpt-codex-support.sdd.md)
- [Codex Total Recall Foundation child](PL-20261027-total-recall/PL-20261027-total-recall-codex-foundation.md)
- [Codex Total Recall Installer and Upgrade child](PL-20261027-total-recall/PL-20261027-total-recall-codex-installer.md)
- [Total Recall Session Graph Quality and Index Contract child](PL-20261027-total-recall/PL-20261027-total-recall-session-graph-quality.md)

## Children

| Work item | Status | Depends on | Evidence / next action |
|---|---|---|---|
| [Codex Total Recall Foundation](PL-20261027-total-recall/PL-20261027-total-recall-codex-foundation.md) | Completed | None | Foundation adapter, deterministic graph validation, hook provisioning contract, and focused/dogfood evidence are complete; installer-owned permissions are implemented, while semantic maintenance and named-rule recovery remain open in the session-index follow-up. |
| [Codex Total Recall Installer and Upgrade](PL-20261027-total-recall/PL-20261027-total-recall-codex-installer.md) | Completed | [Codex Total Recall Foundation](PL-20261027-total-recall-codex-foundation.md) | Completed with limitations; see immutable [closure SDD](../closed/PL-20261027-total-recall-codex-installer/PL-20261027-total-recall-codex-installer.sdd.md). Verified native Windows installation and graph capture; portability and deeper failure/health coverage are transferred to the hardening child. |
| [Total Recall Session Graph Quality and Index Contract](../closed/PL-20261027-total-recall-session-graph-quality/PL-20261027-total-recall-session-graph-quality.sdd.md) | Completed | [Codex Total Recall Foundation](PL-20261027-total-recall-codex-foundation.md) | Completed with deferred automatic-threshold/repeated-dogfood validation; immutable closure packet preserves implementation and evidence. |
| [Codex Total Recall Installer Hardening](PL-20261027-total-recall/PL-20261027-total-recall-codex-installer-hardening.md) | Backlog | [Codex Total Recall Installer and Upgrade](PL-20261027-total-recall-codex-installer.md) | Define and verify cross-platform behavior, mutation-boundary recovery, and remaining configuration/health-check coverage. |
