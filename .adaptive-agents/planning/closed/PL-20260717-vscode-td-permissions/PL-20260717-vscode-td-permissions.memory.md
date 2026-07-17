# PL-20260717-vscode-td-permissions — Working Memory

- Work Unit: PL-20260717-vscode-td-permissions
- Activated: 2026-07-17
- Status: Closed — Completed (2026-07-17)

## Starting State

- **Part A complete**: `install-vscode.sh` writes `vscode/user-wide.instructions.md`, registers `chat.instructionsFilesLocations`, enables `chat.includeApplyingInstructions` and `chat.includeReferencedInstructions`.
- **Part B missing**: No trust grant for the Adaptive Agents repository directory. VS Code prompts for permission on first file read via `@` references.
- **No health check**: `check-adaptive-agents.sh` has no VS Code integration validation function.
- **No automated test**: `scripts/test-install-vscode.sh` does not exist (the VS Code installer predates the installer-duties contract).

## Key Decisions

| Date | Decision | Rationale |
| ---- | -------- | --------- |
| 2026-07-17 | Correct read mechanism: `github.copilot.chat.additionalReadAccessPaths` | VS Code's public Copilot package schema registers this exact array key. `ConfigKey.AdditionalReadAccessPaths`, `toolUtils.ts`, and unit tests confirm that read-only built-in tools allow nested files under configured paths. |
| 2026-07-17 | Migrate and remove `github.copilot.chat.additionalReadAccessFolders` | The first implementation inferred this unregistered key from documentation wording. Live dogfood still prompted, proving the implementation ineffective; the initial health check was also a false positive because it repeated the same assumption. |
| 2026-07-17 | Write access via terminal: `chat.tools.terminal.blockDetectedFileWrites` (default `outsideWorkspace`) means writes outside workspace require approval. Use session-level permission or bypass for write-back workflow. | Confirmed from approvals docs: terminal file writes outside workspace require user approval by default. |
| 2026-07-17 | No separate "write grant" setting exists for agent tool file writes | The agent's built-in file write tools are workspace-scoped. Writes outside workspace use terminal commands which are governed by `blockDetectedFileWrites`. |
| 2026-07-17 | Installer and health check must validate the public key independently | `install-vscode.sh` now writes `additionalReadAccessPaths` and removes the obsolete key. `check-adaptive-agents.sh` checks the public key and reports obsolete-key residue. |
| 2026-07-17 | Isolated installer tests are required before live installation | `scripts/test-install-vscode.sh` covers fresh install, JSONC migration, existing-path preservation, unrelated settings, dry-run, and idempotence. |

## Phase 1 Research Notes

### Sources Consulted

| Source | URL | Key Findings |
| ------ | --- | ------------ |
| VS Code Security docs | code.visualstudio.com/docs/agents/security | Describes workspace-limited file access and additional read access conceptually; the prose-derived key name was not sufficient schema evidence. |
| VS Code Approvals docs | code.visualstudio.com/docs/agents/approvals | Permission levels, tool approvals, terminal command approval; `blockDetectedFileWrites` controls terminal writes outside workspace |
| VS Code AI Settings Reference | code.visualstudio.com/docs/agents/reference/ai-settings | Complete list of all Copilot/agent settings |
| VS Code Custom Instructions | code.visualstudio.com/docs/agent-customization/custom-instructions | How instructions files are loaded, `chat.instructionsFilesLocations` behavior |
| VS Code 1.129 Release Notes | code.visualstudio.com/updates/v1_129 | "Read files outside workspace" feature mentioned for Copilot |
| VS Code Workspace Trust | code.visualstudio.com/docs/editing/workspaces/workspace-trust | `security.workspace.trust.untrustedFiles` controls file open behavior outside workspace |
| VS Code Copilot package schema | github.com/microsoft/vscode/blob/main/extensions/copilot/package.json | Registers the exact public key `github.copilot.chat.additionalReadAccessPaths` as an array. |
| VS Code Copilot configuration source | github.com/microsoft/vscode/blob/main/extensions/copilot/src/platform/configuration/common/configurationService.ts | Defines `AdditionalReadAccessPaths` from `chat.additionalReadAccessPaths`; fully qualified settings use the `github.copilot.` prefix. |
| VS Code Copilot tool source and tests | `toolUtils.ts` and `toolUtils.spec.ts` in `microsoft/vscode` | Configured paths bypass external-file confirmation only for tool calls marked read-only; nested paths are covered. |

### Research Tasks (from ACTIVE.md)

1. ✅ Fetch VS Code official docs for Copilot Agent permissions
2. ✅ Fetch VS Code API docs for extension permission boundaries
3. ✅ Search GitHub for known patterns
4. ✅ Synthesize findings into a clear winner, including source and schema validation
5. ✅ Test corrected setting in a fresh unrelated-workspace session — **user-confirmed pass without read-confirmation prompts**
6. ✅ Verify the read grant in a fresh session; write behavior remains governed separately
7. ✅ Document the corrected mechanism and failed first attempt in this file

## Implementation Progress

| Phase | Status | Details |
| ----- | ------ | ------- |
| Phase 1 — Research | ✅ Complete | Exact mechanism identified as `github.copilot.chat.additionalReadAccessPaths` and confirmed by live dogfood |
| Phase 2 — Installer update | ✅ Complete | Writes the public key and removes the obsolete generated key |
| Phase 3 — Health check | ✅ Complete | Validates the public key and detects stale obsolete-key residue |
| Phase 4 — Automated test | ✅ Complete | Five isolated cases pass, including JSONC migration and idempotence |
| Phase 5 — Dogfood | ✅ Complete | User-confirmed fresh-session test passed from an unrelated workspace |

