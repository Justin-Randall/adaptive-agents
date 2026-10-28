# PL-20261027: Total Recall Session Graph Quality and Index Contract

- Work Unit: PL-20261027-total-recall-session-graph-quality
- Status: Completed
- Origin: Backlog activation
- Branch: `pl-20261027-total-recall`
- Parent Epic: [Total Recall for Session Details](../../backlog/PL-20261027-total-recall.md)
- Source Backlog: [Total Recall Session Graph Quality and Index Contract](../../backlog/PL-20261027-total-recall/PL-20261027-total-recall-session-graph-quality.md)
- Dependency: [Codex Total Recall Foundation](../PL-20261027-total-recall-codex-foundation/PL-20261027-total-recall-codex-foundation.sdd.md)
- Memory: [PL-20261027-total-recall-session-graph-quality.memory.md](PL-20261027-total-recall-session-graph-quality.memory.md)

## Progress

> Keep this checklist current after each meaningful change. Check off completed stages, add discovered work, and record validation evidence in the linked memory.

- [x] Activate this child and synchronize planning metadata.
- [x] Load the Total Recall epic, backlog item, closed foundation handoff, and applicable guidance.
- [x] Reconcile the authoritative event ledger with Markdown indexes and context packets as derived model-facing views.
- [x] Capture the versioned session `INDEX.md` seed-template deliverable and concise model-maintenance contract.
- [x] Define the versioned session-index schema, managed regions, model-authored regions, provenance fields, and compatibility rules.
- [x] Define the context-packet and surrounding-context layout over the authoritative event ledger.
- [x] Define recursive topic-of-topics graph balancing and conservative budget heuristics without imposing a minimum or maximum depth.
- [x] Define the mixed index-entry contract: each index may directly locate `ledger.jsonl` line ranges or delegate named topics to narrower indexes, and sub-indexes may mix both forms recursively.
- [x] Implement focused failing tests for schema, provenance, context relationships, reachability, preservation, idempotence, and compatibility.
- [x] Implement the template, graph-quality behavior, and deterministic validation changes required by the approved design.
- [ ] Run repeated pre-compaction/post-compaction dogfood with seeded instructions, decisions, middle-session facts, evidence, and tool results. Use the cheapest capable model available for these sessions, such as GPT-5.6-luna with light or medium reasoning.
- [ ] Prove meaningful semantic retrieval and correct application after compaction; pointer-only or marker-only recall is insufficient.
- [x] Complete the plan memory review, completion review, and required project validation before closure.

## Objective

Define and prove the quality contract for a Total Recall session graph. Use a versioned common `INDEX.md` template and related record layout to make semantically important session details discoverable with useful surrounding context, while preserving every captured detail and enforcing deterministic reachability and non-orphaning invariants.

## Specifications

- The append-only event ledger is authoritative for complete captured details, stable event identifiers, and stable one-based JSONL line locators.
- Markdown indexes and context packets are derived, model-oriented semantic navigation and retrieval views; they must preserve source provenance and never replace the ledger.
- The model owns topical grouping, semantic labels, context-packet boundaries, and recursive index decomposition.
- The root `INDEX.md` is a topic-of-topics and may mix direct `ledger.jsonl#Lstart-Lend` locators with purposeful delegation through any number of semantically useful sub-index layers; no fixed maximum depth is imposed.
- Each index and first-hop retrieval path should remain context-budget safe using provider telemetry when available and conservative local heuristics otherwise.
- Structural validation is authoritative for links, anchors, source IDs, reachability, retained-detail accounting, update safety, and non-orphaning. Semantic quality requires model-facing evaluation.
- Budget pressure must trigger diagnostics or rebalancing, not loss of retained detail or invalidation of an otherwise reachable graph.
- The session-index seed template is a separate versioned artifact consumed by the adapter, with bounded managed sections that preserve model-authored semantic content.

## Scope

In scope:

- Versioned root `INDEX.md` contract and separate seed-template artifact.
- Semantic breadcrumb and context-packet quality expectations.
- Authoritative ledger, derived packet, recursive index, and provenance relationships.
- Deterministic validation for graph integrity, reachability, context references, retained-detail accounting, compatibility, and safe updates.
- Conservative budget heuristics and rebalancing behavior when provider context limits are unavailable.
- Focused regression tests and repeated Codex pre/post-compaction dogfood.

Deferred:

- Installer portability, permissions, trust review, and transactional upgrade hardening.
- Other harness implementations beyond extension points.
- Retention, pruning, archival, encryption, and cross-session memory policy.

## Acceptance Criteria

