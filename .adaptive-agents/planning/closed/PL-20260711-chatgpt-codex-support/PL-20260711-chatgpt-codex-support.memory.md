# PL-20260711-chatgpt-codex-support Memory

## Verified Context

- The active target is one local ChatGPT Codex integration across the desktop app, CLI, and IDE extension; the user is currently using the Windows desktop app.
- Codex global instruction discovery uses `AGENTS.md` under `CODEX_HOME` (default `~/.codex`); a global `AGENTS.override.md` takes precedence. Windows desktop app and native CLI default to `%USERPROFILE%\\.codex`; WSL uses its Linux home unless explicitly configured to share `CODEX_HOME`.
- Local app, CLI, and IDE agent configuration is shared. The installer and isolated suite were exercised with Windows Git Bash and native Python; Linux/WSL platform behavior remains covered by CI rather than local runtime validation.
- User-level `config.toml` controls sandbox/permission configuration. Workspace-write roots and named filesystem permission profiles are documented; the active permission mode/profile must be checked before choosing a merge.
- Project trust determines whether trusted project `.codex/config.toml` settings load. It is not a read/write grant for the Adaptive Agents repository.
- Official sources reviewed: [Codex configuration](https://learn.chatgpt.com/docs/developer-settings), [Windows desktop app](https://learn.chatgpt.com/docs/app/windows), [Codex AGENTS.md discovery](https://learn.chatgpt.com/docs/agent-configuration/agents-md), and [Codex permissions](https://learn.chatgpt.com/docs/permissions).

## Validation Environment

- Runtime probe: native Windows `codex-cli 0.164.0-alpha.11.1`; `codex debug prompt-input` loaded a unique marker through a symlinked global `AGENTS.md`.
- Automated installer suite: Windows Git for Windows Bash with Python 3.14; CI targets Python 3.11 on Ubuntu and Windows. WSL uses the Linux home default but has not been run directly.
- Permission test mode: isolated fixture uses `sandbox_mode = "workspace-write"` by Codex default (omitted) and preserves `approval_policy = "on-request"`. The focused suite never reads or changes live user config. The first repository health-check run used the auto-detected real `CODEX_HOME` and read its config without changing it; that exposed a missing Adaptive Agents integration. The completed health-check run used an isolated Codex home.
- The Windows desktop app's fresh-session and write-back dogfood remains owner-run.
- On this Windows host, Git Bash `ln -s` produced a regular file in the isolated test environment; Python's native `os.symlink` created a real symlink and is used by the Windows installer path.

## Decisions and Constraints

- Do not split the local integration into separate desktop, CLI, or IDE installers unless runtime evidence disproves shared configuration behavior.
- Do not use a prose pointer as proof that canonical `AGENTS.md` content is loaded. A Windows native Codex CLI runtime probe confirmed that a `CODEX_HOME/AGENTS.md` symlink loads the target content through `codex debug prompt-input`; the local desktop app shares this configuration and still needs owner-run fresh-session dogfooding.
- Preserve existing user instructions, sandbox mode, approval policy, custom profiles, and unrelated `config.toml` values.
- Automated tests must use isolated temp configuration and must not access real user Codex configuration.
- The repository owner will run live dogfood in a fresh Windows desktop app session from an unrelated project and verify a content proof plus a routed write-back, not just the sentinel. Automated validation must never use the real user Codex home.

## Restart Context

- [Closed plan](PL-20260711-chatgpt-codex-support.sdd.md) records the implementation and its remaining verification caveats. The owner reported the integration active in the Windows desktop app; routed write-back and CI remain unverified in the record.
- [Source backlog item](PL-20260711-chatgpt-codex-support.backlog.md) is preserved in this closed packet.
