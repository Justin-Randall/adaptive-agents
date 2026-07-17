# PL-20260717-session-start-upgrade-check — Working Memory

- Work Unit: PL-20260717-session-start-upgrade-check
- Activated: 2026-07-17
- Status: Closed — Completed (2026-07-17)

## Starting State

No existing upgrade mechanism exists. Sessions never check for upstream changes. Users must manually pull, re-run installers, and restart sessions to receive updates.

## Key Decisions

| Date | Decision | Rationale |
| ---- | -------- | --------- |
| 2026-07-17 | Detection runs at session start, not on a timer | Session-start is a natural, low-frequency trigger. No polling or background work needed. |
| 2026-07-17 | Refusal guard uses commit hash file at `~/.cache/adaptive-agents/refused-upgrade-hash` | Crash-safe, no session concept needed. Same hash = already declined. New hash = re-prompt. User's decline is persistent across restarts until the remote advances. |
| 2026-07-17 | Once-per-conversation enforcement is the agent's responsibility | No filesystem marker. The model remembers. Correct behavior: new conversation checks again, ongoing conversation does not. |
| 2026-07-17 | No native session-start hook in VS Code Copilot | Confirmed from upstream contribution-point docs. The only mechanism is agent instructions in `global.instructions.md`. |
| 2026-07-17 | Detection uses `git -C <repo-root>` not `cd` | The agent is typically not in the repo directory; `-C` lets git operate on any repo from any working directory. |
| 2026-07-17 | Repo root discovered from loaded instruction context or tool config | Loaded instruction files declare the repo path explicitly; `@` references embed it; tool settings like `additionalReadAccessPaths` store it. |
| 2026-07-17 | `git pull --ff-only` for upgrade | Prevents merge commits and history rewrites; fails cleanly if local and upstream have diverged. |
| 2026-07-17 | Umbrella `install.sh` re-run after pull | Detects installed tools and runs sub-installers idempotently. |
| 2026-07-17 | VS Code installation includes the exact session-start terminal approval | The user considers approval implied by "install Adaptive Agents." The installer writes one anchored, user/profile-scoped `chat.tools.terminal.autoApprove` rule with `matchCommandLine: true`. |
| 2026-07-17 | Terminal startup approval does not authorize upgrades | The exact rule permits only `bash "<repo-root>/scripts/session-start.sh"`; mutation emitted under `--- ON APPROVE` still requires explicit user approval. |
| 2026-07-17 | Session-start approval trusts the probe directory | The runner dispatches every script under `scripts/session-start/`, so installation documentation must disclose that current and future probes share the runner's approval. |
| 2026-07-17 | Repeat the exact startup command in the generated VS Code bootstrap | Dogfood showed an agent could answer sentinel requests before loading referenced `global.instructions.md`. The first-loaded bootstrap must require startup before the first response, including trivial requests. |

## Repository Layout (relevant files)

| File | Role |
| ---- | ---- |
| `scripts/install-vscode.sh` | VS Code / Copilot installer |
| `scripts/install-claude-code.sh` | Claude Code installer |
| `scripts/install-opencode.sh` | OpenCode installer |
| `scripts/install-antigravity.sh` | Antigravity 2.0 installer |

## Implementation Progress

| Phase | Status | Details |
| ----- | ------ | ------- |
| Spec | ✅ Complete | Full SDD in ACTIVE.md |
| Implementation | ✅ Complete | Playbook, global.instructions.md hook, and INDEX.md routing deployed. |
| Dogfood | ✅ Complete | Upgrade detection worked after fixing installer CWD dependence and executable modes. A fresh unrelated-workspace session then ran the bootstrap proactively before its sentinel response, without a terminal confirmation. |

## Research Evidence

- VS Code stores persistent per-command rules in the public `chat.tools.terminal.autoApprove` setting.
- Regex keys support object values with `approve` and `matchCommandLine`; full-line matching is appropriate for the canonical startup invocation.
- Existing "Always Allow" choices are persisted in user settings, confirming user/profile scope rather than extension-private workspace storage.
- Official references: <https://code.visualstudio.com/docs/agents/approvals> and <https://code.visualstudio.com/docs/agents/reference/ai-settings>.

## Multi-Host Dogfood

- 2026-07-17: Published a documentation-only marker commit to exercise remote update detection, approval, fast-forward pull, installer rerun, and guidance reload on another host.
