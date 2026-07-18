# Scripts

This directory contains deterministic setup, validation, inspection, installation, and migration scripts for Adaptive Agents.

Scripts should be safe to run repeatedly when practical, report actionable failures, and avoid writing outside their documented target paths.

## Markdown Browser

- `ui.py` starts or generates the system-owned Markdown Browser.
- `markdown_browser.py` contains the HTTP server, Project Layer/System navigation, SSE, and watchdog implementation.
- Run `py -3 scripts/ui.py serve --target <project-root>` from this repository to browse any project that has a `.adaptive-agents` Project Layer.

Use this area for executable repository maintenance. Put procedural explanations in [playbooks](../playbooks/INDEX.md) and user-facing setup narrative in [README.md](../README.md).
