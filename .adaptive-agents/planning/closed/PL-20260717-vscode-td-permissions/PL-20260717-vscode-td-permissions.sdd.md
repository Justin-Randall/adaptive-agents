# PL-20260717: VS Code Trusted-Directory Permissions for Adaptive Agents

- Status: Closed — Completed (2026-07-17)
- Work Unit: PL-20260717-vscode-td-permissions
- Origin: Backlog ([PL-20260717-vscode-td-permissions.backlog.md](PL-20260717-vscode-td-permissions.backlog.md))
- Activated: 2026-07-17
- Closed: 2026-07-17
- Memory: [PL-20260717-vscode-td-permissions.memory.md](PL-20260717-vscode-td-permissions.memory.md)

## Objective

Eliminate read-confirmation dialogs when VS Code's built-in Copilot tools access the user-wide Adaptive Agents installation directory. The agent must read `AGENTS.md` and follow `INDEX.md` routing from unrelated workspaces without intervention. External writes remain governed separately by VS Code's terminal and session permission model.

## Specifications

### Problem Spec

The VS Code integration installs via `scripts/install-vscode.sh`:

1. Writes `vscode/user-wide.instructions.md` with `@`-referenced paths to the Adaptive Agents repository (e.g., `@C:/Users/logic/github.com/Justin-Randall/adaptive-agents/...`).
2. Registers the `vscode/` directory in `chat.instructionsFilesLocations` in VS Code `settings.json`.
3. Enables `chat.includeApplyingInstructions` and `chat.includeReferencedInstructions`.

This is **Part A (native entry point)** — the instructions load. However, **Part B (trusted source-directories grant)** is incomplete. When the Copilot agent encounters an `@`-referenced file path outside the current workspace, VS Code displays a file-read permission dialog asking the user to approve access. The agent cannot proceed until the user clicks through.

The current workaround requires the user to ask "Is Adaptive Agents active?" — this forces the agent to attempt enough file reads that VS Code surfaces the permission prompts. The user then approves them one by one. This is:

- **Non-discoverable** — new users don't know the magic question.
- **Frictionful** — permission prompts may reappear across sessions depending on VS Code's caching.
- **Inconsistent** — other integrations (Claude Code, OpenCode, Cline, Cursor) have fully scripted Part B trust grants.

### Research Phase

Before implementing, identify VS Code's persistent mechanism(s) for pre-granting Copilot Agent read/write access to a directory outside the current workspace. Candidates to investigate:

| Candidate | Description | Status |
| --------- | ----------- | ------ |
| `github.copilot.chat.additionalReadAccessPaths` | Public array setting consumed by Copilot's read-only built-in tools for paths outside the workspace | ✅ **Confirmed in package schema, implementation, unit tests, and live dogfood** |
| `github.copilot.chat.additionalReadAccessFolders` | Initially inferred from documentation wording and installed during the first attempt | ❌ **Not a registered setting; live dogfood disproved it** |
| `chat.tools.terminal.blockDetectedFileWrites` | Controls approval for terminal file writes outside workspace (default: `outsideWorkspace`) | ✅ **Confirmed — governs write-back path** |
| `chat.instructionsFilesLocations` side effect | Does registering an instructions directory implicitly grant read access to files referenced therein? | ❌ Only covers files physically in the registered directory, not `@`-referenced paths outside it |
| `security.workspace.trust.untrustedFiles` | Controls file-open dialogs for files outside workspace | ❌ Too broad; controls file open behavior, not agent tool access |
| `github.copilot.chat.experimental.trustedDomains` | Existing VS Code setting for trusted URL/web domains | ❌ Not for file paths — only URL/web fetch approval |
| Workspace trust (`security.workspace.trust.enabled`) | Full trust grants at workspace level | ❌ Too broad; applies to opened workspace, not referenced external paths |
| `workbench.trustedDomains` / `files.dialog` trust | General VS Code file trust model | ❌ Not for agent tool access |
| VS Code `machine.json` or other non-settings trust stores | Persistent per-machine grant storage | ❌ No scriptable equivalent found |

The research phase must produce a clear winner (or combination) that meets these criteria:

- Persists across restarts. ✅ (`additionalReadAccessPaths` is a persistent user setting)
- Is scriptable from a shell installer. ✅ (can be `jq`/Python-merged into `settings.json`)
- Is narrow (grants access only to the Adaptive Agents repo, not entire drives). ✅ (per-folder paths)
- Works for the Copilot Agent Mode specifically (not just Chat panel). ✅ (documented as applying to "built-in agent tools")

### Feature Spec

**Phase 1 — Research ✅:**

