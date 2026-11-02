# PL-20261027: Codex Total Recall Installer Hardening

- Status: Active
- Work Unit: PL-20261027-total-recall-codex-installer-hardening
- Origin: Backlog activation
- Parent Epic: [Total Recall for Session Details](../backlog/PL-20261027-total-recall.md)
- Source Backlog: [Codex Total Recall Installer Hardening](../backlog/PL-20261027-total-recall/PL-20261027-total-recall-codex-installer-hardening.md)
- Dependency: [Codex Total Recall Installer and Upgrade](../closed/PL-20261027-total-recall-codex-installer/PL-20261027-total-recall-codex-installer.sdd.md)
- Memory: [PL-20261027-total-recall-codex-installer-hardening.memory.md](PL-20261027-total-recall-codex-installer-hardening.memory.md)

## Current Priority

**User-approved format decision:** JSONL is deprecated, not a supported
compatibility target. Nothing is released. Promote the proven Markdown path
into the installed Codex runtime, use it for new sessions, and explicitly reject
old JSON/JSONL sessions with a fresh-session instruction. Do not build migration,
dual readers or dual writers. Leave historical evidence files untouched; this
is not permission to delete or rewrite them. Installer upgrade verification
still preserves unrelated configuration and runtime integrity.

**Integration implemented:** source runtime 1.2.0/template 14 now packages the
tested Markdown serializer/capture/reader/search/topic guidance in the single
installed adapter. Canonical roots use the stable installed launcher, PostToolUse
delivers actual result handles, and Stop remains nonblocking. Markdown-only
installation, legacy rejection without mutation, raw UTF-8, empty-PATH readers,
upgrade/rerun and the direct installer entrypoint pass focused tests. The user
has now upgraded, reviewed the changed PostToolUse hook and demonstrated actual
Desktop capture, manual compaction and source-backed recall. No live profile
or supplied evidence was modified by the diagnosing agent.

Prove recoverability, not comparative speed: the complete received ledger makes
otherwise forgotten details available, explicit discovery instructions teach the
model to look for them, and a balanced model-owned topic graph gives useful
subjects, clues and evidence routes. Facts do not need individual index entries.
Keep the root lightweight, connect meaningful decisions/revisions, and permit
bounded search for details without direct routes. Maintenance cost and latency
are guardrails against conversational interference, not the purpose of recall.

The immediate behavioral test is a frozen post-compaction graph/ledger supplied
to fresh Luna contexts that never encountered the original details. Demonstrate
accurate recovery from actual source reads, not answer repetition from an index.
Keep actual compaction-hook integration as a separate previously exercised seam.
Markdown fidelity and proactive topic quality remain independent hypotheses.

Markdown is now the sole supported source format, with deterministic fidelity/append tests, a passing isolated packaged-runtime trial and a real Desktop manual-compaction/source-lookup milestone. This is not full topic-quality, bounded-retrieval, automatic-threshold, long-session or cross-platform acceptance. Graphify and other external graph engines remain deferred; do not install them, add dependencies or tailor the ledger to their parsers.

