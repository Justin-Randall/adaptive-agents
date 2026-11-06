# PL-20260711: GitHub Copilot Agent Mode Support

- Work Unit: PL-20260711-copilot-agent-mode
- Branch: `PL-20260711-copilot-agent-mode`
- Source backlog: [PL-20260711: GitHub Copilot Agent Mode Support](PL-20260711-copilot-agent-mode.backlog.md)
- Memory: [PL-20260711-copilot-agent-mode.memory.md](PL-20260711-copilot-agent-mode.memory.md)
- Status: Closed — Completed (2026-11-05)

## Objective

Verify and extend the VS Code installer so GitHub Copilot Agent Mode consistently loads canonical Adaptive Agents guidance and provides usable Total Recall evidence across fresh sessions, including assistant responses needed for later retrieval.

## Problem Spec

Live dogfooding proved that the Copilot hook captures `SessionStart`, `UserPromptSubmit`, `PostToolUse`, and `Stop` metadata, and that Copilot can search captured prompt text. However, long assistant responses are absent from the Markdown ledger: `Stop` payloads contain only metadata and `text_parts: []`, while the response remains in Copilot's separate `events.jsonl` transcript. This prevents Total Recall from recalling details from large model outputs. The integration also needs a persistent read/write access boundary for the canonical repository and routed write-back workflows without avoidable approval prompts.

## Scope

- Preserve the supported Copilot version-1 camelCase hook contract and existing session-start context injection.
- Add bounded, deduplicated capture of assistant-visible response content from the Copilot transcript path supplied by terminal lifecycle events, without modifying supplied user session artifacts.
- Cover incomplete, locked, malformed, and repeated transcript reads with focused tests.
- Validate the installed hook and effective VS Code configuration, including the repository access boundary, while preserving unrelated settings.
- Dogfood from an unrelated workspace using sentinel, content-proof, response-recall, and routed-write probes.
- Do not auto-approve arbitrary terminal commands or silently bypass Copilot's security prompts.

## Acceptance Criteria

1. A fresh Copilot session records exact user prompts and assistant-visible response text in the provider-specific Markdown ledger.
2. Large responses are captured with bounded processing and no duplicate records across repeated stop events.
3. A later Copilot prompt can retrieve a distinctive detail that exists only in the captured assistant response, with a ledger source anchor.
4. Transcript absence, locking, truncation, malformed lines, and adapter failure remain explicit and do not corrupt the ledger.
5. Existing VS Code hook/settings tests and the repository checker pass; unrelated settings remain unchanged.
6. The installed configuration documents the unavoidable distinction between filesystem access and Copilot's per-session tool approval.

## Applicable Guidance

- `instructions/global.instructions.md` (user-wide guidance): verify claims with tests and source evidence; prefer small reversible changes.
- [Project architecture](../../../ARCHITECTURE.md): keep one authoritative append-only ledger and treat indexes as navigation.
- [Manage planning skill](../../../skills/manage-planning/SKILL.md): keep acceptance evidence and handoff memory current; closure requires approval.

## Test Plan

- Add focused adapter/ledger tests using synthetic Copilot payloads and transcript fixtures.
- Run the VS Code integration and installer tests, Python compilation, and project-layer validation.
- Perform fresh authenticated VS Code dogfood and compare model retrieval with host-side ledger and transcript evidence.

## Decisions

- Keep the Copilot provider namespace separate from Codex while reusing the shared Markdown ledger implementation.
- Treat the Copilot transcript as an input source for response capture only when the hook explicitly supplies its path; do not scan unrelated session-state files.
- Use bounded incremental reads and a stable source fingerprint to avoid duplicating responses.

## Progress

- [x] Activate the Copilot Agent Mode work unit and synchronize planning metadata.
- [x] Capture live Copilot/Total Recall evidence and identify the assistant-response gap.
- [x] Implement response capture, write access, installer checks, and focused validation.
- [x] Complete final merge review and closure approval.