1. ✅ **Fetch VS Code official docs** — Reviewed AI settings reference, Security docs, Approvals docs, Workspace Trust docs, Custom Instructions docs, and 1.129 release notes.
2. ✅ **Fetch VS Code API docs** — Searched for relevant API surfaces via `get_vscode_api` and `github_text_search`.
3. ✅ **Search GitHub for patterns** — Searched `microsoft/vscode` and `github/copilot` scopes for settings, changelogs, and configuration patterns.
4. ✅ **Synthesize findings** — Winner: `github.copilot.chat.additionalReadAccessPaths` for read-only built-in tools. The first `additionalReadAccessFolders` implementation was falsified by live dogfood and corrected from the VS Code package schema and source. Write-back is governed separately by `chat.tools.terminal.blockDetectedFileWrites`.
5. ✅ **Test candidate setting** in a fresh VS Code session from an unrelated repo; user confirmed the dogfood passed without read-confirmation prompts.
6. ✅ **Verify** the read mechanism survives a fresh session. External writes remain governed separately by VS Code's terminal/session policy.
7. ✅ **Final documentation** — Corrected mechanism, failed first attempt, migration, and live result are documented in memory.

**Phase 2 — Installer update ✅ (`install-vscode.sh` updated):**

The trust-grant logic must:

1. Accept the Adaptive Agents repository path.
2. Write the trust grant to the correct VS Code config location (settings.json or other persistent store as determined by Phase 1).
3. Use marker-based section management or merge logic for idempotent updates.
4. Support `--dry-run`.
5. Preserve any existing trust grants the user may have.
6. Verify the exact destination content after write.

**Phase 3 — Health check update ✅ (`check-adaptive-agents.sh` updated):**

Add a VS Code integration check function that:

1. Parses the VS Code settings file (string-aware JSONC, same as the installer).
2. Validates that the trust grant for the Adaptive Agents repo exists.
3. Reports PASS/FAIL with actionable output.
4. Supports `--verbose` (skipped by default).

**Phase 4 — Automated test script ✅ (`scripts/test-install-vscode.sh`):**

Create an isolated automated test that runs entirely against temp directories — never touches real user configuration. Covers:

- Fresh install to empty config.
- Idempotent rerun (byte-stable).
- Dry-run writes nothing.
- Trust-grant validation.
- Unrelated-config and user-file preservation.

**Phase 5 — Dogfood ✅:**

From an unrelated repository in a fresh VS Code session:

1. **Sentinel probe**: Agent responds with `ADAPTIVE_AGENTS_GLOBAL_LOADED`.
2. **Content-proof probe**: "What is the current active plan?" — answerable only from `ACTIVE.md`.
3. **Routed write-back**: Capture a retrospective note to `retrospectives/inbox/` verifying the permission-less integration.

All three must pass without any user-intervention for file-access dialogs.

### Interface/Contract Spec

**install-vscode.sh interface (no CLI changes — existing flags preserved):**

```text
./scripts/install-vscode.sh [--dry-run] [--code-flavor code|insiders|codium] [--settings PATH]
```

Internally it gains the trust-grant step: after updating `settings.json` for instructions, also writes the trust grant (idempotent, survives reruns).

**check-adaptive-agents.sh interface:**

New function `check_vscode_integration()`:

```text
check_vscode_integration [--verbose]
```

Called from main check routine. Runs only when VS Code settings are detected (SKIPs gracefully if not). Validates both Part A (instructions loading) and Part B (trust grant).

### Data Model Spec

The trust-grant data model has been confirmed during Phase 1 research:

**Read access — `github.copilot.chat.additionalReadAccessPaths`:**

- **Location**: VS Code User `settings.json`
- **Key**: `github.copilot.chat.additionalReadAccessPaths`
- **Type**: Array of folder path strings
- **Format**: Absolute paths, forward-slash on all platforms recommended
- **Scope**: User setting (applies across all workspaces)
- **Example**:

  ```json
  "github.copilot.chat.additionalReadAccessPaths": [
    "C:/Users/logic/github.com/Justin-Randall/adaptive-agents"
  ]
  ```

**Write access — `chat.tools.terminal.blockDetectedFileWrites`:**

- The agent's built-in file edit tools are workspace-scoped. Writing outside workspace (e.g., retrospective capture) uses terminal commands.
- `chat.tools.terminal.blockDetectedFileWrites` defaults to `outsideWorkspace`, requiring user approval for terminal writes outside the workspace.
- This is not fully scriptable — comparable to the Antigravity installer caveat (Part B write side requires one-time user action).
- **Recommendation**: Document as a known limitation; write-back via terminal commands requires user approval on first use per session, or using Bypass Approvals session permission.

### Behavioral Spec