The live Desktop installation is now user-upgraded runtime 1.2.0/template 14. The old shared template remains for historical installations, not current format support. This work unit and installer-hardening scope remain active; no child is closed or newly activated. Supplied sessions remain read-only evidence. Historical runtime-1.1 evidence is retained in [CLI pivot proof](PL-20261027-total-recall-codex-installer-hardening.memory.md#luna-cli-pivot-proof).

### Desktop Milestone and Next Checkpoint

- The user demonstrated capture -> forced manual compaction -> delivered recovery guidance -> natural content question -> actual ledger lookup -> correct answer. The [Desktop evidence and qualifications](PL-20261027-total-recall-codex-installer-hardening.memory.md#desktop-markdown-recall-milestone) retain exact source identities and integrity baselines.
- The root still has no model-authored topics. Lookup used raw `rg` and returned 20,099 truncated characters, not the bounded helper. This is a source-backed recall milestone, not topic-quality, bounded-output, unaided-context-absence or automatic-threshold acceptance.
- A stale PostToolUse trust hash initially prevented result capture; the user resolved approval. Tests that freshly trust every isolated handler did not reproduce that upgrade condition. `--check` proves installed configuration/integrity, not effective approval.
- User approved a local milestone commit after validation, explicitly **without pushing**. Keep scripts cleanup and subsequent feature polish separate from this checkpoint; the active work unit remains open.

### Pivot Rationale and Boundaries

- The supplied desktop session eventually covered all 447 frozen events, but a simple "Thank you." took about 6 minutes 38 seconds to finish, with 16 blocked Stop continuations before the seventeenth Stop succeeded. The root grew from 3,976 to 43,541 bytes with 234 semantic links; 107 labels mentioned probes. This is a structural pass and a conversational/navigation failure.
- Fifteen of sixteen source-reading commands exposed only 260-character page previews to the model. Fetching source pages is not proof of semantic inspection. Successful index writes also mean the earlier permission concern did not prevent this run.
- Preserve every received payload independently of whether it receives a breadcrumb. The model chooses useful subjects and relationships; deterministic checks validate capture integrity, stable sources, declared links and read limits, not topic completeness.
- Prefer a compact root and purposeful subindexes, plus on-demand bounded ledger search followed by exact source reads. Do not require per-event/per-command links, a parallel payload store, or exhaustive source rereading after compaction.
- Incremental topical updates must remain lightweight and nonblocking. Background/offline model indexing is deferred: it adds cost, ownership and concurrency complexity and is not the selected first approach.
- The [parent epic](../backlog/PL-20261027-total-recall.md) and [architecture contract](../../ARCHITECTURE.md) separate received-payload retention from selective topical navigation. The old coverage audit and migration CLI are removed, not supported runtime options.
- Prior small-fixture successes remain valid evidence of their tested retrieval paths, not acceptance of desktop scale, topical completeness or foreground latency. Historical coverage/retry requirements below are superseded where they conflict with this pivot.
- **Semantic proof correction:** the passing CLI fixture explicitly directed Luna to inspect one event and create up to three routes from it. All three breadcrumbs pointing at that event are valid references, but the constrained task did not establish independent session-wide topic selection. Preserve the latency, retention and source-read evidence; do not treat the three-link root as proof of proactive topical organization.
- **Serialization boundary:** hooks already parse incoming JSON, construct an event envelope with identity/sequence/kind/time/fingerprint and the complete parsed payload, and serialize their own record. Markdown would replace deterministic serialization, not ask the model to author the ledger. Preserve payload values/types/text; current capture does not preserve original JSON whitespace or key order.
- **Source versus meaning:** hooks may emit stable event/field/within-event source boundaries, but not inferred topics. The model should proactively create and update subjects while context is available, group multiple useful source links beneath a topic, and introduce subindexes when meaningful subdivisions warrant them. Revisions and contradictions should connect old and new evidence without rewriting either.
- **Correct, high-quality and fast:** retention, navigation quality and overhead are independent gates. A small/fast index is not sufficient if it omits useful connections; correct retrieval is not sufficient if proactive indexing repeatedly interrupts ordinary work. Measure maintenance throughout the session, not only after compaction.
- **Incremental trigger:** a new meaningful subject, decision, constraint, evidence change or resolution should prompt a small model-owned topic update when useful. Reuse an existing topic before adding another; describe why each source matters. This is neither a mandatory tool call on every turn nor a Stop-enforced completeness check. Only link already-captured evidence; if a final reply is captured after the model finishes, defer its source link to a natural later opportunity rather than inventing a future address or forcing another turn.

## Progress

> Keep this checklist current as work proceeds. After each meaningful change, check off completed stages, add newly discovered work, remove eliminated work, and adjust plan-specific items so it accurately reflects what remains.

- [x] Activate the installer-hardening child with user approval and verify its installer dependency is completed.
- [x] Synchronize the child, parent epic, backlog index, and planning router.
- [x] Repair existing Project Layer planning-link validation failures before installer implementation.
- [x] Verify Codex hook-source behavior and define inline-hook migration that preserves user-authored entries while rejecting unrecognized managed state.
- [x] Add focused regression tests for inline `config.toml` hooks, managed `hooks.json` upgrades, preservation, and failure-before-mutation behavior.
- [ ] Harden the installer and health checks for supported profiles, transactional upgrades, configuration conflicts, matcher validation, and output/timeout diagnostics.
- [x] Exercise `scripts/install-codex.sh` directly in isolated temporary Codex homes for fresh install, changed-managed-hook upgrade with inline user hooks, rerun, and dry-run.
- [x] Correct compaction maintenance delivery, progress accounting, explicit failure reporting, and synchronous I/O costs; verify a 365-line snapshot completes in six bounded repair batches.
- [x] Verify real Codex app-server compact recovery and five Stop continuation prompts in an isolated synthetic profile; record the sandbox-denied indexing result without claiming semantic success.
- [x] With explicit user approval, install the repaired runtime into the real native Codex profile, run `--check`, and verify preservation before the user's next desktop dogfood run.
- [x] Capture the user-requested simplification direction and distinguish semantic recall from event accounting.
- [x] Specify the minimal ledger/index/state contract and compatibility path; justify every retained artifact and hook responsibility before implementation.
- [x] Replace routine generation of duplicate event records, automatic context packets, archival indexes, and the JSON compatibility mirror with the minimal contract; remove their mandatory validation dependencies without deleting existing session data.
- [x] Repair tool-result semantic indexing with real-shaped `tool_response` fixtures and actual content-level retrieval evidence, not just a field rename or structural pass.
- [x] Prove bounded inspection of large payloads and post-compaction retrieval through model-authored topics with the original corpus unavailable.
- [x] Preserve legacy event-file breadcrumbs and prevent repeated identical Stop payloads from losing maintenance-attempt progress; verify failing regressions before repair.
- [x] Capture same-thread post-compaction provenance: no-tools `UNKNOWN`, completed root/subindex reads before a selected ledger-range call, returned source value, and cited answer. Persist the ordered trace beside this plan and document it in the active memory.
- [x] Falsify locale-dependent capture with identical raw UTF-8 input: old decoding fails on a surrogate, strict UTF-8 preserves the complete payload. Add raw-byte and actual installed-launcher regressions.
- [x] Add long-Unicode assistant capture acceptance gates that reject missing/truncated/mojibake replies, prompt copies, short replies, and ambiguous source keys.
- [x] Prove version-8 behavior in a fresh disposable Codex session without manually editing the graph or supplying maintenance instructions in the post-compaction user turn; preserve the complete synthetic report.
- [x] Fix native sandbox access to installed Windows runtime files through inherited staging ACLs and render an executable, shell-quoted absolute reader command in version-9 roots; verify focused regressions and approved upgrades without changing old evidence.
- [x] Retain an installed-profile native run's original index, ledger, manifest and provider transcript; verify actual compaction, complete Unicode capture, source-led independent retrieval and unchanged configuration. Preserve its original checker false negative separately from corrected verification.
- [x] Resolve reader interpreter and stable launcher paths from installation-time manifest values, render only the session-specific path into new indexes, migrate template version 9 without touching retained sessions, and verify version 1.0.2 in an empty-PATH installed-runtime read.
- [x] Fit compaction recovery instructions to the configured SessionStart context limit, clarify distinct topic routes without copyable fake source ranges, tighten the dogfood checker to require links to the actual tool-result line, and pass a fresh retained native compaction/retrieval run.
- [x] Repeat installed native topic-quality dogfood; runs 8 and 9 passed consecutively on version 1.0.4/template 12, with original artifacts retained. Keep broader platform, desktop and automatic-compaction limits explicit.
- [x] Capture the desktop-driven pivot and distinguish successful frozen event accounting from useful, nonintrusive recall.
- [x] Reconcile the epic/architecture and runtime/template/validator contracts with selective topical navigation and searchable retained detail; define measurable root-size, latency and search/read budgets before implementation.
- [x] Replace coverage-driven blocking maintenance with nonblocking recovery and lightweight model-owned topical updates; retain explicit capture/link/read failures.
- [x] Provide bounded source search for unindexed details without adding a duplicate payload store; preserve exact source provenance and existing readers/links.
- [x] Prove nonblocking behavior and constrained indexed/unindexed retrieval in large-history Luna CLI replay. Two runs passed, but source-directed three-topic curation did not establish independent session-wide organization.
- [x] Prototype deterministic Markdown serialization with exact payload-value round trips, stable within-event addresses, bounded reads/search and safe append/restart behavior, without a second authoritative payload copy. Small storage gates passed; not production-scale acceptance.
- [x] Run bounded proactive-topic dogfood across interleaved results, revisited subjects and a revised decision without source-line hints, prescribed labels/counts or a final curation request. Both attempts failed quality/provenance; preserve evidence rather than treating execution as acceptance.
- [x] Resolve the observed source-handle and relative-link errors in a bounded source-handle trial; the third small pair passed. Keep broader graph-quality acceptance separate.
- [x] Run a recoverability-first frozen-graph trial with independent index-only controls and fresh Luna contexts; retain the mixed result rather than treating correct answers as proof of every source-read/cost gate.
- [x] Promote the tested serializer into the single production adapter and canonical version-14 template; explicitly deprecate JSON/JSONL sessions without migration or deletion.
- [x] Verify managed-launcher Markdown/UTF-8 capture, stable empty-PATH readers, installer upgrade/rerun, and isolated native packaged-runtime topic/compaction/retrieval behavior.
- [x] Verify real user-run Desktop manual compaction and a natural source-backed recall question without answer/source hints or manual graph repair; preserve the empty-graph and raw-search budget limitations.
- [ ] Verify content-based post-compaction retrieval across multiple events and a deliberately unindexed detail without chapter/paragraph identifiers; retain original Markdown, index and native traces for human inspection.
- [ ] Establish full post-compaction internal-context absence for the selected fact. Inspectable text and the behavioral control support lack of available recall, but native opaque compaction state is not inspectable; this stronger condition remains unverified.
- [ ] Extend direct installer coverage to missing prerequisites, broader conflicts, and injected rollback/failure scenarios.
- [ ] Dogfood the actual installer and upgrade in a fresh ChatGPT Codex desktop session from an unrelated project; verify the reported inline-hook scenario, configuration and session-record preservation, `--check`, trust review, and compaction recovery.
- [ ] Run focused and repository validation, record evidence, and complete the review before requesting closure.

## Objective

Close the portability, transactional-safety, and configuration-validation gaps identified during completion of the Codex Total Recall installer, including a supported and verified path for running the installer when Codex user configuration already defines inline hooks.

The immediate corrective objective is to preserve complete received details in one authoritative ledger and make them discoverable through selective model-authored topical navigation plus bounded source search. Recall must not commandeer ordinary conversation to complete an event inventory. Reduce generated duplication and hook responsibilities rather than adding more representations of history. Installer hardening remains in scope, but passing installation or structural checks is not sufficient to satisfy Total Recall.

## Specifications

### Problem Spec

The managed installer is implemented and verified on a native Windows profile, but macOS/Linux/WSL behavior, shell mutation-boundary failure recovery, and several health-check cases remain unverified. Codex hook trust is a separate user review decision, and the installer must not claim effective activation from configuration-file presence alone. Codex documentation confirms same-layer hook sources are merged but recommends using one representation; the installer now preserves the inline representation, migrates only recognized installer-managed hooks into a marked inline block, and rejects unrecognized managed state before mutation.

Earlier desktop dogfood showed that generated event copies and context packets increased I/O, recovery paths, and validation work without ensuring meaningful recall. Tool output is valid session input; version 6 preserved it but omitted the real `tool_response` field from previews. Version 7 removes routine duplication, exposes bounded payload reading, and requests content-level topics. Broad execution links can still pass structural coverage; independent semantic retrieval remains a separate acceptance test.

### Feature Specs

- Define and verify supported native Windows, macOS, Linux, and WSL path and permission profiles; document profiles that cannot be verified or supported.
- Exercise full upgrades and injected failures at installer mutation boundaries, proving restoration or explicit recoverability of installer-owned state and preservation of user session records.
- Validate supported legacy settings, unsupported permission profiles, duplicate user/project/inline hook sources, changed or untrusted hook definitions where observable, and invalid event matchers.
- Measure synchronous timeout and model-visible output budgets and document the enforced limits and diagnostics.
- Ensure health checks report only trust and effective-configuration facts exposed through supported Codex interfaces.
- Make the `scripts/install-codex.sh` entry point an explicit test and dogfood surface, not merely an untested wrapper around helper tests.
- Preserve unrelated Codex configuration and user-authored inline hooks. Select the conflict/migration behavior only after verifying Codex's supported configuration semantics; fail before mutation with actionable diagnostics where coexistence or migration is unsupported.

### Interface / Contract Specs

- Keep automated installer tests isolated in temporary Codex homes and configuration directories; they must never touch the real user configuration.
- Exercise the installer entry point for fresh install, upgrade, same-version rerun, dry-run, missing prerequisites, supported and unsupported configuration, and injected rollback/failure conditions.
- A conflict discovered during preflight must not leave partial installer mutations. Existing user session records must remain byte-identical across install, upgrade, rollback, and migration.
- Installer health checks must distinguish managed configuration presence from Codex hook trust and effective configuration when the latter cannot be observed through a supported interface.
- Real dogfood must use ChatGPT Codex desktop from an unrelated project and record the Codex surface/version, installer invocation and result, `--check`, relevant configuration preservation, hook review, session graph validation, and post-compaction recovery evidence.

### Behavioral Specs

- Treat native Windows desktop/CLI and WSL as distinct profiles unless the user explicitly configures them to share state.
- Do not silently convert legacy sandbox settings to permission profiles or bypass Codex's hook trust review.
- Do not delete, overwrite, or migrate user-authored inline hooks merely to make `hooks.json` installation succeed.
- Do not claim successful activation solely because managed files or hook definitions are present.
- Where a platform or Codex configuration state cannot be supported safely, fail before mutation and explain the supported recovery path.

### Minimal Recall Contract

| Surface | Required responsibility |
|---|---|
| `ledger.md` | The single authoritative deterministic capture of complete received payload values, with checksummed frames and stable event/text-part anchors. Preserve append history; distinguish received text from provider-truncated or unobserved text. |
| `INDEX.md` and purposeful topical subindexes | Model-authored discovery by content and meaning. Link directly to retained source ranges; introduce subindexes only when they improve topical navigation or context safety. Several subjects may point to the same tool-result event. |
| Minimal operational state | Only justified session identity and explicit capture/navigation status. Reassess frozen maintenance and retry state when removing the coverage gate; do not retain it without a purpose or introduce another payload store or parallel semantic graph. |
| Optional diagnostics | Concise execution timing, errors, and maintenance outcomes. Do not duplicate raw payloads or count diagnostic links as semantic coverage. |

- Hooks are thin capture, nonblocking recovery delivery, and diagnostic glue. They do not infer topics, enforce all-event semantic coverage, or manufacture per-event Markdown, automatic neighbor packets, or generic discovery hierarchies.
- Bound model-visible bytes/tokens as well as event counts. Define and test concrete per-pass and per-read limits before implementation; a single large tool result must not force a full-ledger or full-payload context dump. Short previews select source reads; they are not proof that the remaining content was inspected.
- Treat tool results as evidence, not automatically trusted instructions. Index useful subjects in the output as well as the operation that produced it. Repeated material may share topical routes without dropping authoritative detail.
- Preserve capture continuity across compaction, stable source locations, and explicit failures. A selective or stale index must not be presented as complete. Deterministic checks prove ledger integrity and valid declared links; semantic acceptance requires retrieval evidence, not an event-range coverage count.
- Expose bounded ledger search for details without a topical route. A complete short returned excerpt may establish evidence; read further source context when needed. Search is not a second archive or a guarantee of arbitrary semantic recall.
- New-format sessions must not require `events/`, automatic `context-packets/`, generated archival indexes, `ledger.json` or a JSONL mirror. Old JSON/JSONL sessions are unsupported and explicitly require a fresh session; there is no compatibility/migration path. Do not delete, rewrite or relocate historical artifacts.

## Applicable Guidance

- [Manage Planning](../../skills/manage-planning/SKILL.md) — keep active evidence and child/parent status synchronized; activation does not imply closure.
- [Project Layer instructions](../../instructions/project.instructions.md) — follow this repository's project-specific architecture and boundaries.
- [Project instruction index](../../instructions/INDEX.md) — route to the project-specific instructions governing this work.
- [Planning router](../INDEX.md) — authoritative project planning guidance and lifecycle.
- [Branch workflow](../../instructions/branch-workflow.md) — use a plan-specific branch and do not publish until ready.
- [Installer completion packet](../closed/PL-20261027-total-recall-codex-installer/PL-20261027-total-recall-codex-installer.sdd.md) — preserve verified Windows behavior and transferred limitations.
- [Installer Hardening backlog source](../backlog/PL-20261027-total-recall/PL-20261027-total-recall-codex-installer-hardening.md) — authoritative source scope and test approach.

## Test Plan

### Next Experiment: Markdown Sources and Proactive Topics

Use focused test-first stages: write and run the failing check, make the smallest candidate change, rerun it, and broaden only after it passes. The two hypotheses have independent outcomes; do not change storage and prompting together and attribute every improvement to one.

#### Recoverability-First Frozen-Graph Trial

This is the next execution priority and supersedes any implication below that a
graph must beat search-only timing or provide one route per fact.

1. Freeze the existing unmodified `markdown-proactive-3` post-compaction ledger
   and model-owned graph by hashes before selecting questions. It already has
   incremental updates, revisited evidence and a revision; do not regenerate or
   hand-curate it to satisfy new questions.
2. Select two retained details whose answers are absent from all navigation:
   one reachable through a relevant topic and one genuinely unindexed detail.
   Also ask a revision question and an unrecorded-detail question. Keep expected
   answers and evidence anchors in host-only reports, never model prompts.
3. Give each fresh Luna thread the frozen root text as its sole historical
   starting context, plus a natural question. Do not separately prescribe
   search terms, ledger anchors, commands or the retrieval sequence. Root
   instructions themselves must make discovery possible. Use an isolated
   hook-free profile and read-only sandbox; no original transcript, previous
   answers, operational input files or earlier reader sessions may be consulted.
4. First run independent index-only/no-tools controls for the two hidden
   answers. Require no command calls, no recovered answer and an explicit
   unknown. Then enable tools in different fresh threads; require the correct
   detail, completed bounded source output containing it, and an accurate
   citation to a source actually read. For the unindexed detail, require
   bounded search followed by a source read. Reject guessing or search-excerpt-
   only answers. The unrecorded question must remain unknown.
5. Fix guardrails before launch: explicit `gpt-5.6-luna`, 180 seconds and eight
   tool calls per retrieval question, no source output over 4,096 serialized
   bytes, unchanged source/navigation hashes, no ledger dump, no writes or
   coverage maintenance. Save prompts, native traces and failed reports. Reject
   missing controls or answer leakage, and stop after this bounded trial rather
   than tune questions after failures.
6. Interpret narrowly: success proves recoverability from this frozen session
   and the tested details, not universal semantic search, arbitrary context
   absence, production-scale graph quality or that extra indexing always pays
   for itself. Inspect the graph's topic/revision orientation without scoring
   per-fact coverage. Further varied-session tests follow the outcome.

**Executed outcome: core recovery demonstrated; strict trial failed.**
`markdown-frozen-recall-1` used six independent, hook-free Luna threads in an
actual read-only/network-off sandbox. Both index-only controls returned UNKNOWN
with no tool calls. The graph alone did not contain the assay-reagent rationale
or dispatch receipt identifier.

| Question | Observed behavior | Calls | Seconds |
| --- | --- | ---: | ---: |
| Why avoid light exposure? | Topic route led to an exact source read; correctly recovered that light damages the assay reagent. | 5 | 20.737 |
| Dispatch receipt reference? | Correctly found CEDAR-204 using the root's bounded search; cited its returned anchor but skipped the separate source read. | 2 | 7.770 |
| Current versus old pressure trip, and why? | Read the revision source; correctly explained 54 replacing 72 kPa and cold-seal overshoot. | 3 | 10.009 |
| Full name of the dry-run witness? | Correctly answered UNKNOWN, but used ten calls against the eight-call guardrail. | 10 | 29.661 |

The fresh prompts provided the unmodified root and natural question, not search
terms, source IDs, tool commands beyond those already in the root, original
history, expected answers or a prescribed retrieval sequence. Independent
verification confirms hidden answers absent from initial native context, exact
source-page equality, the receipt excerpt matching retained evidence and
unchanged frozen hashes. New answers were never appended to the historical
ledger. The graph is two meaningful topics with a connected revision, not an
event inventory.

This supports the user's central hypothesis: ledger retention plus discovery
instructions makes otherwise unavailable details recoverable, with topical
navigation providing a useful starting point. It does not certify dependable
search-then-read behavior, economical negative lookup, or long-session graph
balance. The strict report remains failed; no questions/gates were changed and
no repeat-to-success run was made. Reports, prompts and native transcripts are
retained as `markdown-frozen-recall-1.json`, its sibling evidence directory and
`markdown-frozen-recall-1-verification.json` in the current Copilot session files.
No live installation, historical repair, scale-up or new indexing mechanism.

**Next scoped decision:** decide whether factual answers from complete short
search excerpts are acceptable or require an explicit source-read instruction
in the navigation contract; do not silently relax the current gate. Investigate
negative-search noise: the literal query `name` matched capture metadata keys
such as `hook_event_name`, contributing irrelevant discovery results. Neither
finding calls for per-fact indexing or a coverage gate.

1. **Available inputs and safety:** use explicit `gpt-5.6-luna` through the verified Codex CLI app-server, the existing retained narrative workload and original negative/positive runs as immutable references. Reuse the current client, provenance checks and isolated-profile controls. Add assistant-owned synthetic structured payloads and cross-turn revisions where the repetitive narrative lacks them. Preserve new successes and failures; no live-profile change or repair of supplied sessions.
2. **Storage hypothesis, small spike first:** define a deterministic Markdown event envelope and source-addressing contract. Test complete parsed-payload round trips for nested objects/arrays, strings/numbers/booleans/null, long multiline results, Unicode, trailing/blank lines, mixed newline values, control characters, embedded headings/fences/HTML and delimiter-like text. Check literal content is not mistaken for an event boundary. Do not add a complete JSONL mirror to make reconstruction work.
3. **Stable, precise source navigation:** address both an event and a relevant part of a large text field without relying on a single giant line or mutable document offsets. Verify actual Markdown rendering/link behavior and that appending later events leaves earlier addresses unchanged. Bounded reader output must match the selected original text exactly; searching unindexed content must return usable source locations. Require human-inspectable source excerpts, not just links that parse successfully.
4. **Append and compatibility gate:** test concurrent writers, duplicate delivery, interrupted/truncated appends, restart and explicit corruption reporting. Preserve readable earlier records without silently declaring a partial tail complete. Existing JSONL sessions and links remain usable and byte-preserved; no automatic conversion or deletion. Reconcile the architecture, epic, reader/validator/template and installer contracts before any production format switch. Stop and reconsider YAML if Markdown cannot meet fidelity, readability and addressing requirements simply.
5. **Topic hypothesis, representative native task:** present several ordinary turns with interleaved subjects, at least two source events revisiting one subject, unrelated material, and a later decision revising earlier evidence. Encourage useful incremental topic maintenance through the normal guidance, but do not name the topics, supply source lines, prescribe a route count, or issue a final "index this" task. Trace evidence must show useful topic work before compaction, while the relevant context was available.
6. **Topic evolution checks:** require an independently selected subject to connect relevant evidence from different turns, with meaningful bullet descriptions or a purposeful subindex. Check the later revision and its relationship to earlier evidence. Multiple topics may legitimately cite one event; different line numbers alone do not establish quality. Reject execution/probe inventories, irrelevant links and an index that only appears after an explicit curation demand.
7. **Recall and overhead checks:** after real compaction, ask natural content-based questions without ledger lines, chapter/paragraph IDs, answer-bearing markers or copied answers. Require correct facts, revision/rationale where applicable, citations and completed index-before-source reads. Separately exercise an unindexed fact through search and exact source reads. Preserve a no-tools control or independent retrieval context and disclose native opaque-state limits. Retain zero coverage blocks and the existing declared response/read budgets; measure incremental indexing time/calls separately so work is not merely shifted into earlier turns.
8. **Progression and human review:** compare serialized representative payloads before paying for large native runs; run one bounded Luna experiment next, diagnose any failed hypothesis, and repeat only after it passes. Retain the actual Markdown ledger, topical index/subindexes, original transcripts and reports for the user to inspect. Good round-trip results alone do not certify usable navigation, and attractive Markdown alone does not certify recall.

#### Immediate Falsification Trial

1. **Small deterministic format spike, no model usage:** render a handful of representative payloads into a fresh assistant-owned Markdown ledger, including a large received narrative result and hostile-to-formatting synthetic text. Prove exact parsed-payload reconstruction, human-readable multiline content, precise event/within-event links, and unchanged earlier addresses after appends. Interrupt one append and verify explicit failure rather than silent source loss. Stop if any of these fail; do not build a parallel JSONL payload copy to rescue the format.
2. **Six-turn Luna workflow, not a corpus benchmark:** interleave three subjects, revisit one with additional evidence, revise an earlier decision, and finish with an ordinary acknowledgement. Put general proactive-topic guidance in the candidate's normal instructions. Do not prescribe labels, route counts, source lines or an indexing task in the user turns. Snapshot the model-authored index after each completed turn without editing it; establish when useful updates actually occurred and whether sources already existed.
3. **Evaluate quality before scaling:** require relevant routes connecting the revisited subject's distinct source events, an accurate revision relationship, no invented source references and no execution inventory. After compaction, use content-based questions requiring the earlier evidence and later revision, not source identifiers. Test source-backed retrieval of an unindexed detail only if one is genuinely absent from the model's routes; do not delete links or force omission to manufacture that case.
4. **Compare foreground cost fairly:** run the same small workload with the existing selective guidance and with proactive guidance, using the same Luna build and candidate storage. Record each turn's latency, index-related tool calls, source-read volume and maintenance token usage where exposed. Retain the zero-blocking, bounded-read and 60-second ordinary-follow-up gates. Set an incremental-maintenance overhead limit before launching the paired run; do not choose it afterward to make a result pass. Do not credit faster compaction recovery if the cost merely moved into every earlier turn.
5. **Explicit stop/go:** failed fidelity or dangling references stop the storage experiment; absent spontaneous topic evolution or incorrect revision recall fails the topic hypothesis; exceeded overhead limits fail the speed hypothesis. Diagnose the failed gate before enlarging the fixture. Only a passing small trial proceeds to repetition and the retained 109-result workload, with readable source/index artifacts for user review.

**Predeclared small-trial budgets:** six identical native workflow turns per mode,
explicit `gpt-5.6-luna`, and the same isolated Markdown runtime and input values.
No coverage-blocked Stops; ordinary acknowledgements and post-compaction replies
at most 60 seconds; other individual turns at most 180 seconds; root at most
8,192 bytes; at most 18 index-related command/file-change calls across the six
turns; at most eight commands per fresh-context recall question. The proactive
mode may add at most 60 seconds to the selective mode's total six-turn foreground
time. Count discovery/read/search/edit/validation activity used for the index,
not only writes. Preserve per-turn snapshots outside the model workspace.
Topic-quality gates apply to proactive mode; the selective control need not
produce spontaneous topics to be a valid timing control. Record unavailable
token breakdowns rather than infer them. These are experimental acceptance
thresholds, not universal latency promises.

**Storage spike status:** an isolated Markdown serializer passed nine focused
storage tests. The retained
`markdown-format-spike-1` artifact reconstructs a received narrative result and
hostile formatting exactly, without a JSONL mirror; a CommonMark renderer
verified all 11 generated anchors and escaped embedded fake HTML. Metadata is
collapsed for human inspection. This is prototype evidence, not a production
format migration or live upgrade.

**First native pair (retained, failed):** `markdown-selective-1` and
`markdown-proactive-1` used identical storage and synthetic inputs with Luna.
The selective workflow took 28.788 seconds; proactive took 31.021 seconds.
Neither produced topics. Proactive instructions are present in 17 native
developer-context messages, so missing hook delivery is not the explanation.
Selective recall was correct but two questions exceeded the eight-command
budget. Proactive also answered the receipt question from a search excerpt
without a source read, and one PreToolUse hook timed out at 10,006 ms.
No candidate success is claimed.

**One bounded corrective pair:** test explicit navigation-write permission and
a one-time root-contract read; the first harness's blanket prohibition on
changing "retained evidence" may have obscured the writable index boundary.
Keep workload and budgets unchanged. Clarify that recall must read the source
after search, retain full hook failure details, and stop the proactive retry
after six turns if precompaction quality/cost gates fail. Do not scale or
retroactively alter the first pair.

**Corrective outcome (stopped):** `markdown-proactive-2` made topical updates on
turns 1-5, with six counted maintenance calls and 78.139 seconds total workflow
time; the final acknowledgement took 2.660 seconds. Its declared links failed
on every snapshot: the model wrote `../ledger.md` although the ledger is beside
the root. More importantly, it linked pump facts to captured user requests
rather than the initial and revised tool-result events containing the facts.
The host did not repair the graph. The early-stop gate prevented compaction and
retrieval work; no second selective control or larger workload was run.
This is a failed provenance/quality experiment, not evidence of accepted
proactive recall. Without the matching second control, added foreground cost
is not certified. The first pair's capture timeout remains an unresolved
native observation, not explained away by healthy hooks in the retry.

**Next decision (now authorized for a bounded trial):** test whether exposing the actual newly
captured tool-result handles, rather than only the current user-request handle,
lets the model cite available evidence correctly without extra discovery calls.
Keep source-pointer delivery deterministic and topic selection model-owned.
Do not substitute stronger coverage pressure, manual link repair, or a relaxed
quality gate. Nine deterministic storage tests and four evidence-accounting
tests now pass; production still uses JSONL and no live profile was changed.

**Source-handle trial:** after the user's approval, add deterministic
PostToolUse context naming the just-captured event and at most four result-text
part handles, with explicit continuation when more exist. Deliver no payload
copy, inferred topics or update mandate. State that root links are relative to
the current INDEX.md and must cite evidence rather than its initiating request.
Configure the isolated PostToolUse hook for the existing 1,200-byte context
limit. First reproduce missing delivery in a regression, then run proactive
six-turn dogfood; only if source-quality gates pass run its matching selective
control and compaction/retrieval evaluation. Keep the existing workload,
Luna model, 18-call/8-KiB/60-second overhead budgets and immutable old evidence.

**Source-handle outcome:** `markdown-proactive-3` passed the small gates:
valid links, model-owned topic evolution, initial/revised evidence connected,
six maintenance calls, 3,218-byte root, 74.705-second workflow and 2.840-second
post-compaction reply. Four fresh-context recall questions passed with
7/5/4/3 commands; the receipt was genuinely unindexed and recovered through
search followed by a source read. Matching `markdown-selective-3` passed
retrieval in 3/4/7/3 commands, with a 35.597-second workflow and no topics.
The proactive mode added 39.108 seconds, within the predeclared 60-second
budget, but did not consistently reduce retrieval calls. Actual native
developer context confirms tool-result handles were delivered in both modes.
Artifact hashes, captured workflow replies, Luna and workspace-write/network-off
policies were independently verified. One initial topic target points to the
first part of a mixed tool result; the next_part chain reaches the fact and the
retriever followed it. This is a useful broad route, not exact fact placement.
Only one passing pair exists; no scale/repeatability or live-install claim.

**User clarification after this trial:** keep the contract simple: every
received detail remains in the searchable ledger without needing an index
entry. The lightweight index is a model-owned graph of useful topics,
facts, decisions and relationships, updated opportunistically. Primary
behavioral proof should freeze an unmodified model-authored index/ledger,
provide the index as the starting point to a fresh session with no original
history, and ask natural questions requiring evidence it never encountered.
Select questions after freezing navigation; allow broad routes and bounded
search, and score accurate evidence-backed answers and cost rather than
per-fact indexing. Real compaction-hook delivery remains a separate integration
check. Do not expand tests or add compulsory source accounting in response to
this simplification.

### Previous Corrective Slice: Nonblocking Topical Recall

These checks establish the retained nonblocking baseline. Their source-directed curation and identifier-based questions are not sufficient for the next experiment's independent topical-organization claim.

Use focused test-first slices: write the failing check, confirm the failure, implement the smallest change, rerun it, then broaden validation. Existing adapter, installer and dogfood tests are the starting surfaces; do not add another indexing framework.

1. **Contract and budgets first:** Reconcile the epic and architecture, then specify the hook/template/recovery/validator/search interfaces and compatibility behavior. The comparative driver fixes experimental gates before each run: no coverage blocks, ordinary post-compaction reply within 60 seconds, root at most 8,192 bytes and 20 links, at most eight tool commands per retrieval question, and exact answers/citations with completed index-before-source ordering. Source read/search output is at most 4,096 serialized bytes; search scans at most 256 events per page with explicit continuation. These are falsifiable experiment gates, not universal model-latency guarantees.
2. **No coverage-driven interruption:** In `scripts/test-codex-total-recall.py`, reproduce a large captured history with no topical coverage and a normal post-compaction completion. Fail if Stop blocks solely for missing breadcrumbs, launches compulsory indexing, or prevents the ordinary response. Retain tests for explicit capture, corruption, link and reader errors.
3. **Retention and source discovery:** Test byte-preserved received payloads, stable identities, existing links and exact bounded reads. Add source-search checks for matches beyond previews, Unicode, pagination, no match, and actionable failures. Search must not silently truncate results or imply semantic completeness.
4. **Realistic semantic dogfood:** Extend `scripts/dogfood-codex-total-recall.py` and its checker tests with hundreds of repetitive events and distinct facts near the beginning, middle and end of large outputs. After genuine compaction, use an ordinary short user reply rather than a maintenance prompt. Reject per-event/probe inventories and any run exceeding the agreed root-size/latency/tool-call budgets.
5. **Two independent retrieval paths:** With the synthetic original corpus unavailable, prove (a) index -> selected source -> cited answer for an indexed fact and (b) index miss -> bounded ledger search -> exact source -> cited answer for an intentionally unindexed fact. Record completed reads before subsequent calls and answers; avoid answer leakage in navigation/prompts. A no-match result or partial preview is not successful recall.
6. **Installed evidence and compatibility:** Retain original new-session artifacts, provider traces, failed runs, timings, source-read sizes and maintenance overhead. Never repair supplied evidence. Verify upgrade preservation in isolated homes before any separately authorized native installation; keep app-server/manual-compaction evidence distinct from desktop/automatic-threshold acceptance.

### Historical Unicode Failure: Evidence-Only Diagnosis and Isolated Proof

The following earlier test slices document prior work. Their mandatory frozen-coverage and Stop-retry expectations are superseded by the nonblocking tests above; retention, provenance and compatibility evidence remain relevant.

1. Preserve supplied sessions and attachments as read-only evidence. Do not repair their indexes, append recovered messages, restore files, or use manually authored navigation as proof of hook behavior. Record prior interventions separately.
2. **Capture hypothesis:** strict raw UTF-8 decoding fixes Windows locale-dependent loss. Disqualify it if identical bytes still fail or differ from the captured payload. Run the old decoder as a negative control; use actual packaged-launcher tests, not only decoded dictionaries or ASCII-escaped JSON.
3. **Maintenance hypothesis:** after real compaction, hook-provided instructions produce usable model-owned topical links. Use an ordinary `Continue.` turn, require complete frozen-snapshot structural coverage and distinct topics pointing to both tool-result and assistant-reply sources. Never hand-edit the test graph to pass.
4. **Recall hypothesis:** index-led source retrieval recovers details unavailable to the retrieval context. Delete the synthetic tool source, check a full long Unicode assistant reply against its actual Stop payload, recover facts from both source types in a fresh thread, then run the existing same-thread no-tools/ordered-retrieval control after another compaction. Preserve native opaque-state and desktop/automatic-compaction limitations.
5. Preserve synthetic reports, including failures and actual started/completed command traces. Keep private authentication separate from the disposable model workspace and clean up both after the run. Do not touch the user's benchmark or live session/configuration.

### Historical Corrective Slice: Simplification and Content Recall

1. **Design before more patches:** Trace capture, source lookup, model maintenance, validation, recovery, and installer compatibility in the existing adapter/template/tests. Specify which artifacts disappear from routine generation and why each remaining state field or file is necessary. Record failure recovery without using redundant Markdown as a second source of truth.
2. **Failing real-shaped fixtures:** Use sanitized Codex `tool_response` strings and structured results alongside prompts and tool inputs. Seed distinct facts at the beginning, middle, and end of a result larger than one inspection batch. An execution-only breadcrumb must fail semantic acceptance even if every event line is linked.
3. **Minimal persistence and compatibility:** Verify fresh capture without the redundant files, stable source locations, retained payload bytes, restart/idempotence, interrupted append behavior, and explicit corruption errors. Test old-layout sessions and old model-authored links without destructive migration; ordinary installation must leave existing sessions unchanged.
4. **Bounded model maintenance:** Measure actual response/read sizes and hook I/O against the declared limits, not only the number of events. Verify one large result can be inspected across bounded passes, with explicit incomplete state if work remains and no moving snapshot target.
5. **Semantic acceptance:** Following genuine compaction, require the model to navigate from `INDEX.md` to retained evidence and correctly explain seeded user/tool-derived details and their implications. Make the original corpus unavailable in the isolated fixture; do not accept direct source-file search, marker-only answers, or a blanket benchmark-activity link as proof. Record the graph path and cited source ranges.
   - **User-requested provenance gate:** Capture actual started/completed events proving the index result preceded the source request, then retain the source output and answer. Check answer leakage into navigation and supplied context; use a no-tools control in the same compacted thread. Explicitly record opaque-state limitations rather than treating a plaintext scan of encrypted state as absence proof.
6. **Upgrade and desktop proof:** Exercise the actual installer with the simplified runtime in isolated homes, then perform separately authorized native desktop dogfood. Keep manual-compaction evidence distinct from automatic-threshold evidence. Synchronize the runtime/template/architecture documentation only when the selected contract is implemented and validated.

### Continuing Installer Validation

Use focused test-first slices. For each behavior, add a failing isolated test, run it to confirm the defect, implement the smallest change, rerun the focused test, then broaden validation. Use the existing Python and Bash tooling; do not add test dependencies unless an existing command demonstrates they are missing.

1. **Inline-hook conflict and preservation:** Extend `scripts/test-codex-hooks-config.py` and the isolated installer suite with fixtures containing user inline hooks in `config.toml`, existing `hooks.json`, and both representations. Prove the selected supported behavior, preservation of user-authored entries, actionable unsupported-state diagnostics, and no mutation on preflight failure.
2. **Installer entry-point coverage:** Extend `scripts/test-install-codex.sh` so it invokes `scripts/install-codex.sh` itself against temporary Codex homes for fresh installation, upgrade, rerun idempotence, dry-run, inline-hook conflict, missing prerequisites, and configuration preservation. Compare relevant files and user session records before and after each scenario.
3. **Upgrade and transaction recovery:** Add focused tests for complete version upgrades and injected failure at each installer-owned mutation boundary. Prove rollback or documented recoverability for the runtime pointer, launcher, configuration, permissions, and other installer-owned state, without rewriting session records.
4. **Platform and permission profiles:** Test path and configuration fixtures for native Windows, macOS, Linux, and WSL; separately verify effective OS permissions on profiles available to CI or dogfood. Record unavailable profiles as unverified, not passed.
5. **Health and hook contract:** Test diagnostics for legacy and unsupported permission settings, duplicate hook layers, trust/changed-hook states where observable, invalid event matchers, missing or incompatible runtime, synchronous timeout, and oversized model-visible output.
6. **Manual desktop dogfood:** Run the actual `scripts/install-codex.sh` for the relevant fresh-install and upgrade paths in the separately authorized native Codex profile, including the state that reproduced the inline-hook error. From a fresh Codex desktop session rooted in an unrelated project, verify `--check`, preservation of inline hooks and unrelated configuration, no session-record changes, required manual trust review, hook dispatch, valid declared links, and meaningful post-compaction retrieval. Verify ordinary conversation completes without event-coverage maintenance loops, and exercise both retrieval paths under the declared budgets. Do not substitute Copilot or CLI-only results for desktop evidence.
7. **Broader validation:** Run the focused installer/configuration suites, applicable platform CI checks, and `bash .adaptive-agents/scripts/check-project-layer.sh`. Run the repository health check when implementation and platform changes are complete.

## User-Facing Surface

- Surface: `scripts/install-codex.sh`, its managed runtime/configuration migration and health checks, plus session `INDEX.md` discovery and source retrieval.
- Runtime scenario: install or upgrade Total Recall for Codex when user-level configuration already contains hooks, then use Total Recall in a fresh desktop session.
- Endpoint or runtime: source and user-upgraded live Desktop runtime 1.2.0/template 14. Isolated trials use desktop-bundled Codex `0.163.0-alpha.10.2` CLI app-server with explicit `gpt-5.6-luna`, workspace-write sandbox and no network access. The later user-run Desktop milestone proves manual compaction/source lookup, not automatic-threshold or full graph-quality acceptance.

## User-Facing Validation

- Agent proof: Repeated live synthetic runs passed; the strongest proof checks three distinct tool-content topics, every source page, user-instruction retrieval, exact values and rationales, source citations, preserved ledger bytes, and absence of hook failures.
- Current evidence: `scripts/dogfood-codex-markdown.py --mode proactive --packaged-runtime` passed isolated managed-launcher capture, early topic evolution, real compaction and all four fresh-context source-backed questions. The original benchmark and live profile are untouched. JSONL live runners are retired; their shared client and historical report checks remain test helpers.
- User handoff: The stronger assistant-owned Unicode exercise passed without manual graph repair, with 42 hook completions and no hook failures. The earlier ASCII/tool-focused proof remains a separate reference. Desktop/automatic-compaction acceptance and broader installer hardening remain; no benchmark run or supplied-session repair is required.
- Stronger provenance evidence: [ordered same-thread trace and limitations](PL-20261027-total-recall-codex-installer-hardening.memory.md#ordered-recall-provenance-evidence) records root -> topical subindex -> ledger line 4 -> answer after a no-tools `UNKNOWN`. Full internal-context absence remains unverified because Codex exposes opaque compaction state.

## DRY Assessment

- Status: Required; duplication identified.
- Scope: Authoritative ledger versus generated event Markdown, automatic context packets, archival indexes, JSON compatibility mirror, and the writer/recovery/validator paths supporting them.
- Decision: Target one authoritative payload store and a model-authored topical graph. Reuse existing installer ownership helpers; do not replace redundant documents with an equally redundant state or indexing framework.
- Result: Fresh sessions retain `ledger.md`, `INDEX.md`, `manifest.json`, and a graph lock. Production and the explicit-root dogfood wrapper share one implementation. No routine event copies, packets, archival indexes or mirror are generated. Earlier 365-event timing is historical JSONL evidence, not a Markdown performance measurement.
- Intentional/deferred duplication: Existing historical artifacts remain untouched, not runtime compatibility targets. Model-authored topical explanation is permitted when it adds meaning; automatic payload replication is not the target design.
- Pivot review: source search reuses ledger integrity parsing and exact source coordinates, without another store. The retained replay driver reuses the existing app-server client, page parser and topic-link checker; profile setup remains local to its distinct retained historical-replay lifecycle. The legacy template is intentionally retained to avoid altering already-installed runtimes through shared checkout paths.

## Scope

- Verify supported platform and permission behavior, configuration conflict handling, transactional upgrades and recovery, health checks, matchers, and timeout/output budgets.
- Include direct `scripts/install-codex.sh` invocation in isolated automated tests and real Codex desktop dogfood.
- Preserve unrelated Codex configuration and user-generated session records.
- Include the user-requested ledger-first simplification and tool-content recall repair as the immediate corrective slice of this active work.
- Do not automate hook trust approval, add undocumented hook fields, convert unsupported permission profiles, delete historical session artifacts, or expand into unrelated cross-session memory or additional harness implementations.

## Acceptance Criteria

- [x] The minimal artifact/state contract is documented, and fresh sessions operate without mandatory event copies, automatic context packets, archival indexes, or a JSON ledger mirror.
- [x] Existing ledger bytes, session identity, valid model-authored source links, and installer ownership boundaries survive the compatibility/upgrade path without automatic historical cleanup.
- [x] Real-shaped tool-result fixtures preserve and expose content from `tool_response`; bounded inspection reaches facts beyond the initial preview within declared byte limits.
- [x] Model-authored topical routes support correct post-compaction retrieval of user and tool-derived details with the original corpus unavailable. Execution-only labels or event-range coverage alone do not satisfy this criterion.
- [ ] Capture, validation, recovery, and diagnostics remain thin and measured; failures are explicit and complete received payloads remain retained independently of topical coverage.
- [ ] Supported native Windows, macOS, Linux, and WSL profiles and their path/permission behavior are explicit; unavailable or unsupported profiles are accurately identified.
- [x] The inline `config.toml` hook case that previously blocked installation has a documented, source-verified migration outcome that preserves user-authored hooks and rejects unrecognized state before mutation.
- [ ] Automated isolated tests invoke `scripts/install-codex.sh` for fresh install, upgrade, rerun, dry-run, conflict, and rollback/failure scenarios.
- [ ] Full upgrade and mutation-boundary failure tests prove installer-owned state is restored or recoverable and user session records are preserved.
- [ ] Health checks and focused tests cover supported legacy settings, unsupported permission profiles, duplicate hook sources, observable trust state, invalid matchers, and timeout/output budgets without claiming unsupported Codex observability.
- [ ] Manual dogfood runs the actual installer in the native Codex desktop profile from an unrelated project, including the reproduced inline-hook setup and an upgrade path; `--check` passes and user configuration/session records are preserved.
- [x] Missing topical breadcrumbs never cause coverage-driven Stop blocking or compulsory exhaustive post-compaction indexing. The Luna CLI replay's normal short user turn completes within the declared experimental budget; desktop acceptance remains separate.
- [x] The constrained Luna candidate root stays within the declared size budget and avoids a per-event inventory; this is not evidence of independently selected session-wide topics.
- [x] A deterministic Markdown candidate preserves complete payload values and stable event/within-event addresses, remains readable to a human, and survives append/restart tests without a second authoritative ledger.
- [x] Normal small-fixture task progression produces useful model-selected topics before compaction; related evidence across turns and a revised decision have meaningful connected routes, without prescribed topics/source lines or a final indexing request. Long-session acceptance remains separate.
- [x] Natural content-based questions retrieve correct multi-event evidence and an unindexed detail after compaction without identifiers or answer leakage; source fidelity and incremental maintenance overhead are measured in the retained small source-handle pair and frozen-graph trial, not desktop scale.
- [x] An intentionally unindexed fact is recovered through bounded ledger search and exact source reads with correct citations and no access to the original corpus; an indexed fact independently passes index-led retrieval.
- [ ] A fresh native desktop-scale run with hundreds of repetitive events meets retention, topicality, retrieval and overhead criteria. Small app-server fixtures and structural coverage alone cannot satisfy this criterion.
- [ ] Desktop dogfood records required hook review and proves hook dispatch, valid session graph, and meaningful post-compaction retrieval without claiming automatic compaction-threshold coverage unless observed.
- [ ] Focused tests, applicable CI checks, Project Layer validation, and required quality review pass; remaining platform limitations and deferred work are recorded.

## Decisions

- The user deprecated JSONL because nothing is shipped. Markdown is the only supported source format; do not implement migration or dual readers/writers. Preserve nonblocking behavior and all earlier evidence. A topic may collect several meaningful source bullets before it needs a subindex; the hook must not manufacture semantic categories.
- Graphify is deferred by user decision. Use the existing Luna CLI harness and a minimal deterministic Markdown candidate; no external graph service, parser-driven storage redesign or new indexing framework belongs in this experiment.
- Closed children remain immutable. This active plan retains installer hardening and now includes the user's corrective simplification/content-recall direction; do not rewrite closed evidence to suggest these defects were already solved.
- Preserve user-authored inline hooks and Codex approval behavior. The verified migration changes only the installer-managed hook block and removes `hooks.json` only when its contents match the managed ownership contract.
- The actual installer script must be exercised in both temporary fixtures and user-approved desktop dogfood; helper-only tests are insufficient.
- Codex hook trust is an explicit user decision; no undocumented setting or trust bypass is in scope.
- Keep user session records out of installer mutation and rollback paths.
- Planned pivot: replace compulsory compact-recovery repair and coverage-driven Stop retries with nonblocking recovery, selective model-owned topics and on-demand source search. Do not launch a separate model session from a hook or require a complete ledger read.
- Historical protocol finding remains valid: Codex's `decision: "block"` / `reason` requests continuation, while `continue: false` stops it. The pivot removes the coverage-blocking policy, not the meaning of those fields.
- The installed five-stalled-attempt policy is superseded as a design target: productive batches can still commandeer a turn. Do not address this mismatch merely by increasing batch sizes, timeouts or retry limits.
- Remove routine derived history writes rather than optimizing a duplicate document system. Keep current-format model-owned roots unchanged during capture; persist maintenance outcomes in appended ledger diagnostics. Keep the 60-second SessionStart/Stop deadlines and other hook deadlines unchanged.
- Bound serialized source pages to 4,096 bytes and maintenance-feedback UTF-8 text to 8,192 bytes. Hooks orchestrate the current model; the independent thread exists only in the explicit dogfood test.
- Preserve historical artifacts and source identities without making their formats supported. Incomplete Markdown appends fail visibly. Keep old shared templates separate from the version-14 contract until the user upgrades; never repair evidence to turn a failed trial into a pass.

## Verification

- Markdown-only promotion: nine foundation tests, ten storage tests, eleven managed-runtime tests, ten hook-config tests, six driver-accounting tests, one retired-recovery no-mutation test, sixteen historical provenance tests and five historical pivot tests pass. Direct Git Bash installer suite passes 21 checks, including inline upgrade, rerun, dry-run, configuration/session preservation and `--check`.
- Packaged native trial `markdown-packaged-1`: runtime 1.2.0/template 14, Luna, native workspace-write/network-off policy. Six task turns total 96.326 seconds, eight discovery/maintenance calls, 5,305-byte root; postcompact reply 2.848 seconds. All 17 declared checks passed; four source-backed recalls used 8/4/5/4 calls. All 94 hook completions succeeded without Stop blocking. This run's receipt was indexed; deliberately unindexed recovery remains established by the earlier source-handle pair/frozen trial, not claimed for this run.
- New native artifacts remain under the user's private dogfood directory; report, original driver and per-turn snapshots are retained in current Copilot session files as `markdown-packaged-1`. No live installation or supplied-session mutation occurred. Older results below remain historical, not current Markdown or Desktop acceptance.
- Independent packaged-proof verification passed: installed manifest/adapter hashes match source, all retained artifact hashes are unchanged, 12 actual native contexts confirm Luna/workspace-write/network-off, seven returned source pages and 32 search excerpts match the authoritative reader, and all six workflow replies match captured Stop payloads exactly. Report hash is `9b90bc7ec49bc732dc4b79451483ce7a9a193b59f6ea0f493330411409c38ecf`; verification is retained as `markdown-packaged-1-verification.json`.
- Final repository health after promotion: **262 passed, zero failures**, with the pre-existing unrelated Claude Code entrypoint warning. Focused Python syntax and `git diff --check` pass. The work unit stays active for user-run fresh Desktop dogfood and the broader platform/rollback/scale acceptance still unchecked below.
- 2026-11-02 read-only desktop diagnosis: structural coverage through line 447 passed, but the normal follow-up required about 6m38s, 17 Stop evaluations and a 43,541-byte root. This remains negative acceptance evidence for the old maintenance design; see [desktop pivot evidence](PL-20261027-total-recall-codex-installer-hardening.memory.md#desktop-coverage-pivot-2026-11-02).
- Luna CLI replay uses 109 received narrative payloads (880,714 UTF-8 bytes) and 436 generation/probe events. The old runtime was stopped after at least 409 seconds, eight coverage-blocked Stops and 227 tool starts, still missing 116 frozen lines. The first corrected candidate completed the ordinary reply in 3.861 seconds, with zero blocks, a 3,681-byte three-topic root, and exact indexed/unindexed retrieval in four/six commands. Ordered source evidence, matching narrative payloads and runtime hashes were independently checked. See the [retained proof and limitations](PL-20261027-total-recall-codex-installer-hardening.memory.md#luna-cli-pivot-proof); the stopped baseline is not a completed timing or recall result.
- Repeat candidate: 2.995 seconds, zero blocks, 3,579-byte three-topic root; all ten gates passed again. Both original reports and artifact hashes are intact. The combined comparison verifies unchanged source evidence and identical replay payloads. Full repository health passed 262 checks with zero failures and one pre-existing Claude Code configuration warning; the active work unit remains open for desktop/automatic-compaction and broader installer work.
- Earlier verification below is historical evidence for the versions and fixtures named, not proof of the new nonblocking contract.
- `python scripts/test-codex-hooks-config.py` — 10 tests passed, including changed managed settings, inline migration, malformed markers, and unrecognized-block preservation.
- Git Bash `scripts/test-install-codex.sh` — 21 checks passed, including direct installer upgrade from changed managed `hooks.json` to inline hooks, user hook/session preservation, dry-run, and `--check`.
- `python scripts/test-codex-total-recall.py` — 33 ledger-first tests passed. A 365-line snapshot completes across more than five process-level bounded repair batches with the original ledger prefix preserved. Coverage includes concurrent subprocess capture, legacy source links, explicit migration/corruption errors, unchanged current-format roots, Unicode pagination, identical Stop retries, and subsequent snapshots.
- `python scripts/test-codex-total-recall-installer.py` — 7 passed.
- Repeated live Codex `0.163.0-alpha.10.2` app-server runs using the default `gpt-6.1-sol` passed actual manual compaction, model-authored calibration/release/nesting topics, and independent-thread retrieval with the seed source deleted. The final run recovered randomized values, their rationales, and original user instructions; it read all three tool-source pages (4,096 / 4,096 / 3,905 serialized bytes) plus the 935-byte user-source page. All 15 retrieval assertions and three topic assertions passed; 34 hook completions had no failures.
- Final observed hook maximum: 6,390 ms; earlier successful runs peaked at 393-428 ms. These are observations, not a universal latency guarantee. A separate 366-event synthetic capture run took 10.546 seconds total, with three initialization atomic writes and zero additional atomic writes for PostCompact. This is not a controlled comparison with the earlier real-session timing.
- Exact installed version-6 source replayed successfully against the current shared template in a disposable store. Upgrading that synthetic session to version 7 preserved the ledger prefix, all historical files, and model-authored legacy event-file links. No live session or profile was changed.
- The earlier sandbox-denied proof is superseded for this test surface: a normal inherited-ACL workspace permits model reads/writes while the private authentication directory remains isolated. No sandbox or approval bypass was used.
- `python -m py_compile scripts\codex_hooks_config.py scripts\test-codex-hooks-config.py` — passed.
- `bash .adaptive-agents/scripts/check-project-layer.sh` — 0 failures.
- Final `bash scripts/check-adaptive-agents.sh` — 262 passed, 0 failures, one unrelated Claude Code configuration warning. The checker now recognizes only the known unrendered Total Recall authority placeholder; adapter tests verify its rendered canonical link. Legacy root upgrade tests cover template versions 2 through 6.
- `git diff --check` — passed.
- User-run native desktop dogfood exposed the missing semantic update; it has occurred, but has not passed acceptance. Read-only evidence from session `90ef9c59-916e-4b35-bff0-c44634acda88` shows a version-5 root, a 365-line compaction snapshot, and no accepted topical coverage.
- Isolated installed Codex `0.163.0-alpha.10.2` app-server testing emitted real manual compaction, immediate compact recovery, and five `Stop` results marked `blocked`. The model attempted indexing but sandbox reads were denied; the final Stop surfaced incomplete status. This is delivery/failure-path evidence, not successful indexing, retrieval, desktop acceptance, or automatic-threshold proof.
- The original installed launcher returned valid continuation JSON in disposable replays taking 7.3-8.7 seconds under its 10-second deadline. An instrumented replay took 9.1 seconds and issued 389 atomic writes. The repaired replay used 12 atomic replacements and took 13.3 seconds under varying I/O conditions, within the new 60-second budget. The original timeout remains a hypothesis: no retained provider timeout record was found, and the old launcher replays did not time out.
- Python compilation and Pylance syntax checks passed; adapter error diagnostics were cleared using equivalent type-narrowing guards.
- The earlier authorized live-profile upgrade installed `versions/1.0.0-af9f03bb47404a02`; its bytes matched version-6 source at installation. All 8,154 existing session-file size/mtime records and 75 ledger/index/manifest/map content hashes were unchanged then, as was configuration outside the managed hook block. Version-7 source has not been installed into that profile.
- Assistant-owned manual app-server semantic acceptance now passes. Native desktop/automatic-threshold acceptance, broader rollback coverage, and cross-platform validation remain pending. Existing benchmark sessions were not modified.
- Subsequent desktop session `67f21f25-3e7e-4420-a70b-c12e1672861a` confirms model-authored graph edits and structural coverage through manual PostCompact line 61, but fails tool-content semantic discovery. All 33 tool-result payloads use `tool_response`; previews expect `tool_output`. A 40,109-character result at line 10 contains the queried story details but previews as only `Bash`. The model's maintenance read omits that field and later retrieves answers directly from the original corpus. See the active memory for the falsifiable reproduction and remaining content-granularity gap.

## Supporting Documents

- [Captured recall provenance JSON](PL-20261027-total-recall-codex-installer-hardening.recall-provenance.json)
- [PL-20261027-total-recall-codex-installer-hardening memory](PL-20261027-total-recall-codex-installer-hardening.memory.md)
- [Source backlog item](../backlog/PL-20261027-total-recall/PL-20261027-total-recall-codex-installer-hardening.md)
- [Parent Total Recall epic](../backlog/PL-20261027-total-recall.md)
- [Completed installer dependency](../closed/PL-20261027-total-recall-codex-installer/PL-20261027-total-recall-codex-installer.sdd.md)
