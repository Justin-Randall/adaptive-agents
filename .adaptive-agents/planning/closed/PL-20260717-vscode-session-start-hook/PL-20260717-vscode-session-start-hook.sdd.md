# PL-20260717: Deterministic and Simplified VS Code Integration

- Status: Completed
- Work Unit: PL-20260717-vscode-session-start-hook
- Origin: Direct
- Activated: 2026-07-17
- Memory: [PL-20260717-vscode-session-start-hook.memory.md](PL-20260717-vscode-session-start-hook.memory.md)
- Prior work: [Session-Start Adaptive Agents Upgrade Check](../PL-20260717-session-start-upgrade-check/PL-20260717-session-start-upgrade-check.sdd.md) ([memory](../PL-20260717-session-start-upgrade-check/PL-20260717-session-start-upgrade-check.memory.md))

## Objective

Replace the layered, best-effort VS Code bootstrap with one deterministic user-level `SessionStart` hook that injects the canonical Adaptive Agents startup context before the model responds. Establish VS Code 1.129.0 as the minimum supported version, remove installer-owned legacy bootstrap artifacts, and retain only configuration that serves a distinct runtime purpose.

## Specifications

### Problem Spec

Multi-host dogfood disproved the reliability claim of the prior implementation: an agent received a clear instruction to run `session-start.sh` before its first response but answered first anyway. It later quoted and understood the instruction, showing that stronger wording cannot guarantee execution.

The current VS Code integration has accumulated overlapping mechanisms:

1. A generated, machine-path-specific `vscode/user-wide.instructions.md` file.
2. `chat.instructionsFilesLocations` registration for that generated file.
3. `chat.includeApplyingInstructions` and `chat.includeReferencedInstructions` mutations intended to make its references fan out.
4. A first-response instruction asking the model to run `session-start.sh`.
5. An exact terminal auto-approval allowing that model-initiated command.
6. `additionalReadAccessPaths`, which independently grants later routed file reads.

The first five mechanisms exist to coax the model into loading and acting on startup context, yet remain probabilistic. They also create path migration, settings ownership, duplicate execution, and test complexity. Only the external read grant has a separate continuing purpose after startup.

VS Code 1.129 introduces agent hooks that execute code at lifecycle points with guaranteed outcomes. The `SessionStart` event runs when a new agent session begins and can inject `hookSpecificOutput.additionalContext` before the model handles the request. VS Code 1.129 discovers personal hooks from `~/.copilot/hooks`.

### Feature Spec

#### 1. Supported-version boundary and upgrade advisory

`scripts/install-vscode.sh` shall detect the selected VS Code flavor's installed version before installing hook integration.

- Minimum deterministic-hook version: `1.129.0`.
- Parse semantic versions numerically rather than lexicographically.
- Support the installer's existing `code`, `insiders`, and `codium` flavors using their corresponding CLI when available.
- When the version is `1.129.0` or newer, install the deterministic integration.
- When the version is older, stop before mutating VS Code integration state and print a prominent advisory that Adaptive Agents requires VS Code 1.129.0 or newer and that the user should update.
- When the version cannot be determined, stop before mutation and print the minimum required version plus a flavor-specific verification command. Do not claim installation succeeded.
- `--dry-run` shall report the detected capability and whether the hook would be installed, skipped, or requires an update.
- The installer remains non-interactive and must not update VS Code itself.

The umbrella installer shall continue installing other detected tools, report the unsupported VS Code integration in its final summary, and return a failure status if any requested integration was not installed. This avoids both silent partial success and one unsupported tool blocking unrelated installers.

#### 2. Deterministic startup-context assembly

The hook adapter shall inject file contents, not instructions asking the model to read files.

- Resolve the `non_trivial_coding` profile from `instruction-load-routes.json`, including inherited profiles, in declared order with path deduplication.
- Read each resolved canonical file from the Adaptive Agents repository and include explicit source boundaries in the injected context.
- Append non-empty output from `scripts/session-start.sh` after the static startup context.
- State in injected context that Adaptive Agents startup has already run so the model does not invoke the instruction fallback again.
- Fail visibly if the manifest is malformed, a required file is missing, or the resolved payload exceeds its declared instruction-load budget.
- Keep the route manifest as the single source of truth for both runtime startup content and instruction-load budget validation; do not create a second startup-file list in the installer or adapter.

This deterministically supplies `AGENTS.md`, `INDEX.md`, `instructions/global.instructions.md`, and the global instruction files inherited by `non_trivial_coding`. Task-specific skills and Project Layer context remain routed and loaded only when relevant.

