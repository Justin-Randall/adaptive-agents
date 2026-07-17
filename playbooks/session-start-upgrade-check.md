# Session-Start Upgrade Check

This playbook describes how the agent checks for Adaptive Agents repository updates at session start and upgrades the integration when a newer version is available.

## When to Use

Run `bash <repo-root>/scripts/check-upgrade.sh` once per conversation after loading guidance. If it exits 0 with an action line, read this playbook and carry out the upgrade. If it exits 1, nothing needs to be done — no further action for this conversation.

## Refusal guard

When the user declines an upgrade, the agent writes the remote HEAD commit hash to `~/.cache/adaptive-agents/refused-upgrade-hash`. The `check-upgrade.sh` script reads this file on future invocations: if the hash still matches, it exits silently. The user is automatically re-prompted only when the remote advances to a *different* commit.

No session concept, no marker cleanup, no model memory needed. Crash-safe by design — a crash leaves the refusal file intact and the next check compares hashes correctly. When the user accepts an upgrade, local `HEAD` catches up to `origin/main` and the script exits cleanly regardless.

## Procedure

### Step 1: Discover the repo root

The agent is typically not inside the Adaptive Agents directory. Determine the repo root by checking these sources in order:

1. **Loaded instruction content** — the user-wide bootstrap file (`vscode/user-wide.instructions.md`) explicitly states the repo path on line 6.
2. **`@`-referenced paths** in loaded instructions — extract the common directory root from paths such as `@<repo-root>/AGENTS.md`.
3. **Tool configuration** — VS Code `github.copilot.chat.additionalReadAccessPaths`, Claude Code `permissions.additionalDirectories`, or similar configured path in the current tool.
4. **Working directory fallback** — if `AGENTS.md` exists at the root of the current directory.

If none of these yield a valid path to a git repository containing `AGENTS.md` and `INDEX.md`, skip the check silently for this session.

### Step 2: Fetch remote refs

Run `git -C "<repo-root>" fetch origin --prune` to update remote refs without modifying local state.

- If the command fails (no network, no remote configured), skip the check silently.
- If the repo has no `origin/main`, try `git -C "<repo-root>" remote show origin` to detect the default branch, or skip.

### Step 3: Check refusal file

Before prompting, check `~/.cache/adaptive-agents/refused-upgrade-hash`. If it contains the current remote HEAD hash, skip silently — the user already declined this version.

### Step 5: Compare versions

Run `git -C "<repo-root>" rev-list --count HEAD..origin/main`.

- If the count is zero, the local copy is current. Take no further action.
- If the count is non-zero, continue to the prompt.

### Step 6: Report and prompt

The agent shall present the following to the user:

> The Adaptive Agents repository has N new commit(s) upstream. Upgrade now? This will pull latest code, re-run the umbrella installer, and load updated guidance.

Options:

- **Yes / Upgrade** — proceed to Step 7.
- **Show changelog** — run `git -C "<repo-root>" log --oneline HEAD..origin/main`, display the output, then re-prompt with the same choices.
- **No / Skip** — write the remote HEAD hash to `~/.cache/adaptive-agents/refused-upgrade-hash` and continue. The script will not prompt for this hash again.

### Step 7: Execute upgrade

If the user approves:

1. **Pull**: `git -C "<repo-root>" pull --ff-only origin main`. If the pull fails (local commits would create a merge), report the error with a suggestion for manual resolution and stop.
2. **Run umbrella installer**: `bash "<repo-root>/scripts/install.sh"`. This detects which tools are installed and runs the appropriate sub-installers. It is idempotent (backups existing config, merges surgically, byte-stable on rerun).
3. **Re-read entry point**: Read the updated `AGENTS.md` and `INDEX.md` (and any newly referenced files that have changed) into the current session context so the updated guidance takes effect.

### Step 8: Report outcome

Log the upgrade result to the user:

- **Upgraded**: N commits pulled, installers re-run, guidance re-read.
- **Declined**: Hash written to refusal file; will not re-prompt for this version.
- **Skipped**: No update needed or network unavailable.
- **Failed**: Pull failed (local changes) or installer failed (partial success reported).

## Edge Cases

| Case | Behavior |
| ---- | -------- |
| Cannot determine repo root | Skip silently. |
| `git fetch` fails (no network) | Skip silently. |
| Already up to date | Skip silently. |
| Refusal file matches current remote hash | Skip silently (previously declined). |
| User declines now | Write remote HEAD hash to `~/.cache/adaptive-agents/refused-upgrade-hash`. |
| Remote advances to new commit | New hash does not match refusal file; prompt appears. |
| `git pull --ff-only` fails (local commits) | Report error, suggest manual resolution, do not modify local state. |
| No `origin/main` | Detect default branch from remote or skip gracefully. |
| Umbrella installer fails | Report failure; the repo is up to date but tool configs may need manual attention. |

## Conversation guard

The agent runs this check at most once per conversation. No filesystem marker is used — the model remembers. New conversation = new check. Ongoing conversation = skip.
| No `origin/main` | Detect default branch from remote or skip gracefully. |
| Umbrella installer fails | Report failure; the repo is up to date but tool configs may need manual attention. |

## Once-Per-Session Guard

After this check completes (regardless of outcome), do not repeat the check for the remainder of the session. Use an in-memory session flag — do not write a file or persist the guard across sessions.
