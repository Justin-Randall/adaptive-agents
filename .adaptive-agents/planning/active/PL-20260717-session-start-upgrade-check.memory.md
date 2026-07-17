# PL-20260717-session-start-upgrade-check — Working Memory

- Work Unit: PL-20260717-session-start-upgrade-check
- Activated: 2026-07-17
- Status: Active

## Starting State

No existing upgrade mechanism exists. Sessions never check for upstream changes. Users must manually pull, re-run installers, and restart sessions to receive updates.

## Key Decisions

| Date | Decision | Rationale |
| ---- | -------- | --------- |
| 2026-07-17 | Detection runs at session start, not on a timer | Session-start is a natural, low-frequency trigger. No polling or background work needed. |
| 2026-07-17 | Once-per-session guard is in-memory | A file or config key would persist across sessions incorrectly — each fresh session should check once. |
| 2026-07-17 | Detection uses `git -C <repo-root>` not `cd` | The agent is typically not in the repo directory; `-C` lets git operate on any repo from any working directory. |
| 2026-07-17 | Repo root discovered from loaded instruction context or tool config | Loaded instruction files declare the repo path explicitly; `@` references embed it; tool settings like `additionalReadAccessPaths` store it. |
| 2026-07-17 | `git pull --ff-only` for upgrade | Prevents merge commits and history rewrites; fails cleanly if local and upstream have diverged. |
| 2026-07-17 | Applicable installer detection uses existing integration signals | Avoids maintaining a separate registry that could become stale. |
| 2026-07-17 | Re-read entry point after upgrade | Loads updated guidance into current session context without requiring a full session restart. |

## Repository Layout (relevant files)

| File | Role |
| ---- | ---- |
| `scripts/install-vscode.sh` | VS Code / Copilot installer |
| `scripts/install-claude-code.sh` | Claude Code installer |
| `scripts/install-opencode.sh` | OpenCode installer |
| `scripts/install-antigravity.sh` | Antigravity 2.0 installer |

## Open Questions

1. How should the agent represent the once-per-session guard? A session variable, a context flag, or a note in working memory?
2. What is the exact re-read mechanism for each tool? For VS Code/Copilot: `read_file` on AGENTS.md, INDEX.md, and the applicable instructions files. For CLI tools: same approach via their read tool.
3. Should `git log --oneline` output be summarized or shown raw in the changelog prompt option?
4. How does the detection avoid being noisy in a multi-root workspace where the Adaptive Agents repo is not the primary workspace?

## Implementation Progress

| Phase | Status | Details |
| ----- | ------ | ------- |
| Spec | ✅ Complete | Full SDD in ACTIVE.md |
| Implementation | ✅ Complete | Playbook, global.instructions.md hook, and INDEX.md routing deployed. |
| Dogfood | ⬜ Pending | Requires a subsequent push to origin/main and a fresh session. |

## Deferred Discoveries

- None yet.
