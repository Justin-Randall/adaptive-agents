# PL-20260711-gemini-cli-support Memory

Curated cross-session context for the Gemini CLI Support work unit.

## Current State

- Activated 2026-07-12 from backlog item `PL-20260711-gemini-cli-support.md`.
- **Phase 1 (Research) is COMPLETE** — findings documented in SDD (ACTIVE.md) and detailed below.
- Phase 2 (Installer implementation) is next.
- Reference implementations: `scripts/install-claude-code.sh`, `scripts/install-opencode.sh`, `scripts/test-install-claude-code.sh`, `scripts/test-opencode.sh`.

## Research Findings (completed 2026-07-12)

### Part A — Native Entry Point

| Question | Finding |
|----------|---------|
| Config file path | `~/.gemini/GEMINI.md` — global context file, loaded in EVERY session |
| Import syntax | `@path/to/file.md` — supports relative (`@./`, `@../`) and absolute (`@/abs/path`) |
| Alternative config | `context.fileName` setting can rename GEMINI.md to `["AGENTS.md", ...]` |
| Max import depth | 5 levels |
| Circular import | Detected and prevented automatically |

**Mechanism**: Write a single `@/absolute/path/to/AGENTS.md` line into `~/.gemini/GEMINI.md`. The Memory Import Processor resolves the import and includes AGENTS.md content in every session's system context.

### Part B — Read/Write Trust Grant

| Question | Finding |
|----------|---------|
| Trust grant mechanism | `context.includeDirectories` in `~/.gemini/settings.json` |
| Narrowest scope | Single absolute directory path |
| Folder trust | `security.folderTrust.enabled` + `~/.gemini/trustedFolders.json` |
| Tool auto-approve | `tools.allowed` array for bypassing confirmations |

**Mechanism**: Add the repo root path to `context.includeDirectories` in `~/.gemini/settings.json`. The sandbox and file system service explicitly allow reads/writes to these paths.

### Gemini CLI Version

Target: `@google/gemini-cli` (npm). Documented config format references v0.3.0+. Pin at install time via `gemini --version`.

## Decisions

- Follow the established two-part pattern exactly (Claude Code and OpenCode are reference implementations).
- **Part A**: Single `@` import line in `~/.gemini/GEMINI.md` → AGENTS.md → INDEX.md → instructions/ fan-out.
- **Part B**: `context.includeDirectories` in `~/.gemini/settings.json` granting read/write access.
- Require three-probe dogfood for closure (sentinel alone is insufficient — prior false-positive evidence from OpenCode).
- No project-local `.gemini/` or `.rules/` files — fan-out from `AGENTS.md`.

## Blocker

- None currently. Phase 1 research complete.

## Immediate Next Step

- **WAITING**: User is reviewing the SDD. After approval, implement `scripts/install-gemini-cli.sh` with the two-part pattern, dry-run support, and legacy migration.

## Deferred Discoveries

- None proposed.