#### 3. User-level hook installation

For supported versions, install one narrowly owned hook configuration under `~/.copilot/hooks/` using a filename unique to Adaptive Agents. The hook shall:

- register exactly one `SessionStart` command;
- invoke an Adaptive Agents-owned adapter using the canonical repository path;
- work from unrelated repositories and arbitrary current working directories;
- preserve unrelated user hook files and hook entries;
- migrate only prior installer-generated Adaptive Agents hook artifacts identified by a narrow signature;
- be byte-stable on same-version reruns;
- be disclosed in installer output and README security/trust documentation.

The default `~/.copilot/hooks` discovery path should be used directly. Do not modify `chat.hookFilesLocations` unless validation proves the default discovery path is unavailable.

#### 4. Hook output adapter

Add a narrow adapter between VS Code's hook protocol and `scripts/session-start.sh`.

- Consume the hook event JSON from stdin without interpreting user-controlled fields as shell code.
- Run the canonical `scripts/session-start.sh` exactly once.
- Always return the resolved static startup context as `hookSpecificOutput.additionalContext` with `hookEventName: "SessionStart"`.
- Append dynamic runner output only when non-empty.
- Preserve the runner's structured sections, including `--- PROMPT`, `--- CHANGELOG`, `--- ON APPROVE`, and `--- PROBE FAILURE`.
- A hook/adapter failure must be visible through valid hook output or a nonzero exit; it must not silently claim success.
- Upgrade mutation remains prohibited until the user explicitly approves instructions under `--- ON APPROVE`.

#### 5. Legacy-artifact migration and settings ownership

After the new hook is written and structurally validated, the supported-version installer shall remove only Adaptive Agents-owned legacy artifacts:

- remove the exact generated `vscode/` entry from `chat.instructionsFilesLocations` while preserving all unrelated entries;
- remove exact installer-generated session-start terminal approval rules while preserving unrelated allow and deny rules;
- stop generating and remove `vscode/user-wide.instructions.md` from the repository/integration;
- remove the now-empty `vscode/` directory from the checked-in product surface;
- stop setting `chat.includeApplyingInstructions` and `chat.includeReferencedInstructions`.

Because ownership of the two generic boolean settings cannot be reconstructed, migration shall preserve their current values rather than unset them. Documentation and health checks shall no longer require them.

Retain `github.copilot.chat.additionalReadAccessPaths` with the canonical repository root. The hook supplies startup context, but later routed workflows still need read access to task-specific files outside the current workspace. Continue removing the obsolete installer-owned `additionalReadAccessFolders` key.

The canonical `global.instructions.md` first-response rule remains cross-tool guidance for integrations without deterministic lifecycle hooks. It is no longer part of VS Code's installed bootstrap path, and hook context explicitly marks startup complete to prevent duplicate execution.

Migration order is transactional at the behavior level: write and validate the new hook first, update the required read grant second, and only then remove legacy VS Code bootstrap artifacts. A failure before hook validation must leave the prior integration intact.

#### 6. Health validation

Extend `scripts/check-adaptive-agents.sh` to distinguish:

- supported VS Code with a valid Adaptive Agents `SessionStart` hook and repository read grant;
- supported VS Code with a missing, malformed, or stale-path hook;
- supported VS Code with installer-owned legacy artifacts still present;
- older or unknown VS Code versions requiring an update before installation can be verified;
- `chat.useHooks: false`, which must be reported as an explicit integration blocker rather than overwritten.

### Interface / Contract Spec

Expected hook shape:

```json
{
 "hooks": {
  "SessionStart": [
   {
    "type": "command",
    "command": "<platform-safe command invoking the Adaptive Agents hook adapter>",
    "timeout": 30
   }
  ]
 }
}
```

Expected adapter output when dynamic startup instructions exist:

```json
{
 "hookSpecificOutput": {
  "hookEventName": "SessionStart",
    "additionalContext": "Adaptive Agents session startup has already run. The canonical startup files below are authoritative for this conversation; do not run startup again.\n\n--- FILE: AGENTS.md ---\n...\n\n--- FILE: INDEX.md ---\n...\n\n--- DYNAMIC STARTUP OUTPUT ---\n--- PROMPT\n..."
 }
}
```

### Behavioral Spec

