# PL-20260717: Session-Start Adaptive Agents Upgrade Check

- Status: Active
- Work Unit: PL-20260717-session-start-upgrade-check
- Origin: Direct
- Activated: 2026-07-17
- Memory: [PL-20260717-session-start-upgrade-check.memory.md](PL-20260717-session-start-upgrade-check.memory.md)

## Objective

When a session starts (or at the first opportunity after), check whether the Adaptive Agents repository has new commits upstream using git. If a newer version is available, ask the user whether to upgrade. Upgrade means: pull the latest code, run the applicable installer shell scripts to update tool integrations, then re-read the entry point so the updated guidance takes effect in the current session.

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

#### 3. Once-per-session guard

The upgrade check must run at most once per session. After the first check (regardless of outcome or user decision), suppress further checks for the remainder of the session. Use a session-level flag (variable or context note) rather than writing to disk.

#### 4. User prompt

When new commits are detected, present a concise, single-choice prompt:

> The Adaptive Agents repository has N new commit(s) upstream. Upgrade now? This will pull latest code, re-run tool installers, and load updated guidance.

Options:

- **Yes / Upgrade** — proceed with pull, installer re-run, and re-read.
- **No / Skip** — defer. Suppress further prompts for this session.
- **Show changelog** — show `git -C "<repo-root>" log --oneline HEAD..origin/main` before deciding.

#### 5. Upgrade action

If the user approves:

1. **Pull**: `git -C "<repo-root>" pull --ff-only origin main`. If the pull fails (local commits would require a merge), report the error and stop — the user has local changes that need manual resolution.
2. **Run umbrella installer**: `bash "<repo-root>/scripts/install.sh"`. This script already detects which tools are installed and runs the appropriate sub-installers for each. It is idempotent (backs up configs, merges surgically, byte-stable on rerun), so re-running is safe.
3. **Re-read the entry point**: After pulling and installing, read the updated `AGENTS.md` and `INDEX.md` (and any newly referenced files that have changed) into the current session context so the updated guidance takes effect immediately.

### Interface / Contract Spec

No new CLI or API surface for this feature. The upgrade workflow is invoked by the agent during session startup. The detection and upgrade steps use existing git commands and installer scripts.

### Behavioral Spec

**Edge cases:**

| Case | Expected behavior |
| ---- | ---------------- |
| Cannot determine repo root (no path found in context) | Skip check silently for this session. |
| No network / `git fetch` fails | Log the failure silently, suppress further checks for this session, continue normal startup. Do not prompt. |
| Already up to date | Skip silently. |
| User declines upgrade | Suppress further prompts for this session. |
| `git pull --ff-only` fails (local commits) | Report the error clearly, do not modify local state, suggest manual resolution. The user has local work that needs to be merged or stashed first. |
| First run — no `origin/main` | Compare against `origin` default branch from `git -C "<repo-root>" remote show origin` or skip gracefully. |
| Umbrella installer fails | Report the failure; the pull already succeeded so the repo is up to date, but tool configs may need manual re-installation. |
| Current session is already on the latest commit (user pulled manually) | Detection returns zero commits; no prompt. |

**Idempotency and safety:**

- The check is read-only until the user approves the upgrade.
- The pull uses `--ff-only` so it never creates a merge commit or rewrites history.
- Each installer is designed to be idempotent (creates backups, merges config, byte-stable rerun).
- The re-read step is advisory — it loads the updated files into the current context but cannot guarantee every runtime behavior picks up changes. Document this limitation.

## Applicable Guidance

- `instructions/coding.instructions.md` — verification requires independent falsifiable checks; installer re-runs must be validated after upgrade.
- `instructions/command-failure-pivot.instructions.md` — git and installer failures may require pivot strategies.
- `playbooks/adaptation-cycle.md` — this feature itself should be dogfooded before promotion.

## Scope

1. ✅ **Detection prompt**: git fetch, rev-list comparison, user prompt with show-changelog option.
2. ✅ **Upgrade execution**: git pull, umbrella installer re-run, re-read entry point.
3. ✅ **Once-per-session guard**: suppress repeated checks in the same session.
4. ✅ **Logging**: report outcomes (skipped, upgraded, declined, failed) for user awareness.
5. ⬜ **Testing**: manual dogfood from a session that detects new commits.

## Out of Scope

- Scheduled / background checks (session-start only).
- Auto-upgrade without user approval.
- Non-git update mechanisms (npm, submodules, etc.).
- Pushing local changes as part of upgrade.
- Updating the existing closed-work plan artifacts.

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

## Decisions

- Detection runs at session start, not on a timer. No background checking.
- `git fetch` over `git pull` for detection to avoid accidental merge.
- `--ff-only` for pull to enforce no history rewriting.
- Session guard is in-memory, not a file or config key.
- Applicable installer detection uses existing integration artifacts rather than a new registry.

## Verification

Not yet run.