## Completion Review

- Implementation and installer follow-up work are present on `main` through commit `87035ef`.
- The worktree was clean at closure; the Copilot response-capture, installer check-mode, trust-boundary, and focused validation changes were already merged.
- The remaining unchecked item was planning metadata, not an implementation defect.
- Disposition: Completed. No blocking gap remains within this work unit. Broader Total Recall retrieval and semantic-index quality questions remain separate backlog work.

- Activated from backlog with user approval on 2026-11-04.
- Confirmed live prompt capture and ledger retrieval in authenticated VS Code.
- Confirmed the response-capture gap in session `ea08eabd-0012-4846-8246-9f9cb7466383`: long prompts are present in `ledger.md`, but `Stop` records have empty `text_parts`; assistant output is present only in the referenced Copilot transcript.
- Added bounded extraction of the latest non-empty `assistant.message.content` from the supplied transcript path and a deduplicated `AssistantResponse` ledger event.
- Added three focused response-capture tests; response tests and the five existing VS Code integration tests pass. Python compilation and `git diff --check` pass.
- The host hook already points at the repository adapter, so the updated source is immediately used. A full installer rerun was blocked by the checked-in installer having CRLF line endings (`set: pipefail: invalid option name` under Bash); this is recorded as a follow-up installer portability issue.
- Further analysis of user dogfood session `a2c1ed75-384d-421e-be6e-224cb2df3d87` found a valid 33-event ledger, nine paired `Stop`/`AssistantResponse` records, one `PreCompact` record, and successful literal retrieval of a detail found only in an assistant response. The index has no model-authored topics, so semantic-quality certification remains false; this is a navigation-quality gap, not a capture-integrity failure.
- Fixed the review items: transcript reads now use the bounded tail, the installer grants the canonical repository sandbox read/write access, all lifecycle hooks are validated, and tests cover a transcript larger than the scan window. Git Bash installer tests pass all 15 cases; response tests pass 4 cases and integration tests pass 5 cases.
- Added read-only `--check` support to all tool-specific installers and aggregated delegation from `install.sh`; checks validate configuration only and explicitly warn where fresh-session or UI-managed trust cannot be proven.

## Merge Review Follow-up

- Antigravity support is being deprecated by user direction; exclude Antigravity from this follow-up's check-mode normalization and do not expand its validation.
- Remaining quality work: reject `--dry-run --check` consistently; replace Claude/OpenCode substring checks with structured configuration validation; add direct non-mutating tests for installer and umbrella `--check` modes.
- The Copilot/Total Recall core passed review without a blocking defect. These installer-quality items are the remaining pre-merge work.
- Implemented the remaining check-mode fixes: consistent conflict rejection, structured Claude/OpenCode validation, and a focused installer check-mode test registered with the repository checker. Antigravity remains intentionally excluded.
- Git Bash bridge diagnosis completed: the bridge was functional; the first test failure was a fixture layout error, followed by a real `/d/...` versus `D:/...` path-normalization issue. Both are fixed, and installer check-mode tests now pass end-to-end.

## Review Findings To Address

- **P1 — transcript windowing:** `latest_assistant_response()` reads only the first 16 MiB, so a growing transcript can leave the newest response beyond the scan boundary and capture stale content.
- **P1 — write trust gap:** the VS Code installer configures `github.copilot.chat.additionalReadAccessPaths` but no persistent write/trusted-directory grant for routed global Adaptive Agents writes.
- **P2 — boundary coverage:** tests do not cover transcripts larger than the scan limit, partial final JSONL lines, or a locked transcript while the final response is being flushed.
- **P2 — validator depth:** integration health validation deeply checks `sessionStart` but does not validate the shape, command, and timeout of all nine installed lifecycle hooks.

These findings were recorded after baseline commit `1d96430` on branch `PL-20260711-copilot-agent-mode`; fixes and follow-up verification remain in scope.
