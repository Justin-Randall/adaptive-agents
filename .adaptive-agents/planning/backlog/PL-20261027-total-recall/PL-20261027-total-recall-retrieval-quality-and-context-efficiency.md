# Backlog: Total Recall Retrieval Quality and Context Efficiency

Plan: PL-20261027-total-recall-retrieval-quality-and-context-efficiency

Parent: [Total Recall for Session Details](../PL-20261027-total-recall.md)

Status: Backlog

Readiness: Needs Review: qualification scope, quality/context thresholds, deployment footprint and retrieval-model choice require approval before activation.

Test approach: Compare the existing bounded reader/search with one coherent retrieval candidate against frozen, answer-blind evidence; measure source-backed accuracy, appropriate abstention, total answering-model context and usable latency, and exercise stale indexes, isolation, rebuilds and deployment failure paths.

## Objective

Qualify a model-neutral retrieval approach that delivers higher-quality,
source-supported answers with lower answering-model context cost. Quality and
context efficiency take priority over speed, while latency must remain usable.
Produce a bounded go/no-go decision, not an open-ended series of retrieval tweaks
or an assumed commitment to embeddings, a database or a framework.

## Problem Spec

Total Recall can preserve and recover details, but successful recovery can expose
too much irrelevant text or require repeated searches. A selective topic graph
and chronological literal matches do not by themselves establish efficient
evidence selection, semantic matching or reliable handling of unsupported
questions. An additional retrieval layer may help, but brings model, storage,
privacy and deployment obligations that must be evaluated as part of the solution.

This is a separate potential optimization, not a refinement, activation or
acceptance gate for the current installer-hardening work unit.

## Scope

Qualify one complete candidate against the current baseline, including evidence
selection, context packaging and operational costs; recommend adoption, rejection
or a separately scoped implementation item.

Deferred: production integration, live-session changes, multiple backend
implementations, semantic-graph construction, cross-session memory and any
expansion of the current active plan.

## Learnings to Carry Forward

These observations originate in work unit
`PL-20261027-total-recall-codex-installer-hardening`. Local milestone checkpoint
`ca4f7df` retains the Desktop and frozen-recall evidence; the later Graphify
inspection is summarized here without requiring its disposable output directory.

- **Recovery already works for tested facts.** Desktop capture, manual compaction
  and a natural question led to an actual source lookup and a correct answer.
  The question supplied no answer, source identifier or retrieval choreography.
  This does not prove that the answer was absent from all retained model context.
- **Topic navigation and bounded search are different capabilities.** The Desktop
  index had no model-authored topics, but did contain working bounded search/read
  commands. The model instead used raw search returning 20,099 truncated
  characters. Do not diagnose this as ignoring an existing populated topic index.
- **A complete excerpt is evidence.** Frozen-context trials recovered facts absent
  from navigation. A short search excerpt containing the complete answer does
  not require a redundant second read; expand only when context is insufficient.
- **Negative lookup cost was not a factual-recall failure.** An unrecorded witness
  name correctly remained `UNKNOWN`, but required ten calls and exceeded the
  trial's eight-call guardrail. Metadata noise included `name` matching
  `hook_event_name`. Preserve failed historical reports rather than relaxing
  their original gates or relabeling correct recovery as incorrect.
- **Structural completeness is not semantic quality.** Earlier mandatory coverage
  eventually passed, but a short follow-up took about 6m38s and produced a
  43,541-byte flat root. Do not restore all-event topic coverage, Stop gates or
  compulsory indexing conversations to improve retrieval.
- **Fast graph misses are not justified abstention.** The user-generated Graphify
  graph had 638 AST-origin nodes describing document/event structure and no node
  records containing the known narrative subject. Queries missed a recorded fact
  in about 0.46 seconds; direct bounded ledger lookup found relevant evidence.
  This tests that structural graph, not semantic GraphRAG generally, and is not
  an end-to-end fresh-model performance comparison.
