# Scripts

This tree contains executable setup, validation, installation and maintenance
tools. Start with the area below rather than scanning every implementation and
test. Keep procedural guidance in [playbooks](../playbooks/INDEX.md).

## Areas

| Area | Contents |
|---|---|
| [Codex](codex/INDEX.md) | Configuration helpers, managed Total Recall runtime, dogfood tools and [Codex tests](codex/tests/INDEX.md). |
| [VS Code](vscode/INDEX.md) | SessionStart implementation, integration validation and [VS Code tests](vscode/tests/INDEX.md). |
| [Markdown Browser](browser/INDEX.md) | System-owned browser server and generator. |
| [Repository tests](tests/INDEX.md) | Shared validation, installer and script-layout regression tests. |
| [Session startup](session-start/) | Existing focused startup probes. |

## Stable Root Commands

- [install.sh](install.sh) detects supported integrations; the tool-specific
  `install-*.sh` commands retain their existing paths.
- [check-adaptive-agents.sh](check-adaptive-agents.sh) runs repository health
  checks and the relocated regression suites.
- [check-instruction-load-budget.sh](check-instruction-load-budget.sh) and
  [its Python implementation](check-instruction-load-budget.py) validate required
  instruction loading.
- [session-start.sh](session-start.sh) remains the lifecycle entrypoint.
- [ui.py](ui.py) launches the browser, including from unrelated projects.
- [vscode-session-start.py](vscode-session-start.py) and
  [check-vscode-integration.py](check-vscode-integration.py) preserve existing
  installed hook and health-check commands.
- [bootstrap-project-layer.sh](bootstrap-project-layer.sh),
  [inspect-project-layer-upgrade.sh](inspect-project-layer-upgrade.sh) and
  [migrate-project-layer-retrospectives.sh](migrate-project-layer-retrospectives.sh)
  retain their repository-maintenance interfaces.

The three root test commands documented in the public README remain small
forwarders: [OpenCode](test-opencode.sh), [Antigravity](test-install-antigravity.sh)
and [Project Layer](test-project-layer.sh). Other tests use their area paths.
[markdown_browser.py](markdown_browser.py) is an import bridge for older Project
Layer browser launchers, not a second server implementation.
