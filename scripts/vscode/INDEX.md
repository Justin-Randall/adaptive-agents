# VS Code Scripts

The stable root commands are intentionally unchanged so existing installed hooks
continue to work without reinstalling.

- [session_start.py](session_start.py) implements the
  [SessionStart entrypoint](../vscode-session-start.py).
- [integration.py](integration.py) implements the
  [integration health checker](../check-vscode-integration.py).
- [install-vscode.sh](../install-vscode.sh) remains the public installer.
- [Tests](tests/INDEX.md) cover hook output/error propagation, settings and
  installer behavior.