### Source-Confirmed Mechanism: `github.copilot.chat.additionalReadAccessPaths`

- **Setting key**: `github.copilot.chat.additionalReadAccessPaths`
- **Type**: array of strings (folder paths)
- **Description**: "Grant read-only access to additional folders outside the current workspace for built-in agent tools."
- **Scope**: User setting (not workspace)
- **Format**: Array of absolute paths in the platform-native format (forward slashes on all platforms recommended for cross-platform compat)
- **Example**:

  ```json
  "github.copilot.chat.additionalReadAccessPaths": [
    "C:/Users/logic/github.com/Justin-Randall/adaptive-agents"
  ]
  ```

This setting is the VS Code equivalent of Claude Code's `permissions.additionalDirectories`, OpenCode's `instructions` entry, and Cursor's trusted rules directories. It completes **Part B (read access)** of the two-part integration contract.

### Write Access Strategy

For write-back operations (e.g., writing retrospectives to `retrospectives/inbox/`), the agent uses either:

1. **File edit tools** (workspace-scoped — directly writing outside workspace requires workaround)
2. **Terminal commands** (e.g., `cp`, `mv`, `cat > file`) — governed by `chat.tools.terminal.blockDetectedFileWrites`

The `chat.tools.terminal.blockDetectedFileWrites` setting defaults to `outsideWorkspace`, meaning terminal commands writing outside the workspace require user approval. Options:

- Accept the approval prompt (one-time click per session)
- Use session-level "Bypass Approvals" permission
- Set `chat.tools.terminal.blockDetectedFileWrites` to `never` (least secure)

**Recommendation**: Document that write-back requires the user to approve terminal file writes outside the workspace on first use — comparable to the Antigravity "Part B is not fully scriptable" caveat.

### Candidate: `github.copilot.chat.experimental.trustedDomains`

- Status: **Not applicable — this is for URL/web fetch domains, not file paths.**
- Notes: The `trustedDomains` settings relate to URL approval (web fetch tool), not file system access. From approvals docs: "The pre-approval respects the Trusted Domains feature."

### Candidate: `chat.instructionsFilesLocations` side effect

- Status: **Needs verification — may already grant read access to files in registered directories.**
- Notes: The installer registers `vscode/` directory in `chat.instructionsFilesLocations`. However, `@`-referenced paths point to files *outside* that directory (the repo root, `AGENTS.md`, `INDEX.md`, `instructions/`, etc.). The side effect likely covers only files physically located within the registered `vscode/` directory.

### Candidate: `security.workspace.trust.untrustedFiles`

- Status: **Not the right mechanism — too broad, controls file open behavior not agent tool access.**
- Notes: Controls dialog when opening files outside trusted workspace folders. Default is `prompt`. Changing to `open` would suppress the dialog but also lower security for all untrusted file opens.

### Candidate: Workspace trust

- Status: **Not the right mechanism — trust is per-workspace and the Adaptive Agents repo is not a workspace root during normal usage.**
- Notes: Workspace trust applies to the folder opened in VS Code. The adaptive-agents repo is referenced via `@` paths from a different workspace's instructions.

## Falsification and correction

The first installer wrote `github.copilot.chat.additionalReadAccessFolders`, and the first health check validated that same unregistered key. The health check passed, but a live unrelated-workspace read still requested confirmation. Direct inspection of the current VS Code Copilot package schema and source identified `github.copilot.chat.additionalReadAccessPaths` as the actual public setting. The corrected installer migrated the live user settings, the isolated regression suite passed, and the user confirmed fresh-window dogfood from an unrelated workspace.

## Summary of findings

The source-backed mechanism for read-only built-in tools is `github.copilot.chat.additionalReadAccessPaths`. It is analogous to:

- Claude Code: `permissions.additionalDirectories`
- OpenCode: `instructions` config entries
- Cursor: `.cursorrules` with trusted paths
- Antigravity: `~/.gemini/trustedFolders.json`

Write access for retrospective capture requires the user to approve terminal file writes outside the workspace (or use Bypass Approvals session mode).

## Repository Layout (relevant files)

| File | Role |
| ---- | ---- |
| `scripts/install-vscode.sh` | VS Code installer; writes the public read-path key and migrates the obsolete key |
| `scripts/check-adaptive-agents.sh` | Repository health check; validates the public key and flags obsolete-key residue |
| `vscode/user-wide.instructions.md` | The user-wide instruction file written by the installer |
| `scripts/test-install-vscode.sh` | Isolated installer regression suite |

## Open Questions

1. ✅ Which VS Code mechanism grants read-only built-in tools access to a directory outside the workspace? → `github.copilot.chat.additionalReadAccessPaths`
2. ✅ Is the read mechanism scriptable from a shell installer? → Yes, implemented in `install-vscode.sh` via Python JSONC merge
3. ✅ Does it work in a fresh VS Code session? → Yes, user-confirmed from an unrelated workspace
4. ✅ Does `chat.instructionsFilesLocations` already cover this? → No — only covers files physically within registered directories
5. ✅ What is the exact JSON structure and config file path? → `settings.json`, array of absolute path strings
6. ✅ Does the forward-slash absolute path work on Windows? → Yes, user-confirmed in fresh-session dogfood

## Closure

- Disposition: Completed
- Closed: 2026-07-17
- Focused installer suite: 5 passed, 0 failures.
- Repository health: 159 passed, 0 failures; one unrelated Antigravity warning.
- Live verification: user-confirmed dogfood passed from an unrelated workspace without read-confirmation prompts.
- Deferred work: None.
- Retrospective: `retrospectives/inbox/2026-07-17-validate-configuration-keys-against-schema.md` captures the false-positive configuration-validation lesson at user-wide scope.
