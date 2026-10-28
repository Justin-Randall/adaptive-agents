# Codex Total Recall Event Coverage

This matrix records the current Codex hook coverage for `PL-20261027-total-recall-codex-foundation`. It is evidence for the event-ledger acceptance criterion, not a claim that unsupported provider paths are complete.

| Retained detail | Codex observation path | Foundation handling | Current disposition |
| --- | --- | --- | --- |
| User messages | `UserPromptSubmit.prompt` | Capture raw hook payload as a stable event record | Supported |
| Assistant turn message | `Stop.last_assistant_message` | Capture the latest assistant message when provided | Supported with provider-defined “latest” semantics; live dogfood required |
| Local tool calls | `PreToolUse` payload | Capture raw tool name/input and lifecycle metadata | Supported for documented local hook paths |
| Local tool results | `PostToolUse` payload | Capture raw tool name/output and lifecycle metadata | Supported for documented local hook paths |
| Hosted tools such as web search | No local `PreToolUse`/`PostToolUse` hook path | Do not fabricate records; investigate a supported provider event or transcript migration path | Activation blocker for complete all-event recall if no fallback exists |
| Subagent lifecycle | `SubagentStart`/`SubagentStop`, parent `session_id`, `agent_id`, latest assistant message | Capture parent-linked lifecycle records and subagent identity | Supported at lifecycle level; topology dogfood required |
| Compaction | `PreCompact`/`PostCompact` with `trigger` and `turn_id` | Capture lifecycle provenance; manifest records provider state as not exposed by command hook | Supported lifecycle-only path |
| Post-compaction recovery | `SessionStart` with `source: compact` | Return concise developer context naming the root `INDEX.md` and retrieval rule | Supported by documented hook contract; live dogfood required |
| Session start/end | `SessionStart`/`SessionEnd` | Capture lifecycle records; SessionStart returns recovery context | Supported |

## Evidence

- Local Codex runtime: `codex-cli 0.163.0-alpha.10.2`; `codex features list` reports `hooks` stable and enabled.
- Official [Codex hooks documentation](https://learn.chatgpt.com/docs/hooks) documents local tool coverage and explicitly excludes hosted tools from the local function-tool hook path.
- The same documentation says `transcript_path` is provided for convenience but its format is not a stable hook interface.
- Isolated adapter tests cover representative prompt, tool, assistant-stop, subagent, compaction, and recovery payloads. They do not claim hosted-tool coverage.

## Required Follow-up

Before closure, either verify a supported hosted-tool event/fallback or preserve this as a recorded activation blocker and narrow the implementation claim accordingly. Do not silently treat a missing hook event as an empty event.
