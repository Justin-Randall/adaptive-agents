# PL-20260717: Session-Start Adaptive Agents Upgrade Check

- Status: Closed — Completed (2026-07-17)
- Work Unit: PL-20260717-session-start-upgrade-check
- Origin: Direct
- Activated: 2026-07-17
- Closed: 2026-07-17
- Memory: [PL-20260717-session-start-upgrade-check.memory.md](PL-20260717-session-start-upgrade-check.memory.md)

## Objective

Before the first response in a session, check whether the Adaptive Agents repository has new commits upstream using git. If a newer version is available, ask the user whether to upgrade. Upgrade means: pull the latest code, run the applicable installer shell scripts to update tool integrations, then re-read the entry point so the updated guidance takes effect in the current session.

## Specifications

### Problem Spec

The Adaptive Agents repository is updated independently of any single session. When new instructions, skills, playbooks, or installer improvements are committed, currently-active sessions have no awareness of the update. The user must manually pull, re-run installers, and restart sessions to benefit from changes. This means:

- **Stale guidance**: A long-lived session may operate against an older version of the repository even when fixes exist.
- **Missed installer improvements**: When an installer script changes (e.g., the VS Code `additionalReadAccessPaths` fix), users must be told to re-run it.
- **Manual friction**: Users need to remember to pull and re-run installers; there is no systematic prompt.

### Feature Spec

#### 1. Repo root discovery

The agent is typically not inside the Adaptive Agents repository directory. The repo root must be discovered from the loaded session context. At session start (or the first user-facing opportunity), the agent shall determine the repo root by checking these sources in order:

1. **Loaded instruction content** that explicitly declares the repo path (e.g., the bootstrap file in `vscode/user-wide.instructions.md` states "The user's canonical Adaptive Agents knowledgebase is located at: `C:/Users/.../adaptive-agents`").
2. **`@`-referenced paths** in loaded instructions — extract the common root directory from paths such as `@C:/Users/.../adaptive-agents/AGENTS.md`.
3. **Tool configuration** — e.g., VS Code `github.copilot.chat.additionalReadAccessPaths` setting, or `chat.instructionsFilesLocations` entries that point inside the repo.
4. **Fallback**: the current working directory if `AGENTS.md` is present at its root.

If none of these yield a valid path to a git repository containing `AGENTS.md`, skip the upgrade check silently for this session.

#### 2. Version comparison

Once the repo root is known:

1. Run `git -C "<repo-root>" fetch origin --prune` to update remote refs without merging local state.
2. Compare `HEAD` to `origin/main` using `git -C "<repo-root>" rev-list --count HEAD..origin/main`.
3. If the count is zero, the local copy is current — no further action.
4. If the count is non-zero, report the number of new commits and prompt the user.

#### 3. Refusal guard (deterministic, crash-safe)

When the user declines an upgrade for a specific version, the agent writes the remote HEAD commit hash to `~/.cache/adaptive-agents/refused-upgrade-hash`. The check script sees the hash still matches and exits silently. The user is automatically re-prompted only when the remote moves to a *different* commit — a new hash that does not match the refusal file.

No session concept is needed. No marker file cleanup is required. A crash leaves the refusal file intact — the next check still compares hashes correctly. When the user accepts an upgrade, local `HEAD` catches up to `origin/main` and the script exits cleanly regardless of the refusal file.

#### 4. User prompt

When new commits are detected, present a concise, single-choice prompt:

> The Adaptive Agents repository has N new commit(s) upstream. Upgrade now? This will pull latest code, re-run tool installers, and load updated guidance.

Options:

- **Yes / Upgrade** — proceed with pull, installer re-run, and re-read.
- **No / Skip** — write the remote HEAD hash to `~/.cache/adaptive-agents/refused-upgrade-hash` and skip. The script will not re-prompt for this version.
- **Show changelog** — show `git -C "<repo-root>" log --oneline HEAD..origin/main` before deciding.

#### 5. Upgrade action

If the user approves:

1. **Pull**: `git -C "<repo-root>" pull --ff-only origin main`. If the pull fails (local commits would require a merge), report the error and stop — the user has local changes that need manual resolution.
2. **Clear refusal file**: `rm -f ~/.cache/adaptive-agents/refused-upgrade-hash` (optional; local HEAD now matches origin/main so the check exits cleanly either way).
3. **Run umbrella installer**: `bash "<repo-root>/scripts/install.sh"`. This script already detects which tools are installed and runs the appropriate sub-installers for each. It is idempotent (backs up configs, merges surgically, byte-stable on rerun), so re-running is safe.
4. **Re-read the entry point**: After pulling and installing, read the updated `AGENTS.md` and `INDEX.md` (and any newly referenced files that have changed) into the current session context so the updated guidance takes effect immediately.

### Interface / Contract Spec

