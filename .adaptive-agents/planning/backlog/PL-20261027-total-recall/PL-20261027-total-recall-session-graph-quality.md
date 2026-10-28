# Backlog: Total Recall Session Graph Quality and Index Contract

Plan: PL-20261027-total-recall-session-graph-quality

Parent: [Total Recall for Session Details](../PL-20261027-total-recall.md)

Status: Completed

Closure: Completed with approved deferred provider-specific validation follow-up. See the immutable [closed SDD](../../closed/PL-20261027-total-recall-session-graph-quality/PL-20261027-total-recall-session-graph-quality.sdd.md).

Depends on: [Codex Total Recall Foundation](PL-20261027-total-recall-codex-foundation.md)

Readiness: Ready: user approved activation after reconciling the authoritative event ledger, recursive semantic graph, context-packet, budget, and session-index template contracts.

Test approach: Write focused failing graph-quality and validator tests first for versioned index structure, semantic coverage declarations, source provenance, context links, turn-bundle or context-capsule reachability, preservation of raw detail, and compatibility with existing graphs; then run repeated pre-compaction and post-compaction dogfood with seeded instructions, decisions, middle-session facts, and tool evidence to measure breadcrumb creation, contextual retrieval, and correct application of recovered guidance.

## Objective

Define and prove the quality contract for a Total Recall session graph. Use a versioned common `INDEX.md` and related record layout to make semantically important session details discoverable with useful surrounding context, while preserving every captured detail and enforcing deterministic reachability and non-orphaning invariants.

## Problem Spec

The Codex foundation currently produces structurally valid graphs: raw hook events are retained, fallback indexes are generated, and deterministic validation proves that retained records remain reachable. However, the semantic layer is not yet reliable enough for the scope of a long conversation. In the current seven-session sample, only three graphs had model-authored semantic breadcrumbs; four retained the placeholder, including a compaction dogfood graph. Even when a breadcrumb exists, it points directly to a raw event payload, leaving the model to reconstruct surrounding user, assistant, tool-call, tool-result, and decision context by traversing chronological records.

The work therefore needs to address more than seeding a root `INDEX.md`. It must define what constitutes sufficient semantic coverage, how semantic claims retain source provenance, how a breadcrumb exposes useful neighboring context without duplicating or discarding raw detail, how the graph expands into topic indexes or context capsules, and how retrieval quality is evaluated after compaction. Deterministic code can prove identity, links, anchors, reachability, preservation, and update safety; model-facing evaluation must establish whether the graph is meaningful and useful.

## Agreed Architecture Direction

Total Recall remains a graph, but it is an adaptive evidence graph rather than a fixed two-level index. The graph may grow through any number of semantically meaningful sub-topic indexes when session scale requires additional narrowing. Depth is not itself a failure condition; each navigation node must remain small enough to serve as a useful retrieval step so that recalling history does not immediately trigger another compaction.

The model owns semantic organization. It determines which events belong together in a context packet, what topics and sub-topics are meaningful, how indexes should be split, what each node contains, and why a breadcrumb matters. A large root index becomes a topic-of-topics: it gives the model enough semantic orientation to choose a narrower index or context packet without loading the entire session.

The implementation should separate three layers:

1. An append-only JSONL event ledger containing complete authoritative captured records and stable event identifiers.
2. Model-oriented context packets that gather semantically related user messages, assistant responses, tool calls, tool results, decisions, evidence, and useful surrounding context without replacing the raw records.
3. A recursive Markdown index graph in which the root and sub-indexes provide descriptive semantic navigation to packets and, when necessary, exact raw records.

The normal retrieval path should be short and context-efficient—root index to a useful topic index to a context packet—while allowing deeper paths when needed. Raw JSONL line ranges may be included as explicit reading instructions and human navigation hints, but stable event identifiers and validated source links are authoritative because arbitrary Markdown renderers may not honor line fragments.

Provider-reported context budgets are optional. When unavailable, the graph must remain valid and usable through conservative local heuristics such as byte/character size, estimated token count, entry count, description length, and first-hop retrieval cost. Budget pressure is an optimization and rebalancing signal, not a reason to discard details or fail the feature. Oversized indexes should remain recoverable, be marked for rebalancing, and retain deterministic fallback navigation until a validated model-authored split is available.

