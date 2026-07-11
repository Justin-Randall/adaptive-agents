# Backlog

Read this index before opening detailed plans or proposing a new item. Keep entries ordered by intended consideration priority.

> **Cross-tool integration contract from PL-20260711 (Claude Code)**: Verify each tool's official native loading syntax before designing the installer; prose that merely names an external file is not an import. Use one native entrypoint to load canonical AGENTS.md and route through INDEX.md. Handle external-path and trust boundaries explicitly, change only narrowly required access or discovery settings, preserve and deduplicate unrelated user configuration, and keep same-version reruns content-idempotent. Do not generate rule copies, hooks, or skill markers unless verified tool behavior requires them. Validate the exact destination and effective config, then dogfood from an unrelated repository for both `ADAPTIVE_AGENTS_GLOBAL_LOADED` and a routed workflow. Repeat fresh-session checks for integrations with flaky loading.

| ID | Plan | Outcome | Readiness |
| --- | --- | --- | --- |
| PL-20260711 | [OpenCode Installer Rework](PL-20260711-opencode-installer-rework.md) | Diagnose why AGENTS.md is not honored and redesign around OpenCode's verified native entrypoint behavior. | Ready |
| PL-20260711 | [Multi-Tool Agent Coding Support](PL-20260711-multi-tool-agent-support.md) | Umbrella tracker for supporting 8 major AI coding agent tools across Adaptive Agents — each with an idempotent installer. | Ready |
| PL-20260711 | [Claude Code Support](PL-20260711-claude-code-support.md) | Native CLAUDE.md import plus the narrow additional-directory access grant required for routed files. | Ready |
| PL-20260711 | [Codex CLI Support](PL-20260711-codex-cli-support.md) | Single-entrypoint installer: AGENTS.md with imperative load directive. No plugin manifests, chronicle seeding, or exec scripts — the repo is the source of truth. | Ready |
| PL-20260711 | [Cursor Support](PL-20260711-cursor-support.md) | Single-entrypoint installer: marker-delimited .cursorrules referencing repo AGENTS.md. No .cursor/rules/*.mdc file generation — fan-out handles it. | Ready |
| PL-20260711 | [Copilot Agent Mode Support](PL-20260711-copilot-agent-mode.md) | Update install-vscode.sh to generate .github/copilot-instructions.md with imperative AGENTS.md load directive. No settings.json changes beyond what existing installer already does. | Ready |
| PL-20260711 | [Cline Support](PL-20260711-cline-support.md) | Single-entrypoint installer: .clinerules referencing repo AGENTS.md. No .clineignore, skills/hooks mapping, or Kanban integration — fan-out from AGENTS.md handles everything. | Ready |
| PL-20260711 | [Antigravity Support](PL-20260711-antigravity-support.md) | Single-entrypoint installer: marker-delimited config file referencing repo AGENTS.md. No plugin manifests, slash commands, or hooks — fan-out handles it. | Ready |
| PL-20260711 | [Gemini CLI Support](PL-20260711-gemini-cli-support.md) | Single-entrypoint installer: GEMINI.md referencing repo AGENTS.md with imperative load directive. No slash commands or skills install — fan-out handles it. | Ready |
| PL-20260711 | [Windsurf Support](PL-20260711-windsurf-support.md) | Single-entrypoint installer: marker-delimited .windsurfrules referencing repo AGENTS.md. No separate rule files. | Ready |
| PL-20260710 | [Project Layer Web UI](PL-20260710-project-layer-web-ui.md) | A browsable, editable web interface that surfaces all Project Layer artifacts without requiring directory-tree navigation. | Ready |

Detailed plans use `PL-YYYYMMDD-descriptive-slug.md` (or legacy `PL-YYYYMMDDTHHMMSSZ-...`, `PL-####-...`). Backlog items are lightweight — an Objective, Problem Spec, and one-line Scope suffice. The full SDD specification is written into `ACTIVE.md` during activation, not before. Updating an existing plan or creating a new one requires user approval.
