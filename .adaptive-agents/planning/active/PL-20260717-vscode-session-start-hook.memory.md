# PL-20260717-vscode-session-start-hook — Working Memory

- Work Unit: PL-20260717-vscode-session-start-hook
- Activated: 2026-07-17
- Status: Active — Complete, Closure Approval Pending

## Trigger

Multi-host dogfood showed that clear first-response instructions are not a deterministic startup mechanism. The agent answered before running `session-start.sh`, then later quoted and acknowledged the instruction.

## Verified Platform Evidence

| Evidence | Finding |
| --- | --- |
| VS Code version after update | `1.129.0`, commit `125df4672b8a6a34975303c6b0baa124e560a4f7` |
| Bundled Copilot version | `0.57.0` |
| VS Code core | Registers `chat.hookFilesLocations`, `chat.useHooks`, and personal hook discovery at `~/.copilot/hooks`. |
| Copilot runtime | Executes `SessionStart` through the hook service before handling the request. |
| Hook output | `hookSpecificOutput.additionalContext` is added to the model conversation. |
| Current user state | `~/.copilot/hooks` does not exist on this host. |
| Prior local version | VS Code `1.128.0` did not expose the same hook configuration surface. |
| Route-manifest report | Full-profile reporting passes after adding this active work-unit memory path to `adaptive_agents_planned_change`. |
| Live migration | VS Code 1.129.0 installed `~/.copilot/hooks/adaptive-agents.json`; independent validation confirms the hook, read grant, and legacy-artifact removal. |
| Context payload | Direct launcher execution injects the canonical repository path and eight files from `non_trivial_coding`; silent probes add no dynamic section. |
| Fresh-session dogfood failures | `/bin/bash` could open neither the Windows `C:/...` path nor the Git Bash `/c/...` path in the hook runtime. Resolving a generic `bash` command is not a stable Windows integration contract. |
| Python-first hook | The hook invokes `vscode-session-start.py` directly with the selected Python launcher. The adapter locates Git for Windows Bash from `git.exe` only for existing shell probes. |
| Corrected live hook | Installer regression executes the exact stored direct-Python command; focused adapter and independent health tests pass pending fresh-session lifecycle confirmation. |
| Dogfood observability | Successful adapter completion atomically writes `~/.cache/adaptive-agents/vscode-session-start-status.json`; invocation start removes stale markers so absence indicates the latest attempt did not complete. |
| Fresh-session lifecycle proof | A new VS Code chat wrote a success marker at `2026-07-17T09:57:35.007195Z` with eight files loaded and no dynamic output. AC8 passes. |

## Sources

- <https://code.visualstudio.com/docs/copilot/customization/hooks>
- <https://code.visualstudio.com/docs/agents/reference/hooks-reference>
- Installed VS Code 1.129.0 core and bundled Copilot runtime.
- Prior closed work: [SDD](../closed/PL-20260717-session-start-upgrade-check/PL-20260717-session-start-upgrade-check.sdd.md) and [memory](../closed/PL-20260717-session-start-upgrade-check/PL-20260717-session-start-upgrade-check.memory.md).

## Decisions

| Date | Decision | Rationale |
| --- | --- | --- |
| 2026-07-17 | Plan a user-level `SessionStart` hook | Hooks provide deterministic lifecycle execution; instructions do not. |
| 2026-07-17 | Minimum supported version is VS Code 1.129.0 | This is the first locally verified stable build exposing the required hook surface. |
| 2026-07-17 | Treat VS Code 1.129.0 as a hard integration prerequisite | A legacy VS Code fallback would retain the fragile implementation this work removes. |
| 2026-07-17 | Preserve first-response guidance only for other tools | Cross-tool guidance remains canonical, but supported VS Code uses hook-injected context exclusively. |
| 2026-07-17 | Use default `~/.copilot/hooks` discovery | Avoid unnecessary user-settings mutation and keep ownership narrow. |
| 2026-07-17 | Expand from hook addition to VS Code integration simplification | Deterministic context injection can replace the generated bootstrap, registration, model-invoked terminal command, and exact terminal approval. |
| 2026-07-17 | Use `instruction-load-routes.json` as the startup-content source | Reuses the reviewed route and budget model instead of creating another list of files that can drift. |
| 2026-07-17 | Inject the resolved `non_trivial_coding` profile | Ensures canonical operating and engineering guidance is actually present before the first response; task-specific context remains deferred. |
| 2026-07-17 | Retain only the repository read grant as distinct VS Code settings state | Later routed reads still need external access; generated instruction registration and terminal approval become redundant. |

## Constraints

- Do not update VS Code automatically.
- Do not overwrite or merge unrelated user hook files.
- Do not mutate or claim successful VS Code integration on unsupported or unknown versions.
- Do not authorize upgrade mutations through the startup hook.
- Do not remove legacy artifacts until the replacement hook is written and validated.
- Do not unset generic instruction booleans whose ownership cannot be proven.
- Do not close the work unit until a fresh VS Code session proves lifecycle ordering and the user approves closure.

## Next Step

Request user approval to close the completed work unit.