| Case | Expected behavior |
| --- | --- |
| VS Code 1.129.0+ | Install and validate the user-level `SessionStart` hook. |
| VS Code below 1.129.0 | Make no VS Code integration mutation, fail that integration clearly, and advise updating. |
| Version unavailable or malformed | Make no VS Code integration mutation and fail with a verification command. |
| Existing unrelated personal hooks | Preserve them byte-for-byte. |
| Repository path contains spaces or regex/shell metacharacters | Generated command invokes the exact canonical adapter path safely. |
| Session runner emits nothing | Hook injects static manifest-resolved startup context without a dynamic-output section. |
| Session runner reports an available upgrade | Context reaches the model before its first response; mutation still waits for user approval. |
| Adapter or probe fails | Failure is surfaced and does not become a false successful startup claim. |
| Installer rerun | No duplicate hooks or configuration churn. |
| Existing generated bootstrap and exact terminal approval | Remove them only after validating the replacement hook. |
| Existing generic chat instruction settings | Stop managing them but preserve their values. |
| `chat.useHooks` is explicitly false | Do not override; report that hooks must be enabled for Adaptive Agents. |

## Applicable Guidance

- `instructions/coding.instructions.md` — checks must be independently falsifiable and installer behavior must preserve user configuration.
- `instructions/tdd.instructions.md` — add focused failing tests before production behavior changes.
- `skills/update-adaptive-agents/SKILL.md` — installer and durable-guidance changes require the Adaptive Agents update workflow.
- `.adaptive-agents/skills/manage-planning/SKILL.md` — this active plan is authoritative and implementation requires separate user approval.
- Official VS Code agent hooks and hooks-reference documentation — authoritative lifecycle and JSON protocol contract.

## Scope

1. Establish VS Code 1.129.0 as the minimum supported integration version with actionable preflight failures.
2. Resolve the existing instruction-load route manifest into deterministic startup context.
3. Add an Adaptive Agents-owned user `SessionStart` hook and protocol adapter.
4. Remove the generated VS Code bootstrap, its registration, and its exact terminal approval after successful hook migration.
5. Retain only the external repository read grant and settings with independent user-owned purposes.
6. Extend isolated installer, adapter, umbrella-installer, and repository-health validation.
7. Update README, playbooks, skills, and integration-contract documentation that describe the retired bootstrap.
8. Install and dogfood on a supported VS Code host, including migration from the current installation.

## Out of Scope

- Automatically updating VS Code.
- Removing the cross-tool startup instruction from canonical global guidance.
- Installing workspace-owned `.github/hooks` files into unrelated repositories.
- Auto-approving upgrade mutation.
- Implementing hooks for non-VS Code integrations in this work unit.
- Deterministically loading task-specific skills or arbitrary Project Layer files before their relevance is known.

## Acceptance Criteria

| # | Criterion | Verification |
| --- | --- | --- |
| AC1 | Installer detects VS Code versions numerically with minimum `1.129.0`. | Isolated tests cover below, equal, above, prerelease/extra-text, malformed, and missing version output. |
| AC2 | Older or unknown versions receive a clear update advisory and no partial VS Code mutation. | Captured installer output names the installed/unknown version, required version, verification command, and failed integration status. |
| AC3 | Supported versions install exactly one narrowly owned personal `SessionStart` hook. | Temp-home installer test validates hook path and structured JSON. |
| AC4 | Existing hooks and unrelated configuration survive installation and reruns are byte-stable. | Migration, preservation, idempotence, and dry-run tests pass. |
| AC5 | Adapter resolves the `non_trivial_coding` route and injects every declared canonical file exactly once. | Focused tests cover inheritance, order, deduplication, missing files, malformed manifests, and budget overflow. |
| AC6 | Hook context prevents duplicate startup and preserves explicit upgrade approval. | Injected context says startup already ran; `--- ON APPROVE` remains unchanged and no mutation runs automatically. |
| AC7 | Supported-version migration removes only installer-owned bootstrap cruft after hook validation. | Tests prove generated file/registration/exact approval removal and unrelated setting/rule preservation. |
| AC8 | Fresh supported-host session executes startup before the first response. | Agent debug hook logs and user-observed behavior confirm `SessionStart` ran without relying on model compliance. |
| AC9 | Health check accurately reports valid hooks, stale/malformed hooks, disabled hooks, legacy residue, read-grant drift, and unsupported versions. | Isolated fixtures plus live supported-host validation pass. |
| AC10 | Documentation and routing contain no active claims that VS Code uses the retired generated-bootstrap path. | Repository search plus README/playbook/skill review. |
| AC11 | Umbrella installation continues other tool installers but returns failure when VS Code is unsupported. | Focused umbrella-installer test covers mixed supported/unsupported tool outcomes. |

