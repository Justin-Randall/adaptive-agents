# VS Code Tests

- [test-vscode-session-start.py](test-vscode-session-start.py) checks deterministic
  hook context, instruction budgets and explicit failures through the stable root
  entrypoint.
- [test-vscode-integration.py](test-vscode-integration.py) checks configuration
  validation through the stable root health checker.
- [test-install-vscode.sh](test-install-vscode.sh) invokes
  [test-install-vscode-hook.sh](test-install-vscode-hook.sh), covering fresh
  installation, migration, rerun, conflicts, dry-run and copied-checkout fixtures.

Use Python for the Python suites and Bash for the installer suite.
