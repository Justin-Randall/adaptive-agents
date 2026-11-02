# Repository Script Tests

Application-specific suites live under [Codex](../codex/tests/INDEX.md) and
[VS Code](../vscode/tests/INDEX.md).

- [test-script-layout.py](test-script-layout.py): grouped implementations/tests,
  public Python entrypoints outside the checkout, legacy browser import and
  canonical-root discovery.
- [test-instruction-load-budget.py](test-instruction-load-budget.py): required-read
  route and budget regressions.
- [test-project-layer.sh](test-project-layer.sh): Project Layer validator fixtures.
- [test-install.sh](test-install.sh): integration auto-detection/dispatch.
- [test-install-claude-code.sh](test-install-claude-code.sh): Claude Code installer.
- [test-install-antigravity.sh](test-install-antigravity.sh): Antigravity installer.
- [test-opencode.sh](test-opencode.sh): OpenCode installer/configuration.

Python suites run directly with Python; shell suites use Bash. Public README
commands for Project Layer, Antigravity and OpenCode remain root forwarders.
