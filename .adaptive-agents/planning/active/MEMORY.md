# Session Memory — Claude Code Support

Cross-session learnings and decisions for the Claude Code Support plan.

## Decisions Captured

- **Flags are limited to `--dry-run` only**: Following existing installer patterns (install-opencode.sh, install-vscode.sh). Tool-specific flags like `--scope`, `--skip-rules`, `--skip-hooks` are not part of the interface.
- **Path references over inline content**: CLAUDE.md references repo files by path rather than duplicating content. This way the repo stays the source of truth and re-running the installer isn't needed when instructions change.
- **Marker-delimited sections**: `#==ADAPTIVE_AGENTS_START/END==` in CLAUDE.md for clean update/removal on re-run.
- **User scope only**: Install to `~/.claude/` globally.
- **Single entrypoint fan-out, not per-file rule generation**: The entrypoint file (CLAUDE.md, .cursorrules, etc.) references the repo's AGENTS.md → INDEX.md → instructions/ chain. Do not generate individual rule files, hooks, skill markers, or guidance copies.
- **Claude requires one narrow settings grant**: The user-level `permissions.additionalDirectories` entry is required so Claude can read files routed from imported AGENTS.md when the active project is elsewhere. Preserve all existing settings and modify no unrelated keys.
- **Use Claude's native import syntax**: The CLAUDE.md section must contain a bare absolute `@.../AGENTS.md` line. A backticked path is literal text and does not import the file.

## Verified Behavior

- `--dry-run` shows all actions without writing
- First run appends section to existing CLAUDE.md
- Re-run replaces between markers (idempotent)
- CLAUDE.md imports the canonical AGENTS.md at startup
- settings.json preserves existing values and contains one repository access entry
- Automated installer suite passes
- Live Claude verification from outside the repository returns `ADAPTIVE_AGENTS_GLOBAL_LOADED` and routes a generic backlog question to the Project Layer `manage-planning` workflow
