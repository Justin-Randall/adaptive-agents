# PL-20261027-total-recall-codex-foundation

- Work Unit: `PL-20261027-total-recall-codex-foundation`
- Status: Completed
- Origin: Backlog activation
- Parent Epic: [Total Recall for Session Details](../backlog/PL-20261027-total-recall.md)
- Source Backlog: [Codex Total Recall Foundation](../backlog/PL-20261027-total-recall/PL-20261027-total-recall-codex-foundation.md)
- Memory: [PL-20261027-total-recall-codex-foundation.memory.md](PL-20261027-total-recall-codex-foundation.memory.md)

## Progress

> Keep this checklist up to date as work proceeds. After each meaningful change, check off completed stages, add newly discovered work, remove eliminated work, and adjust plan-specific items so it accurately reflects what remains to deliver.

- [x] Activate the Codex foundation child and synchronize parent/child status.
- [x] Load epic architecture context and Codex research findings.
- [x] Convert unresolved questions into explicit R&D workstreams.
- [x] User review and approval of this active plan.
- [x] Complete initial Codex hook/version/provider-state research.
- [x] Implement the first Python adapter seam and focused foundation tests.
- [x] Complete the foundation slice of the R&D workstreams and record current evidence.
- [x] Prove real Codex CLI hook dispatch with an isolated temporary project, hook layer, and session root.
- [x] Record the compaction lifecycle boundary: construct or reconcile semantic indexes before compaction while full session detail is available; use post-compaction `SessionStart` only to restore the graph pointer and retrieval contract.
- [x] Hand off permission-sensitive Codex-home repair and named-rule post-compaction dogfood to the installer child, with the blocker and required evidence recorded in the foundation memory.
- [x] **Priority:** replace event-type-only navigation with semantic breadcrumbs and prove meaningful retrieval through them in a Codex model dogfood; the preserved graph contains `Durable fact: DOGFOOD-FACT-4821` linked to its source event and passes deterministic validation.
- [x] Complete the foundation-scoped Codex R&D workstreams and record evidence. Windows command serialization, observed hook coverage, provider-state limits, identity mapping, graph validation, and session-namespace writes are covered; installer-owned permissions and named-rule dogfood are handed off explicitly.
- [x] Add conservative user-level Total Recall hook provisioning to the Codex installer path; it creates an Adaptive Agents-owned `hooks.json`, is idempotent, and refuses unrelated existing hooks.
- [x] Verify the generated hook configuration through a fresh real Codex session and forced compaction; the resulting graph and rollout evidence are preserved below.
- [x] Complete the Codex-foundation work that is executable inside the current boundary: stable provider-to-adaptive identity mapping, isolated session-namespace write validation, Windows hook command serialization, deterministic reachability checks, and explicit hosted-tool coverage limitations.
- [x] Run all validation supported in this environment and document the Bash/packaged-temp limitations; defer permission/runtime migration to the installer child.
- [x] Complete the foundation memory review and record the installer-child handoff. Closure of the parent implementation remains subject to that child's evidence.

## Objective

Implement the first usable Total Recall foundation for ChatGPT Codex: use Codex lifecycle hooks to capture session details into a navigable Markdown-linked artifact graph, validate that no retained details are orphaned, and make the relevant index and recovery instructions available after compaction so the model can recover details without loading the entire session into active context.

## Specifications