- [x] A versioned common session-index contract defines required sections, model-authored regions, extension points, compatibility rules, and the distinction between authoritative records and derived navigation.
- [x] A maintained, versioned `INDEX.md` seed template exists as a separate artifact consumed by the adapter and preserves model-authored semantic content across regeneration.
- [ ] The graph-quality contract defines measurable semantic coverage and a repeatable fixture for instructions, decisions, requirements, unresolved questions, durable facts, evidence, artifacts, recent context, middle-session context, and tool-derived details.
- [x] Raw records retain complete captured payloads with stable JSONL line locators while derived context packets provide optional bounded surrounding context without replacing source detail.
- [x] Recursive topic-of-topics and sub-topic indexes work without a fixed maximum depth, with configurable or heuristic size guidance for each node and first-hop path.
- [x] Semantic breadcrumbs and context views preserve stable provenance and remain reachable through the root and any hierarchy of sub-indexes.
- [x] Deterministic tests reject orphaned details, broken links, invalid context links, unknown source IDs, malformed metadata, unsafe rewrites, and incompatible older indexes.
- [x] Missing provider budget telemetry degrades to conservative heuristics and diagnostics without invalidating a reachable graph.
- [x] Focused tests cover model-authored-content preservation, idempotent updates, graph expansion/rebalancing, raw-detail retention, and compatibility.
- [ ] Repeated dogfood demonstrates meaningful breadcrumb creation, useful surrounding-context retrieval, and correct application of seeded guidance after compaction; pointer-only or marker-only recall does not pass.

### Deferred by approved closure

- The repeatability portion of the live dogfood criterion and independent automatic-threshold behavior remain provider-specific follow-up validation. One live explicit `/compact` run emitted `PreCompact` and `PostCompact`, recovered the four durable facts with meaningful explanations, and passed deterministic validation; bounded accumulation did not independently trigger the automatic threshold.
- The broad semantic-coverage fixture remains evaluation work rather than a claim that the validator certifies semantic usefulness. Focused tests and multi-topic dogfood provide coverage evidence, while future manual dogfood may open targeted bugs or backlog items.

## Closure Disposition

Completed with deferred provider-specific validation follow-up, approved by the user. The implementation, template, mixed direct/delegated locator contract, deterministic validator, focused regression suite, live explicit-compaction lifecycle, and meaningful post-compaction recovery evidence are preserved in this immutable packet.

## R&D Tasks

1. Compare context capsules with deterministic turn bundles and select the smallest reliable first-hop retrieval unit.
2. Determine reliable event grouping using provider turn IDs, sequence windows, tool-call/result relationships, and fallback rules.
3. Define how multi-turn semantic topics cite multiple source events without duplicating or orphaning detail.
4. Establish which semantic coverage claims remain evaluation evidence rather than hard validator rules.
5. Evaluate local size/density heuristics when provider context limits are unavailable and define rebalancing diagnostics.
6. Specify the template artifact format, version metadata, managed/model-authored boundaries, and migration behavior for existing indexes.

## Test Plan

For every implementation slice, write the focused failing test first, run it to confirm failure, make the smallest change, rerun the focused test, and broaden validation only after the focused check passes.

- Schema/template slice: test required sections, version metadata, managed-region preservation, model-authored-region preservation, and compatibility with existing valid indexes.
- Ledger/provenance slice: test complete raw retention, stable source IDs and JSONL line locators, direct line-range links, multi-source packets, exact source links, and rejection of unknown or orphaned references.
- Context-layout slice: test bounded packet construction, neighboring user/assistant/tool context, packet-to-ledger provenance, and fallback navigation.
- Recursive-graph slice: test mixed direct JSONL locators and purposeful nested topic delegation at arbitrary depth, oversized-node diagnostics, conservative rebalancing, idempotence, and last-valid-graph preservation.
- Validator slice: test broken links/anchors, unreachable events, malformed metadata, unsafe rewrites, fenced-payload handling, and backward compatibility.
- Dogfood slice: seed important instructions, decisions, middle-session facts, evidence, and tool results; force or observe compaction; inspect recovery guidance, graph traversal, retrieved context, and correct post-compaction application.

## DRY Assessment

- Template/schema and validator changes: scan required because a shared contract and validation behavior are being extended across generated indexes and tests; use the project’s configured duplication baseline if parallel serializers or validators are added.
- Context-packet and graph-balancing changes: scan required if new adapters, serializers, or parallel record formats are introduced; otherwise record a local duplication review.
- Documentation-only refinements: full scan not required; review for duplicated contract language between the epic, backlog item, template, and implementation artifact.

## Applicable Guidance

- [Manage planning skill](../../../skills/manage-planning/SKILL.md)
- [Project guidance index](../../../instructions/INDEX.md)
- [Project instructions](../../../instructions/project.instructions.md)
- [Project branch workflow](../../../instructions/branch-workflow.md)
- [Total Recall epic](../../backlog/PL-20261027-total-recall.md)
- [Closed Codex foundation handoff](../PL-20261027-total-recall-codex-foundation/PL-20261027-total-recall-codex-foundation.sdd.md)

## Initial Verification Evidence

- Activation is user-approved.
- The foundation dependency is closed and its deterministic graph validator and hook contract are available.
- The epic and child were reconciled so the event ledger is authoritative and Markdown is model-facing navigation/retrieval.
- Fresh multi-topic semantic dogfood produced five model-authored descriptive direct JSONL-range breadcrumbs and a meaningful same-session recovery summary across architecture, retrieval, hierarchy, validation, and evidence topics; external graph validation passed. No compaction lifecycle events were emitted, so the post-compaction acceptance criteria remain open.
- The existing focused Codex Total Recall test suite passed before this plan’s implementation changes.