### Concise Seed-Template Guidance

The seeded session `INDEX.md` should give the model a short operational contract rather than repeat the full backlog design. The proposed template guidance is:

> Maintain this graph as a semantic map, not a full summary. Add concise, descriptive breadcrumbs for important instructions, decisions, requirements, unresolved questions, preferences, milestones, evidence, and artifacts; say what each target contains and why it matters. You decide topical groupings, context packets, and how many nested topic indexes are useful; treat the root as a topic-of-topics and split oversized indexes without discarding detail. Prefer a first hop to a context packet with related user, assistant, and tool context. Preserve the raw ledger, link derived nodes to stable source events, and keep event/chronological indexes as fallback navigation. Validation proves links, source IDs, reachability, and non-orphaning, not semantic quality. If provider budgets are unknown, stay concise and rebalance conservatively.

The implementation should load this contract from a maintained template artifact rather than embedding the prose in the Python adapter. The template must remain concise enough to survive compaction while still naming the model-owned semantic responsibilities and the code-owned reachability guarantees.

## Session INDEX.md Template Deliverable

The feature must provide a versioned, maintained seed template for the session root `INDEX.md`. This is not merely a formatting sample: it is the compact model-facing contract that establishes how the graph should be maintained during the pre-compaction pass and consulted after recovery.

The template must:

- identify `INDEX.md` as the semantic navigation surface and topic-of-topics;
- instruct the model to create descriptive breadcrumbs and semantically meaningful context packets;
- permit recursive topic and sub-topic indexes whenever the session grows, without imposing a fixed depth;
- preserve the authoritative raw event ledger and stable source-event provenance;
- identify chronological and event-type indexes as deterministic fallback navigation;
- state that validation proves links, identifiers, reachability, and non-orphaning, not semantic quality;
- instruct conservative rebalancing when provider context budgets are unavailable or uncertain; and
- remain concise enough that the recovery contract does not consume the context it is intended to protect.

The template should use clearly bounded managed sections so deterministic regeneration can update its framework without overwriting model-authored breadcrumbs. Its version and compatibility rules belong in the session manifest, and existing valid session indexes must remain readable when the template evolves.

## Scope

In scope:

- Define a versioned, harness-independent root `INDEX.md` contract, including required recovery/bootstrap sections, semantic-breadcrumb regions, fallback navigation, extension points, and model-authored regions.
- Define semantic coverage expectations for important instructions, decisions, requirements, unresolved questions, preferences, milestones, durable facts, evidence, artifacts, and next actions.
- Define the relationship between the authoritative event ledger, raw event records, chronological/event-type indexes, semantic topic indexes, turn bundles, and context capsules.
- Design a raw and derived Markdown record layout that preserves exact captured details while making bounded surrounding context easy for the model to retrieve.
- Preserve source-event provenance for every semantic breadcrumb or context capsule and require stable links back to authoritative records.
- Add deterministic validation for template/version metadata, source identifiers, link and anchor resolution, context relationships, graph reachability, retained-detail accounting, and backward compatibility with existing graphs.
- Add repeatable quality evaluation using seeded conversations and compaction dogfood, including old, recent, middle-session, and tool-derived details.
- Update the Codex foundation adapter to render or consume the common contract without replacing model-authored semantic content or weakening the existing event ledger.

Out of scope:

- Installer portability, permissions, trust review, or transactional upgrade hardening; see [Codex Total Recall Installer Hardening](PL-20261027-total-recall-codex-installer-hardening.md).
- Other harness implementations beyond defining extension points.
- Retention, pruning, archival, encryption, or cross-session memory policy.
- Treating a provider transcript format as a stable persistence API where the harness does not guarantee one.

## Proposed Quality Contract