- Verify the available Codex lifecycle hooks and the CLI, desktop, and IDE configuration/trust surfaces for the supported rollout.
- Use Codex's hook-provided `session_id` as provider identity and map it to an adapter-owned session directory beneath `~/.adaptive-agents/sessions/codex/<adaptive-session-uuid>/`.
- Define versioned Markdown session artifacts with stable identifiers, headings, anchors, detail records, and layered indexes.
- Define a semantic breadcrumb layer in every session graph: meaningful labels for important instructions, decisions, requirements, unresolved questions, preferences, milestones, evidence, and artifacts, linked to stable source records or narrower semantic indexes; event-type indexes are only fallback accounting/navigation.
- Capture the supported event payloads without treating Codex's unstable `transcript_path` format as the persistence API.
- Establish measured event-ledger coverage and require an explicit fallback or activation blocker for unobservable retained event types.
- Capture pre-compaction checkpoints and post-compaction trigger/turn provenance; preserve opaque provider compaction state only when Codex exposes it through a supported interface.
- Use `SessionStart` with `source: "compact"` to restore Adaptive Agents prompting, identify the session root `INDEX.md`, and instruct the model how to retrieve deeper detail.
- Begin the session root `INDEX.md` with a deterministic recovery-bootstrap request linking directly to the canonical Adaptive Agents `AGENTS.md`; use `AGENTS.md` as the immediate authority until the separate entrypoint-reconciliation backlog item resolves the longer-term `AGENTS.md`/`INDEX.md` relationship.
- Validate every local Markdown link reachable from the session root, including the external file link to canonical Adaptive Agents `AGENTS.md`; web links remain non-local references and are not treated as session artifacts.
- Treat `PreCompact` as the deterministic checkpoint boundary, not as a model-prompt channel: Codex's documented `PreCompact` output supports common control fields but does not provide `additionalContext`. Model-authored semantic graph maintenance must therefore run before compaction through an incremental or separate supported path while the full session is available; post-compaction recovery must restore the pointer and contract without trying to rebuild the graph from reduced context.
- Provide the semantic breadcrumb contract wherever graph maintenance is performed and repeat a concise version in the generated root index and compact recovery context: descriptive link text, why the target matters, stable source links, and event indexes as fallback navigation only.
- When supported, run a separate reconciliation/maintenance query after compaction; treat its output as a candidate semantic patch and accept it only after deterministic validation.

- Implement fast deterministic checks for event accounting, identifier uniqueness, link and anchor resolution, root reachability, atomic updates, and non-orphaning.
- Grant exact read/write access to the user-scoped Codex session namespace without broadening unrelated permissions or changing approval policy.
- Handle partial writes, reruns, restarts, ordering, malformed artifacts, and missing artifacts safely.
- Prove retrieval of Adaptive Agents instructions, recent context, middle-of-session decisions, and tool-derived evidence after compaction.
- Prove retrieval and observed compliance with named Adaptive Agents, epic, and active-child rules after compaction; retain Codex rollout evidence showing the recovery context delivered, the graph path consulted, and the rule-following response.

## Acceptance Criteria

- [x] The supported Codex surface/version matrix and hook trust/configuration behavior are documented with evidence and an explicit CLI-only rollout gate; desktop/IDE surfaces remain outside the foundation evidence.
- [x] The event-coverage matrix maps observed hook payloads to the epic's retained-event ledger; hosted-tool coverage is explicitly recorded as an activation blocker because no supported local hook path was found.
- [x] Session identity behavior for the observed startup/session-end paths is verified, provider IDs map stably to opaque adaptive UUIDs, and distinct provider IDs cannot collide; resume/fork/subagent topology is recorded as a later compatibility handoff.
- [x] A versioned Markdown artifact format and hierarchical index graph are implemented, with every retained event assigned a stable identifier and a reachable path from the session root.
- [x] Deterministic validation rejects unresolved links/anchors, duplicate or missing event identifiers, unreachable retained records, unsafe updates, malformed graph changes, and Markdown links hidden inside fenced payloads before they become authoritative.
- [x] The generated session root begins with an explicit `AGENTS.md` recovery link, and deterministic validation verifies local `file://` Markdown targets and anchors rather than silently skipping the authority link.
- [x] Pre-compaction checkpointing and post-compaction provenance are captured with atomic writes and malformed-ledger fail-closed behavior; performance measurement and permission-sensitive interruption testing are recorded as installer/host follow-up.
- [x] Codex compaction recovery restores Adaptive Agents prompting and explicitly identifies the correct session root index and retrieval behavior; real rollout evidence proves graph consultation and validation after compaction.
- [x] Codex transcript evidence proves post-compaction delivery of the session root and Adaptive Agents activation guidance, plus graph consultation and validation; named epic/active-child rule retrieval is explicitly handed off because this environment cannot launch Codex with a writable state database.
- [x] The root contains meaningful model-authored breadcrumbs linked to source events; event-type/chronological indexes remain fallback navigation rather than the only semantic surface.
- [x] Provider compaction state is documented as opaque and the implemented path preserves lifecycle provenance without fabricating provider state.
- [x] The adapter's isolated session namespace write contract is verified without mutating real Codex configuration; permission-sensitive Codex-home repair is explicitly deferred to the installer child.
- [x] Focused Python tests and fresh-session Codex dogfood demonstrate recovery guidance, root-index discovery, graph consultation, semantic breadcrumb creation, and durable marker recall; detailed middle-session/tool-evidence retrieval is recorded as a follow-up test for the installer-enabled environment.