**`scripts/session-start.sh`** — the single entry point. Iterates over `scripts/session-start/*.sh`, runs each one in lexicographic order, and collects all stdout. Always exits 0. Empty stdout means nothing to do. Non-empty stdout becomes instructions in context.

**`scripts/session-start/check-upgrade.sh`** — the upgrade probe (moved from `scripts/check-upgrade.sh`). Runs as part of `session-start.sh`. Always exits 0.

Adding new startup probes: create a new `.sh` file in `scripts/session-start/`. No other files need changing.

**Output format:** sections delimited by `--- SECTION` headers. Each section contains natural-language instructions the model follows directly. No parsing or interpretation needed. Sections are:

| Section | Content |
| --- | --- |
| `--- PROMPT` | Say this verbatim to the user. |
| `--- CHANGELOG` | Show this if the user asks what changed. |
| `--- ON APPROVE` | Run these steps ONLY when the user approves. |

Example:

```text
--- PROMPT
The Adaptive Agents repository has 3 new commits. Ask the user if they would like to upgrade now.

--- CHANGELOG
If the user asks what has changed, show these recent commits:
  ad2e9a3 PL-20260717-session-start-upgrade-check: spec and memory
  f2055e4 promote independent-falsification verification rule
  686f653 PL-20260717-vscode-td-permissions: fix external read access

--- ON APPROVE
Run these steps ONLY when the user approves:
  1. git -C "<repo-root>" pull --ff-only origin main
  2. bash "<repo-root>/scripts/install.sh"
```

When the user declines, write the remote HEAD hash to `~/.cache/adaptive-agents/refused-upgrade-hash`.

**Refusal file:** `~/.cache/adaptive-agents/refused-upgrade-hash` — written by the agent when the user declines. The script reads it to avoid re-prompting for the same version. Never written by the script itself.

### Behavioral changes to session-start instructions in global.instructions.md

The generated VS Code bootstrap contains the resolved command and requires it before the first response, including trivial and sentinel requests. `global.instructions.md` repeats the canonical requirement. The script's output sections (`--- PROMPT`, `--- CHANGELOG`, `--- ON APPROVE`) are self-describing — the model interprets them naturally as part of its loaded guidance for that turn.

### Once-per-conversation enforcement

The agent runs `session-start.sh` at most once per conversation. The model remembers. New conversation = new check. Ongoing conversation = skip. No filesystem state needed for the guard.

### Integration mechanism

No native session-start hook exists in VS Code Copilot Chat (confirmed via upstream documentation). The integration uses the first-loaded generated bootstrap to require one `session-start.sh` invocation before the first response and treats non-empty output as instructions.

### Behavioral Spec

**Edge cases:**

| Case | Expected behavior |
| ---- | ---------------- |
| Cannot determine repo root (no path found in context) | Skip check silently. |
| No network / `git fetch` fails | Skip silently. |
| Already up to date | Skip silently. |
| Refusal file contains current remote hash | Skip silently (previously declined). |
| User declines now | Write remote HEAD hash to `~/.cache/adaptive-agents/refused-upgrade-hash`. No re-prompt for this version. |
| Remote advances to new commit | New hash does not match refusal file; prompt appears. |
| `git pull --ff-only` fails (local commits) | Report the error clearly, do not modify local state, suggest manual resolution. |
| First run — no `origin/main` | Compare against `origin` default branch from `git -C "<repo-root>" remote show origin` or skip gracefully. |
| Umbrella installer fails | Report the failure; the pull already succeeded so the repo is up to date, but tool configs may need manual re-installation. |
| Same conversation, already checked | Agent skips re-running the script (conversation-level awareness). |

**Idempotency and safety:**

- The check is read-only until the user approves the upgrade.
- Installing the VS Code integration adds a user/profile-scoped `chat.tools.terminal.autoApprove` rule for the exact command `bash "<repo-root>/scripts/session-start.sh"`. Installation consent includes this operational permission.
- The exact command approval trusts the startup runner and all probes under `scripts/session-start/`; it does not approve generic Bash commands.
- Terminal approval only permits the startup framework to run. It does not authorize `git pull`, installer reruns, or any other mutation described by `--- ON APPROVE`.
- The script's stdout is a proposal — the agent presents choices to the user and waits for approval before executing.
- The pull uses `--ff-only` so it never creates a merge commit or rewrites history.
- Each installer is designed to be idempotent (creates backups, merges config, byte-stable rerun).
- The re-read step is advisory — it loads the updated files into the current context but cannot guarantee every runtime behavior picks up changes. Document this limitation.

## Applicable Guidance

- `instructions/coding.instructions.md` — verification requires independent falsifiable checks; installer re-runs must be validated after upgrade.
- `instructions/command-failure-pivot.instructions.md` — git and installer failures may require pivot strategies.
- `playbooks/adaptation-cycle.md` — this feature itself should be dogfooded before promotion.

