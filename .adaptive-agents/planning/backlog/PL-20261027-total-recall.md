# Backlog: Total Recall for Session Details

Plan: PL-20261027-total-recall

Status: Epic

Readiness: Needs Review: session artifact boundaries, retention, and cross-harness invariants need refinement.

Test approach: Each child defines falsifiable capture-integrity, declared-link and installer checks plus fresh-session compaction dogfood. Require indexed and intentionally unindexed source-backed retrieval, compact topical navigation and measured nonblocking conversation at realistic scale; the epic itself is not activated directly.

## Objective

Define and deliver a harness-independent Total Recall capability that preserves all received session details through compaction, keeps Adaptive Agents active, and makes retained history discoverable through selective model-owned topical navigation plus bounded source search. The model decides which subjects and relationships deserve Markdown routes; deterministic code preserves received payloads, stable identities and valid declared links without requiring every event to receive a semantic breadcrumb.

## Problem Spec

Compaction reduces the active context available to an agent, but important instructions, decisions, recent turns, and earlier technical evidence may still be needed later in the same session. A summary alone can omit details or lose the path to the original user message, assistant response, tool call, or tool result. A valid post-compaction state must restore both the Adaptive Agents operating instructions that keep the guidance system active and the session graph's root index plus instructions for consulting it. Total Recall should persist the session as a navigable, multi-level Markdown graph: a compact root `INDEX.md` may link directly to detail records for small sessions or delegate to progressively narrower topic, time-range, session-phase, or event-type indexes as detail grows. The model should be able to retrieve deeper detail only when needed, but context reduction must never orphan, discard, or make retained session details undiscoverable.

## Scope

Semantic navigation is a first-class requirement: the graph must contain meaningful breadcrumbs—not merely event-type categories—for important instructions, decisions, requirements, unresolved questions, preferences, milestones, evidence, and artifacts. Each breadcrumb must link to stable source detail or a narrower semantic index; event-type and chronological indexes remain fallback accounting/navigation only.

In scope:

- Define the session-record, index, breadcrumb, and link-graph concepts that make all retained session details discoverable.
- Define a common user-scoped session store with one root `INDEX.md` per session beneath a harness namespace, independent of the current project and harness-private session storage.
- Define how each harness resolves a provider session identity or creates and persists an opaque Adaptive Agents session UUID without inferring identity from project location alone.
- Define an authoritative event ledger in which every retained session event receives a stable identifier and can be found through source search/read tools discoverable from the root, independently of topical coverage.
- Define a deterministic validator that proves source integrity and declared link/anchor validity; all-event coverage is an optional audit, not a blocking semantic-completion requirement.
- Preserve prompt instructions, recent-turn context, and semantically important middle-of-session material across compaction.
- Define a post-compaction recovery bootstrap that restores Adaptive Agents prompting and explicitly identifies the session graph root index and retrieval behavior.
- Define a common compaction adapter contract: capture pre-compaction evidence when available, preserve exposed provider output or lifecycle provenance, and deliver bounded nonblocking recovery guidance. Do not launch another model or force exhaustive post-compaction indexing from a hook.
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
| Authoritative session record | Keep complete received details in one append-only ledger, with a model-authored root and purposeful topical subindexes; retrieve selected payloads directly in bounded pages rather than requiring generated event copies, packets, archival trees, or a mirror | Capture preserves evidence while model-owned navigation adds meaning; duplicate payload documents add I/O and failure paths without certifying semantic recall. |
| Current Codex format | Deterministic `ledger.md` with stable event/text-part anchors; runtime 1.2/template 14. JSON/JSONL recall sessions are deprecated and require a fresh conversation, with no migration or dual reader/writer | Nothing is shipped; avoid carrying a compatibility layer for an abandoned format. Preserve historical evidence without claiming runtime support. |
| Session storage and identity | Store sessions under a user-scoped root such as `~/.adaptive-agents/sessions/<harness>/<adaptive-session-uuid>/`, with a manifest recording provider identity when available; provide the session root explicitly during recovery | A common location avoids dependence on project layers or private harness stores, while harness namespacing and adapter-owned identity prevent collisions and unreliable session inference. |
| Discovery model | Use a stable root `INDEX.md` with an incrementally expandable hierarchy of sub-indexes and detail records; keep the graph flat for small sessions and introduce layers as detail grows | A hierarchical graph keeps high-level navigation compact while preserving discoverable paths to arbitrarily detailed session evidence. |
| Graph correctness | Preserve source identity and declared-link validity; unindexed events remain discoverable through bounded ledger search and reads | Selective navigation must not discard evidence, but missing semantic links must not cause conversation-blocking paperwork. |
| Semantic navigation | Keep selective meaningful breadcrumbs alongside the authoritative ledger; use bounded source search/read tools when a useful route is absent | Event categories account for records but do not tell the model why a detail matters. Source search preserves discovery without a compulsory parallel inventory. |
| Semantic authority | Let the model choose breadcrumb labels, topics and relationships, including whether a routine event needs a route; validate declared references | Meaning is model-supplied. Capture completeness is independent of semantic coverage. |
| Event accounting | Assign every retained user message, assistant message, tool call, tool result, instruction, and other retained event a stable identifier and preserve a deterministic fallback path when semantic classification is incomplete | Model-directed organization must not make capture completeness depend on successful semantic interpretation. |
| Validation authority | Deterministic capture and explicit validation prove source integrity, identifiers and declared-link resolution; the model owns topical selection | Missing topics do not invalidate retained history. Executable checks cannot certify semantic completeness. |
| Compaction accuracy boundary | Preserve the compaction boundary as provenance, not a mandatory topic-completion denominator. Measure retrieval correctness, retention and foreground overhead separately | Frozen coverage still caused prolonged productive retry loops; eliminating the compulsory inventory addresses the incentive rather than adjusting retry limits. |
| Compaction recovery bootstrap | Restore both the active Adaptive Agents guidance and an explicit session-graph discovery instruction pointing to the root index | Retaining the graph is useless if compaction leaves the model unaware of either the operating guidance or the graph's existence. |
| Compaction adapter contract | Preserve exposed provider output or lifecycle evidence, restore guidance and source discovery, and continue the user's task without a coverage audit | Provider compaction is external. Recovery must not turn a short user reply into exhaustive maintenance; offline/background indexing is deferred. |
| Recall boundary | Treat the active session as the first-class recall scope | The immediate problem is surviving compaction within a conversation; broader memory should remain a separate concern. |
| Harness boundary | Keep the capability contract in the epic and put lifecycle/hook mechanics in harness-specific children | Different agents expose different events, storage locations, and prompt-injection mechanisms. |
| Cross-harness catalog | Do not require a global cross-harness session index for active recall; treat cataloging as optional future functionality | Active recovery only needs the current session root, avoiding unnecessary privacy, locking, and unbounded-growth concerns. |

## Cross-harness Maintenance Findings