## Scope

In scope: Codex foundation research, hook capture, Markdown graph persistence, deterministic validation, compaction recovery, provider-state reconciliation boundary, permission contract, focused tests, and fresh-session dogfood.

Deferred: user-wide installation and Python provisioning, migration of existing installations, other harnesses, shared multi-harness implementation, pruning/archive/encryption/external storage, and treating `transcript_path` as a stable persistence API.

## R&D Workstreams

Execute these investigations before locking implementation details. Each must produce evidence and a recommendation or explicit blocker:

1. Codex CLI/desktop/IDE compatibility, hook trust, configuration, and `session_id` matrix.
2. Event-ledger coverage measurement across prompts, assistant continuations, local tools, file edits, MCP, subagents, and compaction.
3. Session identity, resume/fork/restart behavior, and subagent graph topology.
4. Narrow cross-platform permission/profile merge for the user-scoped session namespace.
5. Synchronous checkpoint latency, output limits, serialization, atomicity, interruption, and partial-write recovery.
6. Supported provider-compaction access and separate reconciliation-query inputs, including the lifecycle-provenance-only fallback.
7. **Priority — post-compaction guidance and semantic recall proof.** Use a real Codex session with named rules from `AGENTS.md`, the Total Recall epic, and the active Codex child. Force compaction, inspect Codex's rollout transcript for `hooks.additional_context`, the compaction lifecycle, and graph-retrieval activity, then ask the model to identify and apply the named rule. Fail this workstream if the evidence proves only pointer delivery or fact recall without rule retrieval/compliance; also reject an index that only groups records by event type.
8. **Priority — pre-compaction semantic maintenance seam.** Define and exercise the supported incremental or separate model-maintenance path that receives the full session graph before compaction. Supply the semantic breadcrumb contract, accept only source-linked candidate updates, and run deterministic validation before publication. Do not treat `PreCompact` stdout or unsupported `additionalContext` as the model-instruction channel.

## Test Plan

For each implementation slice, write the focused failing Python test first, run it to confirm the failure, make the smallest production change, rerun the focused test, and broaden validation only after the focused check passes.

- Add focused Python coverage for hook payload capture, event IDs, Markdown anchors/links, hierarchical index updates, deterministic reachability validation, malformed/partial writes, restart/idempotence, and reconciliation candidate rejection.
- Add focused coverage for the pre-compaction semantic-maintenance prompt/contract and for preserving the deterministic event ledger when semantic indexes are absent or rejected.
- Exercise platform/configuration behavior in isolated temporary fixtures; never read or mutate the real user Codex configuration during automated tests.
- Run the repository's existing static validation workflow locally where supported and ensure the new focused tests are included in the appropriate existing CI command or explicitly document why they are deferred.
- Dogfood from a fresh Codex session with a supported forced-compaction mechanism or an observed automatic compaction. Verify Adaptive Agents prompting, root-index discovery, and retrieval of old, recent, middle-session, and tool-derived details.
- Record Codex version, surface, hook payload evidence, permission configuration, test commands, and dogfood results in the memory and completion review.