1. **Before install**: Requesting file read outside workspace → permission dialog.
2. **After install**: Read-only built-in tools read `AGENTS.md`, `INDEX.md`, and `ACTIVE.md` without prompts. External writes still follow VS Code's separate terminal/session approval policy.
3. **Rerun idempotent**: Running installer again produces identical config (no duplicates).
4. **Dry-run**: Shows what trust grant would be written without modifying files.
5. **Backup**: The existing backup mechanism (`settings.json` timestamped backup) covers all settings changes.
6. **Upgrade path**: If VS Code changes its permission model in a future version, the installer detects the change and reports actionable guidance.

## Applicable Guidance

- **Cross-tool integration contract (from backlog INDEX.md)**: Every integration is exactly two parts at user scope — (1) a single native entry point loading canonical `AGENTS.md` content, and (2) a trusted source-directories grant. Part A is done. This work unit completes Part B for VS Code.
- **Installer-duties contract (from backlog INDEX.md)**: Migrate don't accumulate; isolated automated tests; live health check; version pinning. The existing VS Code integration predates this contract — bring it to parity by adding a health check and automated test script.
- **Two-part pattern**: Proven by Claude Code (`permissions.additionalDirectories`), OpenCode (`instructions` entry), Cursor (`.cursorrules`), Cline (`cline_rules`), Antigravity (`trustedFolders.json`).
- **Content-proof probe requirement**: The sentinel alone can be a false positive (as PL-20260711 OpenCode proved with a stale installed copy). Must verify with a content-proof probe answerable only from repository content.
- **Branch workflow**: `instructions/branch-workflow.instructions.md` — create a `pl-PL-20260717-vscode-td-permissions` branch from primary after activation.

## Scope

1. ✅ **Phase 1** — Source research and live confirmation of the corrected mechanism are complete.
2. ✅ **Phase 2** — Updated `install-vscode.sh` to write the trust grant. Idempotent, dry-run support, backup, content verification.
3. ✅ **Phase 3** — Added `check_vscode_integration()` to `check-adaptive-agents.sh`. Validates Part A (instructions) and Part B (trust grant).
4. ✅ **Phase 4** — Added `scripts/test-install-vscode.sh`; it covers fresh install, obsolete-key migration, JSONC, preservation, dry-run, and idempotence.
5. ✅ **Phase 5** — User-confirmed dogfood from an unrelated repository passed without read-confirmation dialogs.

## Out of Scope

- Other VS Code Copilot surfaces (Chat panel, inline completions) — Agent Mode is the target.
- Other integrations' permission models (Claude Code, Cline, etc. already have Part B).
- Project-owned instruction file generation (`.github/copilot-instructions.md`).
- General VS Code settings unrelated to file permissions.
- Reverse-engineering undocumented binary/protobuf stores (if the trust mechanism is not scriptable, document the limitation like Antigravity did).
- Proactive permission revocation (the installer creates, not removes — user can manually revert).

## Acceptance Criteria

| # | Criterion | Verification |
| --- | --- | --- |
| AC1 | Phase 1 complete: VS Code's Copilot Agent file-permission mechanism is identified, tested, and documented in memory.md. | Memory file documents mechanism, exact config location, and data format. |
| AC2 | Phase 2 complete: `install-vscode.sh --dry-run` reports the trust grant without writing. | Dry-run output contains trust-grant details. |
| AC3 | Phase 2 complete: `install-vscode.sh` writes the trust grant to the correct location. | Actual config file contains the grant after install. |
| AC4 | Phase 2 complete: Rerunning the installer is idempotent — no duplicate entries, settings unchanged. | Config file before and after second run is byte-identical. |
| AC5 | Phase 3 complete: `check-adaptive-agents.sh --verbose` includes the VS Code integration check and passes. | Check reports PASS for VS Code integration. |
| AC6 | Phase 3 complete: `check-adaptive-agents.sh` reports non-passing status when the trust grant is absent. | Check reports FAIL (or SKIPs) with actionable output. |
| AC7 | Phase 4 complete: `scripts/test-install-vscode.sh` exists, runs against temp dirs, and passes all test cases. | Test script exits 0; covers fresh install, rerun, dry-run, trust-grant validation, unrelated-config preservation. |
| AC8 | Phase 5 complete: Dogfood from unrelated repo in fresh VS Code session — sentinel, content-proof, and routed write-back pass without any file-permission prompts. | User confirms all three probes pass without dialogs. |

## Verification

- `bash scripts/test-install-vscode.sh`: 5 passed, 0 failures.
- `bash scripts/check-adaptive-agents.sh --verbose`: 159 passed, 0 failures; one unrelated Antigravity permission warning.
- Live settings contain `github.copilot.chat.additionalReadAccessPaths` with the repository root and no obsolete `additionalReadAccessFolders` key.
- User-confirmed fresh-session dogfood from an unrelated workspace passed on 2026-07-17.

## Disposition

Completed on 2026-07-17. No deferred scope or follow-up backlog item was identified.