- Every retained raw event remains authoritative and reachable from the session root, regardless of whether semantic classification succeeds.
- Every semantic breadcrumb states what the target contains and why it matters; opaque event IDs and generic labels are insufficient by themselves.
- Every semantic breadcrumb or derived context node links to one or more stable source events and cannot hide or replace the underlying raw records.
- A breadcrumb should normally lead to a bounded context view—such as a turn bundle or context capsule—that links the source event, related events in the same interaction, and relevant neighboring evidence.
- Context views may summarize or organize, but must not become the only copy of a retained detail.
- Root indexes remain compact. As the graph grows, semantic topics, time ranges, session phases, turn bundles, or context capsules may be delegated to sub-indexes while the root retains descriptive links to those indexes.
- The graph has no fixed maximum depth. Rebalancing should add semantic layers whenever needed to keep individual indexes and first-hop retrieval paths within a conservative or observed budget.
- Exact provider context telemetry is optional. Missing telemetry must degrade to conservative local heuristics and diagnostics; it must not invalidate an otherwise reachable graph.
- Budget-related oversize conditions should preserve the last valid graph, retain fallback navigation, and request later rebalancing rather than dropping or hiding retained detail.
- Deterministic validation must reject broken links, invalid anchors, unknown source identifiers, unreachable retained records, invalid context references, and unsafe updates.
- Retrieval tests must measure whether the model can find and correctly apply seeded important details after compaction, not merely whether a graph pointer or marker fact is present.

## Acceptance Criteria

- [ ] A versioned common session-index contract defines required sections, model-authored regions, extension points, compatibility rules, and the distinction between authoritative records and derived navigation.
- [ ] A maintained, versioned `INDEX.md` seed template exists as a separate artifact consumed by the harness adapter, contains the concise graph-maintenance contract above, and preserves model-authored semantic content across regeneration.
- [ ] The graph-quality contract defines measurable semantic coverage expectations and a repeatable evaluation fixture for instructions, decisions, requirements, unresolved questions, durable facts, evidence, artifacts, recent context, middle-session context, and tool-derived details.
- [ ] Raw event records retain complete captured payloads while a deterministic or model-assisted layout provides bounded surrounding context through turn bundles, context capsules, or an equivalent linked structure.
- [ ] The graph supports recursive topic-of-topics and sub-topic indexes without imposing a fixed maximum depth, while each index and first-hop retrieval path is subject to configurable or heuristic size guidance.
- [ ] Semantic breadcrumbs and context views preserve stable source provenance and remain discoverable through the root index and any hierarchy of sub-indexes.
- [ ] Deterministic tests reject orphaned details, broken or invalid context links, unknown source identifiers, malformed version metadata, unsafe graph rewrites, and incompatible older indexes; existing valid graphs remain readable even when provider budget telemetry is absent.
- [ ] Budget-pressure handling preserves the last valid graph, reports heuristic or unknown budget mode, and supports validated rebalancing without deleting or hiding retained detail.
- [ ] Focused tests run before implementation changes and cover preservation of model-authored content, idempotent index updates, graph expansion/rebalancing, and raw-detail retention.
- [ ] Repeated pre-compaction and post-compaction dogfood demonstrates meaningful breadcrumb creation, useful surrounding-context retrieval, and correct application of seeded Adaptive Agents/session guidance; a pointer-only or marker-fact result does not pass.

## Design Questions for Activation

1. Should semantic breadcrumbs target context capsules directly, with capsules linking to raw events, or should deterministic turn-bundle indexes be the primary target?
2. What event grouping is reliable enough for a turn bundle: provider `turn_id`, sequence windows, tool-call/result pairing, or a combination?
3. How should the graph represent semantic material that spans several turns or has multiple source events?
4. Which semantic coverage claims can be checked deterministically, and which must remain evaluation evidence rather than hard validation rules?
5. What size or density heuristic should trigger rebalancing into topic indexes, time/phase indexes, or context capsules without risking orphaned details?
6. Which conservative local sizing signals best predict retrieval safety when the provider does not expose context limits, and how should observed dogfood results calibrate them?

## Related Work

- Parent epic: [Total Recall for Session Details](../PL-20261027-total-recall.md)
- Foundation dependency: [Codex Total Recall Foundation](PL-20261027-total-recall-codex-foundation.md)
- Installer predecessor: [Codex Total Recall Installer and Upgrade](PL-20261027-total-recall-codex-installer.md)
- Installer follow-up: [Codex Total Recall Installer Hardening](PL-20261027-total-recall-codex-installer-hardening.md)