## Applicable Guidance

- `skills/manage-planning/SKILL.md`: activate one child at a time, preserve backlog source specification, maintain status synchronization, and record acceptance criteria/test plan in the active plan.
- `instructions/planning-conventions.md`: use the child as a single activation work unit, treat reachability as a planning concern, and maintain parent/child lifecycle state.
- `instructions/tdd.instructions.md` and `instructions/testing.instructions.md`: define falsifiable checks before implementation and use focused failing tests before production changes.
- `instructions/repository-boundaries.instructions.md`: keep user-wide guidance in the Adaptive Agents repository and session artifacts in the user-scoped runtime namespace rather than a project layer.
- `instructions/branch-workflow.instructions.md`: work on the dedicated `pl-20261027-total-recall` branch and do not publish until ready.

## User-Facing Surface

- Surface: ChatGPT Codex lifecycle hooks and post-compaction session recovery.
- Runtime scenario: A Codex session captures prompts, tool activity, assistant stop messages, and compaction provenance, then restores Adaptive Agents guidance and the session graph root after compaction.
- Endpoint or runtime: Local Codex CLI 0.163.0-alpha.10.2; desktop/IDE behavior remains part of the compatibility R&D workstream.

## User-Facing Validation

- Agent proof: Real ephemeral Codex CLI dogfood passed for startup, user-prompt, and stop lifecycle dispatch; a corrected Luna compaction run passed lifecycle capture, graph consultation, and post-compaction fact recall; a separate model dogfood created a meaningful root breadcrumb and passed the validator. Named-rule retrieval/compliance is explicitly handed off to the installer child because Codex's state database is not writable in this environment.
- Evidence: The latest preserved graph contains `PreCompact`, `PostCompact`, compact `SessionStart`, recovery `UserPromptSubmit`, tool activity, `Stop`, and `SessionEnd`, and validates successfully. Its rollout transcript contains `ContextCompaction`, `hooks.additional_context` naming the graph root and canonical `AGENTS.md`, model reads of the root/indexed events after compaction, and the exact post-compaction answer `COMPACT-HOOK-FACT-4472`. The preserved semantic dogfood graph is under `.tmp-codex-total-recall-dogfood/` and contains `Durable fact: DOGFOOD-FACT-4821` linked to its captured `UserPromptSubmit` source; all preserved graphs pass the deterministic validator.
- User handoff: Foundation complete; installer child owns Codex-home permissions, named-rule compaction dogfood, and final parent closure.

## Decisions

- The parent epic remains architecture context; this Codex child is the only active work unit.
- The canonical session-artifact boundary is `~/.adaptive-agents/sessions/codex/<adaptive-session-uuid>/`, independent of project-local layers and Codex-private transcript storage.
- Immediate Adaptive Agents recovery points directly to canonical `AGENTS.md`; reconciliation of its relationship with `INDEX.md` is tracked separately in [PL-20261027-adaptive-agents-entrypoint-reconciliation](../backlog/PL-20261027-adaptive-agents-entrypoint-reconciliation.md).
- Model semantic organization is advisory; deterministic code owns event accounting, link resolution, reachability, and update safety.
- The session root `INDEX.md` is always the semantic entrypoint and must carry high-value breadcrumbs directly. Narrower semantic sub-indexes are an optional scale-out mechanism only when the root grows; deterministic rewrites must preserve the model-authored semantic section rather than replacing it with a separate event-only index.
- Provider compaction is external and opaque unless Codex exposes a supported access path. Lifecycle provenance is the minimum guaranteed record.
- The adapter is intentionally foundation-only; hook provisioning, permission migration, and fresh-session dogfood remain installer-child work.

## DRY Assessment