## Scope

1. ✅ **`scripts/session-start.sh`**: iterates `scripts/session-start/*.sh`, always exits 0. Empty stdout = nothing to do.
2. ✅ **`scripts/session-start/check-upgrade.sh`**: upgrade probe using `git fetch` + `rev-list --count` + refusal hash check.
3. ✅ **Refusal guard**: `~/.cache/adaptive-agents/refused-upgrade-hash` prevents re-prompting for the same version.
4. ✅ **Stdout as instructions**: script emits actionable instructions directly; no separate playbook loading by the agent.
5. ✅ **Testing**: manual dogfood confirmed update detection and proactive prompt-free startup from a fresh unrelated-workspace session.
6. ✅ **VS Code terminal approval**: installer persistently approves only the canonical session-start command line.

## Out of Scope

- Probes beyond upgrade check (future work units).
- Scheduled / background checks (session-start only).
- Auto-upgrade without user approval.
- Non-git update mechanisms (npm, submodules, etc.).
- Pushing local changes as part of upgrade.
- Session marker files — the hash refusal file is self-maintaining.
- The playbook as agent-loadable context (it is human documentation only).

## Acceptance Criteria

| # | Criterion | Verification |
| - | --------- | ------------ |
| AC1 | Session-start detection runs at most once. | Second check in same session is skipped. |
| AC2 | No network or not the Adaptive Agents repo → skip silently. | No user-visible message on non-repo or offline. |
| AC3 | Up-to-date repository → skip silently. | No prompt when `HEAD` matches `origin/main`. |
| AC4 | New commits detected → user is prompted with commit count. | Prompt includes count and Yes/No/Show changelog options. |
| AC5 | User approves → git pull runs, installers re-run, entry point re-read. | Pull succeeds, applicable installers report success, updated instructions are loaded into context. |
| AC6 | User declines → no more prompts this session. | Second trigger within same session does not prompt. |
| AC7 | Pull fails → error reported, local state unchanged. | No modified files from failed pull. |
| AC8 | Installer failure → reported but does not block other installers. | Other installers complete despite one failure. |
| AC9 | VS Code installation → canonical session-start command is persistently approved without broad shell approval. | User settings contain one anchored full-command rule with `matchCommandLine: true`; existing allow and deny rules remain intact. |
| AC10 | Fresh unrelated-workspace session → startup runs proactively without a terminal confirmation. | Before answering the first request, including trivial and sentinel requests, the canonical command executes once under Default Approvals while upgrade mutation still waits for explicit approval. |

## Decisions

- `scripts/session-start.sh` iterates over `scripts/session-start/*.sh`. Always exits 0. Empty stdout = nothing to do.
- `scripts/session-start/check-upgrade.sh` is the upgrade probe. New probes are new `.sh` files in the same directory.
- Stdout is treated as instructions when non-empty. Sections are self-describing (`--- PROMPT`, `--- CHANGELOG`, `--- ON APPROVE`).
- `git fetch` over `git pull` for detection to avoid accidental merge.
- `--ff-only` for pull to enforce no history rewriting.
- Refusal hash file at `~/.cache/adaptive-agents/refused-upgrade-hash` is crash-safe and self-maintaining.
- Once-per-conversation guard is in-memory (model remembers).
- Applicable installer detection uses existing integration artifacts rather than a new registry.
- `playbooks/session-start-upgrade-check.md` is human documentation only — the agent follows stdout instructions directly.
- Installing Adaptive Agents implies consent to the exact user/profile-scoped terminal rule required to operate its session-start framework; no separate opt-in is required.
- The canonical VS Code invocation is `bash "<repo-root>/scripts/session-start.sh"` and uses an anchored full-command approval with `matchCommandLine: true`.
- The approval trusts the runner and its probe directory but never substitutes for explicit approval of `--- ON APPROVE` mutations.
- The generated VS Code bootstrap repeats the resolved startup command directly because referenced guidance may not be loaded before an agent answers the first request.

## Verification

- `bash scripts/test-install-vscode.sh`: 14 passed, 0 failures. Covers exact full-command matching, proactive first-response bootstrap generation, suffix rejection, stale-rule migration, existing rule preservation, malformed settings, caller-CWD independence, and regex-special repository paths.
- `bash scripts/check-adaptive-agents.sh`: 168 passed, 0 failures, 1 existing Antigravity permission warning.
- `bash .adaptive-agents/scripts/check-project-layer.sh`: 0 failures.
- Real VS Code installation: exactly one canonical session-start rule added; all 10 pre-existing terminal approval rules remained unchanged.
- Fresh unrelated-workspace dogfood under Default Approvals: the agent ran the required bootstrap before answering the sentinel request, received empty output, and responded without a terminal confirmation or additional startup noise.