## Implementation Plan

1. Reconcile the active-memory route invariant so `check-instruction-load-budget.py --report` validates every profile before the manifest becomes a runtime dependency.
2. Add red tests for version preflight and aggregate umbrella-installer failure behavior.
3. Add adapter tests for route resolution, content boundaries, dynamic output, protocol encoding, and failures.
4. Implement the deterministic context adapter against `instruction-load-routes.json`.
5. Add hook generation and transactional legacy migration to `install-vscode.sh`.
6. Rewrite installer tests around the new ownership matrix, including removal of legacy positive assertions.
7. Extend health validation and remove active documentation for the retired path.
8. Run focused tests, shell syntax checks, instruction-load budget checks, Project Layer validation, and repository health checks.
9. Install on VS Code 1.129.0+, inspect migration of the current profile, and dogfood from fresh unrelated workspaces using hook logs as deterministic evidence.

## Decisions

- Use user-level `~/.copilot/hooks`, not workspace hooks, because Adaptive Agents is user-wide guidance.
- Require VS Code `1.129.0+` for deterministic hook installation.
- Treat older/unknown VS Code as unsupported and avoid maintaining a second VS Code bootstrap implementation.
- Use `instruction-load-routes.json` as the runtime and validation source of truth for startup files.
- Resolve and inject the `non_trivial_coding` profile on every VS Code session; defer task-specific and Project Layer context.
- Do not modify `chat.hookFilesLocations` when the default personal hook location is available.
- Preserve `additionalReadAccessPaths`; remove only installer-owned bootstrap registration and terminal approval.
- Stop managing generic instruction booleans but preserve existing values because ownership is ambiguous.
- Keep upgrade mutation separately gated by explicit user approval.
- Production implementation was approved on 2026-07-17 and is complete pending fresh-session dogfood and closure approval.

## Verification

Implementation verification:

- `py -3 scripts/test-instruction-load-budget.py`: 31 passed.
- `py -3 scripts/test-vscode-session-start.py`: 8 passed.
- `py -3 scripts/test-vscode-integration.py`: 5 passed.
- `bash scripts/test-install-vscode.sh`: 14 passed, 0 failures.
- `bash scripts/test-install.sh`: aggregate failure behavior passed.
- Claude Code installer: 10 passed, 0 failures.
- OpenCode installer: 16 passed, 0 failures.
- Antigravity installer: 13 passed, 0 failures.
- `py -3 scripts/check-instruction-load-budget.py --check`: passed after refreshing the intentional `INDEX.md` baseline change.
- `py -3 scripts/check-instruction-load-budget.py --report`: passed for all profiles after adding the active work-unit memory route.
- `bash scripts/test-project-layer.sh`: 14 passed, 0 failures.
- Shell syntax checks passed for all changed shell entrypoints.
- `bash scripts/check-adaptive-agents.sh`: 173 passed, 0 failures, 1 existing Antigravity permission-dialog warning.
- Live VS Code 1.129.0 installation succeeded; independent validation found a valid hook and read grant, no legacy registration, and no legacy terminal approval. Generic instruction booleans remained unchanged.
- Direct launcher protocol check returned `SessionStart`, the canonical repository path, eight routed files, and no dynamic section when probes were silent.
- Two fresh-session dogfood attempts failed before the first response because the hook command invoked ambiguous `bash`: `C:/...` was not a Bash executable path, while `/c/...` was unavailable to the resolved `/bin/bash` environment.
- The hook now invokes `vscode-session-start.py` directly with the selected Python launcher. On Windows, the adapter resolves probe execution from Git for Windows' installed `git.exe` rather than an ambiguous `bash` on `PATH`.
- Installer regression executes the exact stored direct-Python command; focused adapter and independent health tests pass. A new fresh-session lifecycle check remains pending.
- Successful hook execution now atomically writes `~/.cache/adaptive-agents/vscode-session-start-status.json` after probes and context assembly complete; each attempt removes stale evidence first.
- Fresh-session lifecycle dogfood passed: a new VS Code chat produced `vscode-session-start-status.json` at `2026-07-17T09:57:35.007195Z` with `filesLoaded: 8` and `dynamicOutput: false`, proving startup completed despite silent probes.
- Remote-system dogfood passed after installing from `origin/main`, confirming the full clone/install/fresh-session workflow.
- All acceptance criteria are satisfied. The user approved closure on 2026-07-17.