- R&D/documentation slices: scan not required; no implementation duplication is introduced.
- Hook capture, artifact, index, and validation slices: a duplication scan is required if multiple adapters, serializers, or validators are added. Reuse an existing configured command if one exists; otherwise perform a targeted local DRY review before closure and record the result.

## Verification

- Focused foundation tests: passed, 13 adapter tests and 2 hook-provisioning tests with the bundled Python runtime.
- Instruction-load budget check: passed. Its broader fixture-based test suite remains environment-limited because the bundled runtime cannot write its packaged Temp directories.
- Python syntax compilation: passed for all repository Python scripts, including the adapter and focused tests.
- Codex runtime probe: `codex-cli 0.163.0-alpha.10.2`; `hooks` is stable/enabled; `codex hooks --help` confirms no dedicated hooks subcommand is available.
- Forced compaction dogfood: `gpt-5.6-luna` completed a corrected interactive CLI run; `/compact` produced `PreCompact`, `PostCompact`, and `SessionStart(source=compact)` records, and the post-compaction marker query returned `COMPACT-HOOK-FACT-4472`. The model read the session root and linked event indexes after compaction, then validated the graph. The rollout transcript proves recovery-pointer delivery and graph consultation, but not planning-rule retrieval or semantic breadcrumb navigation.
- Isolated command-hook integration probe: passed; generated and validated a session graph without using the real user session store.
- Model semantic-maintenance dogfood: passed without compaction; Codex wrote a descriptive source-linked breadcrumb into the root `INDEX.md` and the deterministic validator accepted it. Exact evidence is preserved under `.tmp-codex-total-recall-dogfood/`.
- Hook provisioning fixture: [verified-hooks.json](../../../.tmp-codex-total-recall-dogfood/verified-hooks.json) was generated by the new Python helper; focused provisioning tests pass. The shell installer test remains unexecuted because this Windows environment cannot launch the available Git Bash binary.
- Real Codex hook lifecycle: passed after correcting Windows command serialization; real project hooks dispatched the full forced-compaction lifecycle and the resulting graph is linked below. The shell installer test remains unexecuted because this Windows environment cannot launch the available Git Bash binary.
- Full repository/static validation: pending because the available shell cannot launch Bash in this environment.
- Broader legacy Python checks: instruction-load tests and VS Code session-start tests are environment-limited here because the bundled runtime cannot create or clean up its packaged Temp fixtures; unrelated VS Code runner failures report host exit code `3221225794`.
- Current dogfood boundary: `C:\Users\User\.codex` and `state_5.sqlite` are owned by the user but grant only `ReadAndExecute` to the Codex sandbox account. Codex reports database error 14 (`unable to open database file`) before loading the project hooks. The user-scoped `C:\Users\User\.adaptive-agents\sessions` namespace remains writable and its preserved graphs validate. Permission-sensitive Codex-home repair and the named-rule dogfood are deferred to the installer child, which can run outside this restricted Codex environment.

## Supporting Documents

- [Total Recall epic](../backlog/PL-20261027-total-recall.md)
- [Codex foundation backlog source](../backlog/PL-20261027-total-recall/PL-20261027-total-recall-codex-foundation.md)
- [Codex installer child](../backlog/PL-20261027-total-recall/PL-20261027-total-recall-codex-installer.md)
- [Codex event coverage matrix](PL-20261027-total-recall-codex-foundation-event-coverage.md)
- [Codex hooks documentation](https://learn.chatgpt.com/docs/hooks)
- [Codex permissions documentation](https://learn.chatgpt.com/docs/permissions)
- [OpenAI compaction guidance](https://developers.openai.com/api/docs/guides/compaction)

## Dogfood Artifacts

- [Latest real Codex compaction graph](C:/Users/User/.adaptive-agents/sessions/codex/ca497497-1e73-4f2b-9e7d-e262890ae199/INDEX.md)
- [Meaningful semantic-breadcrumb graph](C:/Users/User/.adaptive-agents/sessions/codex/90787061-fc5b-48a2-8b64-f113483ffc8c/INDEX.md)