The active child now packages the tested Markdown-only runtime. Its isolated
managed-launcher trial passed native capture, early topic evolution, real
compaction and four fresh-context source-backed questions. Complete short search
excerpts are valid evidence; facts need not each receive a topic entry. The user
has upgraded to runtime 1.2.0/template 14 and demonstrated real Desktop capture,
manual compaction, recovery-context delivery and a correct source-backed lookup
from a natural question. See the [Desktop milestone](../active/PL-20261027-total-recall-codex-installer-hardening.memory.md#desktop-markdown-recall-milestone).
The graph remained empty and raw search exceeded the helper budget; topic
maintenance, bounded retrieval discipline, automatic-threshold compaction,
long-session and cross-platform acceptance remain open. JSONL findings below
are historical, not current migration, coverage or repair requirements.

The 2026-11-02 desktop pivot supersedes mandatory frozen coverage and productive Stop retry policies in the historical findings below. The supplied 447-event snapshot eventually passed coverage, but took about 6m38s after a short reply and produced a 43,541-byte flat root. The active child now tests selective topics, source-search fallback and nonblocking recovery using Luna CLI replay of received narrative content; original sessions remain immutable. Small-fixture successes and earlier repair evidence are retained, not reclassified as desktop-scale acceptance.

The active [installer-hardening memory](../active/PL-20261027-total-recall-codex-installer-hardening.memory.md) records the compaction repair evidence and falsified hypotheses:

- A captured checkpoint or persisted "maintenance requested" diagnostic is not evidence that a model received the request or updated `INDEX.md`. Verify delivery, actual topical graph edits, bounded snapshot coverage, and meaningful retrieval separately.
- Freeze each compaction maintenance snapshot. Later captured events remain pending for a later snapshot; maintenance must not chase its own growing ledger or permanently exempt the tail.
- Bound the source material per pass, not total useful work: five 64-event batches cannot cover a 365-line gap. Count stalled attempts separately from productive batches and report incomplete work explicitly.
- Use the harness's documented model-visible recovery/continuation channel. Codex compact recovery now requests immediate repair and Stop supplies further batches in the current model session. Its correct Stop schema is `decision: "block"` / `reason`, not `continue: false`.
- Measure complete hook execution against its deadline, including filesystem I/O and validation, and expose hook failures. Avoid rewriting unchanged derived artifacts or repeatedly rereading the same ledger for individual links.
- Current automated evidence covers 365-line completion across more than five adapter subprocess batches. The first real app-server proof was blocked by workspace ACLs; subsequent assistant-owned tests using normal inherited workspace ACLs now pass model-authored indexing and fresh-context retrieval without weakening the sandbox. Desktop/automatic-compaction acceptance remains separate.
- Later native desktop evidence proves model-authored edits but exposes a tool-content blind spot: Codex emits `tool_response`, while preview helpers and fixtures assumed `tool_output`. Capturing and linking a tool event under an execution-related topic is not sufficient to make its internal subjects discoverable. Use actual harness payload shapes, bounded inspection of large result bodies, and topic-driven retrieval tests isolated from original source files; do not equate event-line coverage with complete semantic recall.
- The Codex version-7 corrective slice now implements one payload store, a model-authored topical root, minimal operational state, and ledger diagnostics. Routine event copies, automatic packets, archival hierarchies, and the JSON mirror are removed; historical artifacts and valid legacy source links are preserved. JSON-only migration remains explicit and additive.
- The reproducible opt-in dogfood uses actual manual compaction and a fresh independent thread, with the synthetic source deleted. Distinct calibration, release, and nesting routes lead to the same retained tool event; every bounded page and the original user instruction are read, then exact values, rationales, restrictions, and citations are verified. Structural coverage alone is not semantic certification.
- Carry these lessons to other harnesses: bound serialized source bytes (Codex: 4,096) and maintenance-feedback bytes (8,192 UTF-8), preserve the frozen snapshot, and retain advancing maintenance outcomes even when Stop payloads repeat identically. The independent retrieval thread is a testing mechanism, never extra runtime hook infrastructure. Codex proof does not establish another harness's delivery or semantics.
- **Ordered provenance captured:** the [active memory's evidence record](../active/PL-20261027-total-recall-codex-installer-hardening.memory.md#ordered-recall-provenance-evidence) links the persistent synthetic trace and exact commands. In the original thread after another real compaction, the model answered `UNKNOWN` without tools, then read the root, followed a model-authored survey subindex, selected ledger range L4-L4, and returned the accession from its output. This is the reference for future harness iterations; citations and unordered command lists alone are insufficient.
- **Acceptance limitation retained:** the requested value is absent from inspectable compacted text, graph Markdown, and the question, but Codex also retains opaque compaction state. Full internal-context absence is explicitly unproven, not inferred from an encrypted representation. Preserve this distinction between observed failed unaided recall followed by source retrieval and a stronger claim about every part of model context.
- **Wire fidelity and evidence preservation:** the [active memory's Unicode diagnosis](../active/PL-20261027-total-recall-codex-installer-hardening.memory.md#unicode-capture-failure-and-evidence-boundary) records proven locale-dependent loss of long final replies, the strict UTF-8 fix, and the test gap caused by ASCII-escaped fixtures. Every harness needs raw-byte/native-launcher checks and real compaction/retrieval proof. Supplied failed sessions are read-only evidence, not repair targets; manual index reconstruction cannot prove a hook fix. The strengthened isolated dogfood includes long Unicode assistant replies and tool results without manual graph edits.
- **Unicode proof captured:** the [active memory's result and persistent report](../active/PL-20261027-total-recall-codex-installer-hardening.memory.md#unicode-dogfood-result) records exact capture of a 24,547-character final reply, six required content topics, complete frozen coverage, 19 fresh-thread retrieval checks and 14 same-thread ordered provenance checks after another real compaction. Forty-two hook completions had no failures. This is assistant-owned synthetic evidence, separate from supplied failed sessions and the earlier ASCII reference; retain the model/scale/desktop/automatic-compaction limitations.
- **Installed native artifacts retained:** the [active memory's native evidence](../active/PL-20261027-total-recall-codex-installer-hardening.memory.md#native-result-and-repeatability-limit) identifies original normal-store indexes, ledgers and transcripts, not reconstructed report-only artifacts. Version 9 first addressed executable reader discovery and packaging 1.0.1 fixed Windows inherited access; template 12 and runtime 1.0.4 use install-manifest interpreter/stable-launcher paths and clearer semantic maintenance guidance. Runs 8 and 9 passed consecutively with source-line-specific content topics and ordered retrieval; earlier coarse/mixed runs remain preserved. See [semantic-route dogfood evidence](../active/PL-20261027-total-recall-codex-installer-hardening.memory.md#semantic-route-quality-dogfood). This supports repeatability for the tested fixture/model, not universal completeness. Desktop UI and automatic-compaction behavior remain unverified.
- **Reader paths resolved from installation:** template version 10 and runtime 1.0.2 store interpreter and stable launcher paths in the install manifest, avoiding version-specific adapter paths in newly generated indexes. The installed command passed bounded-read verification with empty PATH. Existing version-9 evidence indexes were not rewritten. See the [active memory](../active/PL-20261027-total-recall-codex-installer-hardening.memory.md#install-resolved-reader-paths).

## Related Work

- [Completed ChatGPT Codex integration](../closed/PL-20260711-chatgpt-codex-support/PL-20260711-chatgpt-codex-support.sdd.md)
- [Codex Total Recall Foundation child](PL-20261027-total-recall/PL-20261027-total-recall-codex-foundation.md)
- [Codex Total Recall Installer and Upgrade child](PL-20261027-total-recall/PL-20261027-total-recall-codex-installer.md)
- [Total Recall Session Graph Quality and Index Contract child](PL-20261027-total-recall/PL-20261027-total-recall-session-graph-quality.md)

## Children

| Work item | Status | Depends on | Evidence / next action |
|---|---|---|---|
| [Codex Total Recall Foundation](PL-20261027-total-recall/PL-20261027-total-recall-codex-foundation.md) | Completed | None | Foundation adapter, deterministic graph validation, hook provisioning contract, and focused/dogfood evidence are complete; installer-owned permissions are implemented, while semantic maintenance and named-rule recovery remain open in the session-index follow-up. |
| [Codex Total Recall Installer and Upgrade](PL-20261027-total-recall/PL-20261027-total-recall-codex-installer.md) | Completed | [Codex Total Recall Foundation](PL-20261027-total-recall/PL-20261027-total-recall-codex-foundation.md) | Completed with limitations; see immutable [closure SDD](../closed/PL-20261027-total-recall-codex-installer/PL-20261027-total-recall-codex-installer.sdd.md). Verified native Windows installation and graph capture; portability and deeper failure/health coverage are transferred to the hardening child. |
| [Total Recall Session Graph Quality and Index Contract](../closed/PL-20261027-total-recall-session-graph-quality/PL-20261027-total-recall-session-graph-quality.sdd.md) | Completed | [Codex Total Recall Foundation](PL-20261027-total-recall/PL-20261027-total-recall-codex-foundation.md) | Completed with deferred automatic-threshold/repeated-dogfood validation; immutable closure packet preserves implementation and evidence. |
| [Codex Total Recall Installer Hardening](PL-20261027-total-recall/PL-20261027-total-recall-codex-installer-hardening.md) | Active | [Codex Total Recall Installer and Upgrade](PL-20261027-total-recall/PL-20261027-total-recall-codex-installer.md) | Runtime 1.2.0/template 14 now has a [real Desktop Markdown recall milestone](../active/PL-20261027-total-recall-codex-installer-hardening.memory.md#desktop-markdown-recall-milestone): manual compaction and natural source-backed lookup without graph repair. Remaining: scripts cleanup, proactive topic quality, bounded-helper discipline, installer/platform/rollback checks and automatic-threshold/scale acceptance. Earlier ordered provenance and failed repetitions remain historical evidence. |