- **Source fidelity is a separate requirement.** Preserve exact received text,
  Unicode, event identity and stable anchors. Retrieval cannot recover upstream
  truncation. Supplied histories, roots and failed evidence are read-only;
  reconstructed topics or repaired history cannot demonstrate a retrieval fix.

## Candidate Direction and Boundaries

- Compare the existing bounded literal search with ranked lexical retrieval and
  one justified hybrid candidate: lexical plus semantic candidates, rank fusion,
  learned reranking where warranted, then a small sufficient evidence set.
  Rank fusion alone is not a learned relevance model. Do not assume more
  components improve quality.
- Evaluate an embedded local engine such as [LanceDB](https://docs.lancedb.com/search/hybrid-search)
  versus a service-based option such as [Qdrant](https://qdrant.tech/documentation/search/hybrid-queries/)
  only as needed to select the candidate. A server adds lifecycle obligations;
  Qdrant's Python local mode is documented for prototyping/testing, not proof of
  production-service equivalence. No product or embedding model is selected.
- Model-neutral means independence from the answering model, not necessarily
  model-free retrieval. A local encoder/reranker may be independently versioned.
  Pin compatible document/query encoders, revision, preprocessing and index
  profile. Answering-model changes must not require reindexing; incompatible
  embedding-profile changes require an explicit rebuild.
- Keep Markdown evidence authoritative. Any search index is a rebuildable
  derivative, never a second authoritative history or revived JSONL runtime.
  Review storage and ownership changes before adoption; this item does not
  amend the current architecture by implication.
- Retrieval must preserve exact source handles, useful surrounding context,
  original-versus-quoted evidence provenance, revisions and contradictions.
  Reduce duplicate echoes and metadata noise without silently excluding valid
  evidence or always preferring the newest statement.
- Capture and Stop must not wait for model inference or expensive indexing.
  Expose index freshness; include the unindexed tail or report incomplete search
  coverage explicitly. Enforce session isolation and explicit failure reporting.
  The default candidate must not require sending session content to a third party.
- Treat retrieved text as evidence, not instructions. Similarity scores or zero
  matches do not prove absence; distinguish supported answers, related but
  insufficient evidence and unsuccessful retrieval.

## Qualification Before Adoption

- At activation, approve measurable quality, context and latency gates, hardware
  and language/code coverage, runtime/model footprint and the single candidate.
  Expand the test approach into an executable plan; split production adoption
  into another item if it would exceed a single bounded work unit.
- Freeze original evidence before generating probe turns; exclude later questions,
  search echoes and answers from candidate indexes. Use fresh answering contexts
  with natural questions, no answers or source hints, and independent ground
  truth. Include exact identifiers, paraphrases, revisions, contradictions,
  intentionally unindexed facts and genuinely unsupported attributes.
- Measure correctness, completeness, source support and false abstentions or
  invented answers. Count total model-visible retrieval/navigation material,
  repeated calls and retries, not only the final excerpt. Report actual tokens
  when available and label byte-based proxies; account for auxiliary-model
  computation/context separately.
- Measure end-to-end latency and slow outliers separately from retrieval timing,
  indexing cost and cold starts. Verify installation, offline operation after
  provisioning, permissions, concurrent sessions, missing models, profile changes,
  stale/corrupt caches, rebuilds and fallback diagnostics in isolated profiles.
- Preserve baseline/candidate hashes, ordered tool evidence, failures and explicit
  limitations. A winning decision requires better supported answers per context
  cost with usable latency and acceptable operational burden, not a faster
  unsupported `UNKNOWN`. Do not repeat or retune held-out tests into a pass.

## Related Work

- [Installer-hardening source item](PL-20261027-total-recall-codex-installer-hardening.md):
  originating work unit; resolve its current or archived evidence through the
  planning router when activating this item.
- [Session graph quality closure](../../closed/PL-20261027-total-recall-session-graph-quality/PL-20261027-total-recall-session-graph-quality.sdd.md):
  prior navigation and compaction work, not acceptance of this optimization.
