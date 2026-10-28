# Backlog: Codex Total Recall Foundation

Plan: PL-20261027-total-recall-codex-foundation

Parent: [Total Recall for Session Details](../PL-20261027-total-recall.md)

Status: Ready for closure

Readiness: Foundation implementation is validated and ready for closure. Installer-owned Codex-home permissions, named-rule compaction dogfood, and the final parent closure review remain explicitly handed off to the installer child.

Test approach: Write focused failing Python tests for hook-event capture, linked index generation, deterministic reachability validation, detail retrieval, restart/idempotence, and compaction recovery; then dogfood a fresh Codex session with forced or observed compaction and verify recovery of old, recent, and tool-derived details plus Adaptive Agents prompting.

## Objective

Implement the first usable Total Recall foundation for ChatGPT Codex: use Codex lifecycle hooks to capture session details into a navigable Markdown-linked artifact graph, validate that no retained details are orphaned, and make the relevant index and recovery instructions available after compaction so the model can recover details without loading the entire session into active context.

## Problem Spec

Codex currently receives canonical Adaptive Agents guidance and can access the repository, but the session itself does not yet have a durable, structured recall surface that preserves detailed user messages, assistant messages, tool calls, tool results, instructions, decisions, and semantic relationships when context is compacted.

## Scope

In scope:

- Verify the Codex lifecycle events or hooks available for observing session turns and compaction.
- Verify the current Codex CLI, desktop app, and IDE extension hook configuration surfaces, enablement defaults, trust requirements, and version differences.
- Use Codex's hook-provided `session_id` as the provider identity and map it to an adapter-owned session directory beneath the user-scoped `~/.adaptive-agents/sessions/codex/` namespace.
- Define a versioned session-artifact format for raw turn details, semantic notes, and layered `INDEX.md` files.
- Implement capture and index updates with stable Markdown anchors and links to detailed records, using `UserPromptSubmit` and supported `PostToolUse` payloads rather than relying on Codex's unstable transcript format.
- Establish and test a Codex event-coverage matrix against the epic's retained-event ledger; any event type that hooks cannot observe must have an explicitly verified fallback or remain an activation blocker rather than becoming an undocumented gap.
- Capture `PreCompact` checkpoints and `PostCompact` trigger/turn provenance; preserve the opaque provider compaction item only if Codex exposes it through a supported interface. Then use `SessionStart` with `source: "compact"` to restore Adaptive Agents prompting, identify the session root index, and tell the model how to search it before continuation.
- When Codex exposes provider state or compaction output through a supported interface, run a separate reconciliation/maintenance query that can propose semantic graph updates; treat its result as a candidate patch and accept it only after deterministic validation. When provider state is not exposed, reconcile using the available lifecycle provenance and captured event ledger rather than inventing provider output.
- Preserve a compact recovery instruction that tells the model when and how to search the session index; keep hook-visible context within Codex's output limits.
- Add a deterministic fast validator for event accounting, link/anchor resolution, root reachability, atomic updates, and non-orphaning before accepting model-proposed semantic graph changes.
- Grant the hook runtime read/write access to the user-scoped Codex session namespace without broadening unrelated Codex permissions or changing the user's approval policy.
- Handle partial writes, reruns, restarts, ordering, and malformed or missing session artifacts safely.
- Prove retrieval of semantically important instructions, recent context, middle-of-session decisions, and tool-derived evidence after compaction.

Deferred:

- User-wide installation, Python environment provisioning, and migration of existing Codex installations; see the installer child.
- Other agent harnesses and a shared multi-harness adapter implementation.
- Automatic pruning, long-term archival, encryption, or external storage.
- Treating Codex's `transcript_path` or transcript file format as a stable persistence API.

## Research Findings

Official OpenAI documentation currently establishes the following Codex behavior:

- [Codex hooks](https://learn.chatgpt.com/docs/hooks) provide `SessionStart`, `PreCompact`, `PostCompact`, `SessionEnd`, `UserPromptSubmit`, `PreToolUse`, and `PostToolUse` lifecycle events.
- Command hooks receive structured JSON on stdin, including the current `session_id`, `cwd`, `hook_event_name`, model, permission mode, and—when available—`transcript_path`. The documentation explicitly says the transcript format is not a stable hook interface.
- `PreCompact` runs before manual or automatic compaction and can stop compaction. `PostCompact` runs after it. `SessionStart` with `source: "compact"` runs before the next model request, including the immediate continuation after mid-turn automatic compaction.
- `SessionStart` can return `additionalContext`, which Codex adds as developer context. Hook output is size-limited by default, so recovery should point to the root index and explain retrieval rather than dump the session graph.
- `PostToolUse` can observe supported local tool input and output, including shell, file-edit, MCP, and other local function tools, but the documentation warns that some specialized paths may opt out of the default hook path. Capture coverage must therefore be measured and validated rather than assumed.
- Background hooks can run concurrently and finish out of order; Codex permits up to eight background hooks per session. Capture writes need serialization, stable ordering, and atomic replacement, or the foundation should keep the capture hooks synchronous.
- Hooks can be disabled, plugin-bundled hooks require trust review, and plugin lifecycle hooks have distribution limitations. The child must verify the installation path selected for local Codex rather than assuming plugin packaging is the only route.
- [Codex permissions](https://learn.chatgpt.com/docs/permissions) support exact user-scoped filesystem rules and workspace roots. The foundation must request only the session namespace it needs; the installer child owns the safe user-level configuration merge.
- [OpenAI compaction guidance](https://developers.openai.com/api/docs/guides/compaction) describes provider compaction state as opaque and intended to be carried forward, which supports preserving provider output as provenance rather than attempting to replace it with the Markdown graph.
- The local Codex hook documentation currently describes `PreCompact` and `PostCompact` trigger/turn metadata, but does not establish that the provider's opaque compaction item is available to a command hook. The implementation must verify a supported access path and must not claim to capture opaque provider state when only lifecycle provenance is available.

## Architectural Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Capture format | Markdown records with stable headings/anchors and machine-checkable metadata where needed | Supports human inspection and direct Markdown traversal while leaving room for deterministic tooling. |
| Index shape | A compact session root index links to semantic topic indexes and detailed event records, expanding into sub-indexes as detail grows | Keeps compaction recovery small and makes deeper evidence discoverable on demand without orphaning records. |
| Session identity | Use the hook-provided Codex `session_id` as provider identity and map it to an opaque Adaptive Agents UUID under the Codex namespace; do not infer identity from `cwd` alone | Codex exposes the current provider session identifier directly, while the adapter-owned UUID keeps storage portable and prevents collisions; reuse across resume/fork behavior must be verified. |
| Capture authority | Use synchronous Codex lifecycle hooks for correctness-critical checkpoints and tool capture; use background hooks only for work that can tolerate reordering or loss | Model-only capture can omit details, and concurrent background hooks can finish out of order or be cancelled at session end. |
| Recovery behavior | Use `SessionStart` with `source: "compact"` to inject concise recovery context naming the root index, Adaptive Agents instructions, and retrieval behavior | Codex delivers this context before the continuation request, including after mid-turn automatic compaction. |
| Transcript boundary | Treat Codex `transcript_path` as a diagnostic or migration input, not the primary event API | Official documentation says the transcript format is not stable for hooks. |
| Permission boundary | Grant the hook runtime exact read/write access to the user-scoped Codex session namespace through the existing user-level permission merge | The session graph lives outside most project workspaces; access must be explicit and narrow without broadening approval behavior. |
| Storage boundary | Treat `~/.adaptive-agents/sessions/codex/<adaptive-session-uuid>/` as the canonical session-artifact location, independent of project-local layers, Codex-private storage, and transcript paths | Recovery must have a stable user-scoped location that the adapter controls and can identify explicitly after compaction. |
| Provider compaction | Preserve provider compaction output as opaque provenance when Codex exposes it; otherwise preserve lifecycle provenance, then reconcile available state with the Markdown graph through a separate maintenance query when supported | Provider bookkeeping may contain state that should be carried forward even when it is not human-readable, but hook-visible data may be limited to compaction metadata. |

## R&D Tasks

These investigations are part of the activated foundation plan. Each task must produce evidence and a recommendation that either closes the design question or records a concrete activation blocker; none should be left as an implicit implementation assumption.

1. **Build the Codex compatibility matrix.** Probe the installed Codex CLI, desktop app, and IDE extension surfaces and versions, and compare their hook configuration, enablement/trust behavior, lifecycle payloads, and `session_id` semantics. Deliver a checked-in or plan-linked matrix identifying the supported rollout target and any version gates.
2. **Measure event-ledger coverage.** Exercise the supported lifecycle hooks with representative prompts, assistant continuations, local tools, file edits, MCP calls, subagent activity, and compaction. Map observed payloads to the epic's retained-event ledger, identify omissions, and recommend a supported fallback or declare the missing coverage an activation blocker. Do not adopt `transcript_path` as a fallback without separately proving its stability and ownership.
3. **Resolve session identity and subagent topology.** Test resume, fork, restart, and subagent behavior to determine when Codex reuses or changes `session_id`, how parent identity is reported, and whether child records should live in the parent graph or in linked child session directories. Deliver the identity manifest and graph-topology rules needed to prevent collisions or orphaned subagent details.
4. **Design and test the permission merge.** Determine the narrowest user-level permission/profile change that grants the hook runtime read/write access to `~/.adaptive-agents/sessions/codex/` on Windows, macOS, Linux, and WSL without mutating unrelated settings or broadening approval behavior. Deliver representative before/after configuration tests and the installer-facing contract.
5. **Benchmark the correctness-critical hook path.** Measure synchronous `PreCompact` checkpoint latency, output-size behavior, concurrent/reordered hook handling, atomic replacement, interruption, and recovery from partial writes. Deliver timeout and serialization thresholds plus the minimum safe checkpoint protocol; identify any work that must be deferred to a later maintenance query.
6. **Investigate provider-compaction access and reconciliation.** Verify whether Codex exposes the opaque provider compaction item through any supported hook or companion interface. If it does, define the provenance artifact and separate reconciliation-query inputs; if it does not, define the lifecycle-provenance-only path and the post-compaction ledger state that the query can safely use. In both cases, demonstrate deterministic validation of the resulting candidate graph patch.

## Related Work

- Parent epic: [Total Recall for Session Details](../PL-20261027-total-recall.md)
- Predecessor integration: [Completed ChatGPT Codex integration](../../closed/PL-20260711-chatgpt-codex-support/PL-20260711-chatgpt-codex-support.sdd.md)
- Depends on no sibling child.
