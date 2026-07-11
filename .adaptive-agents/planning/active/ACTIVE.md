# PL-20260711: Claude Code Support

- Status: Active
- Work Unit: PL-20260711-claude-code-support
- Origin: Backlog ([PL-20260711-claude-code-support.md](../backlog/PL-20260711-claude-code-support.md))
- Activated: 2026-07-11

## Objective

Create an idempotent installer (`scripts/install-claude-code.sh`) that makes the canonical Adaptive Agents `AGENTS.md` available in every Claude Code session and preserves access to files it routes to, without copying or regenerating guidance.

## Specifications

### Problem Spec

Claude Code loads user instructions from `~/.claude/CLAUDE.md`, but it does not natively discover `AGENTS.md`. Prose telling the model to read an external path is insufficient because runtime file tools reject paths outside allowed working directories. Claude's native `@path` import loads AGENTS.md at startup, while `permissions.additionalDirectories` grants access to INDEX.md and other files selected by the canonical routing flow.

### Feature Spec 1.0: Install Script

`scripts/install-claude-code.sh` — idempotent installer.

**Flags**:

- `--dry-run` — preview changes without writing

**Detection logic**:

1. Detect Adaptive Agents repo root (same pattern as existing installers)
2. Read existing `~/.claude/CLAUDE.md` for prior Adaptive Agents section

**Merge strategy**:

- `~/.claude/CLAUDE.md`: append or replace a marker-delimited section containing a bare absolute `@<repo>/AGENTS.md` import.
- `~/.claude/settings.json`: preserve existing content and ensure `permissions.additionalDirectories` contains the repository root exactly once.

**Idempotency**: marker replacement in CLAUDE.md plus a deduplicated settings entry. A same-version rerun leaves both files byte-for-byte unchanged.

**Exit codes**: 0 = success, 1 = error.

### Feature Spec 2.0: Umbrella Integration

Update `scripts/install.sh` to detect Claude Code and route to `install-claude-code.sh`.

### Feature Spec 3.0: Health Check

Update `scripts/check-adaptive-agents.sh` to validate Claude Code config:

- Check `~/.claude/CLAUDE.md` for Adaptive Agents section
- Check the section imports the canonical AGENTS.md
- Check `permissions.additionalDirectories` grants access to the repository

### Interface/Contract Spec

| Aspect | Spec |
| --- | --- |
| Invocation | `bash scripts/install-claude-code.sh [flags]` |
| Stdout | Human-readable progress lines, one per action |
| Stderr | Error messages with actionable guidance |
| Exit 0 | Installation complete |
| Exit 1 | Error with description on stderr |
| Dry-run output | Prefix each action with `[dry-run]`, show what would be created/modified |

### Data Model Spec

**Idempotency mechanism**: Marker-based detection on CLAUDE.md section markers (no separate sentinel in settings.json). The installer detects prior installation by checking for START/END markers in `~/.claude/CLAUDE.md`, not by any key in `settings.json`.

**CLAUDE.md section markers**:

```markdown
#==ADAPTIVE_AGENTS_START==
@C:/path/to/adaptive-agents/AGENTS.md
#==ADAPTIVE_AGENTS_END==
```

### Behavioral Spec

- **User scope**: Install to `~/.claude/` by default, making Adaptive Agents available in every project.
- **Conflict resolution**: If `~/.claude/CLAUDE.md` already has a section between the markers, replace it. If no markers found, append at end.
- **Settings preservation**: If `~/.claude/settings.json` exists, retain all existing keys and permission entries. If absent, create the minimal access grant.
- **Re-run behavior**: Replace the managed CLAUDE.md section and add the repository access entry only when content differs.

## Applicable Guidance

- `instructions/global.instructions.md` — default engineering guidance
- `instructions/coding.instructions.md` — coding standards for the installer script
- `instructions/repository-boundaries.instructions.md` — keep installer in Adaptive Agents repo, not current project
- `instructions/tdd.instructions.md` — test-driven approach for installer behavior
- `commands/install-opencode.sh` (reference) — existing installer for parallel patterns
- `commands/install-vscode.sh` (reference) — existing VS Code installer patterns

## Scope

- Create `scripts/install-claude-code.sh` with `--dry-run` flag
- Update `scripts/install.sh` for Claude Code routing
- Update `scripts/check-adaptive-agents.sh` for Claude Code validation
- Update `README.md` with Claude Code installation section
- Create `scripts/test-install-claude-code.sh` integration test

## Out of Scope

- Modifying provider config, model selection, or unrelated permissions in settings.json
- Generating rules, hooks, skills markers, or copies of canonical guidance
- Deep auto-memory integration (Claude-managed per-project)
- MCP server configuration
- GUI installer
- Modifying existing OpenCode or VS Code config

## Acceptance Criteria

- [x] `scripts/install-claude-code.sh` creates/updates `~/.claude/CLAUDE.md` with Adaptive Agents file references.
- [x] After reinstall, a new Claude session outside this repository returns `ADAPTIVE_AGENTS_GLOBAL_LOADED` and routes backlog questions to `manage-planning`.
- [x] Single CLAUDE.md entrypoint fans out to repo files — no individual rule files generated.
- [x] Re-running the installer produces no duplicate entries or config bloat.
- [x] `--dry-run` shows changes without modifying anything.
- [x] Existing Claude Code settings are preserved and repository access is deduplicated after install.
- [x] `scripts/check-adaptive-agents.sh` validates Claude Code config when present.
- [x] `README.md` documents the Claude Code installation path.
- [x] Test script passes: `bash scripts/test-install-claude-code.sh`.

## Progress

- [x] Create `scripts/install-claude-code.sh` (single entrypoint: CLAUDE.md only)
- [x] Create `scripts/install.sh` umbrella
- [x] Update `scripts/check-adaptive-agents.sh` (Claude Code validation, AGENTS.md sentinel check)
- [x] Add sentinel to AGENTS.md (canonical source for all tools)
- [x] Update `README.md`
- [x] Create integration test (`scripts/test-install-claude-code.sh`)
- [x] Dogfood: reinstall, verify imported instructions and routing in a new Claude Code session
- [x] Dogfood: re-run, verify idempotency
- [x] Dogfood: verify `--dry-run` output

## Decisions

- **User scope**: Installing to `~/.claude/` makes Adaptive Agents available in every project.
- **`@` imports over inline content**: Keeps CLAUDE.md short; repo path parameterized at install time.
- **No generated rules, hooks, or skill markers**: AGENTS.md and INDEX.md remain the only routing source of truth.
- **Marker-delimited sections**: `#==ADAPTIVE_AGENTS_START/END==` in CLAUDE.md for clean update/removal.
- **Narrow JSON merge**: Only `permissions.additionalDirectories` is changed, preserving the user's existing Claude Code configuration.
- **No sentinel in settings.json**: Idempotency uses CLAUDE.md markers only — no `_adaptive_agents` key in settings.json (removed as confusing/unused dead weight).

## Verification

- Unit: test `--dry-run` flag in isolation
- Unit: test native absolute import and JSON merge with access deduplication
- Unit: test section replacement in CLAUDE.md (first install, re-run, removal)
- Integration: full install → dogfood in Claude Code → re-run → check health
- Idempotency: run twice, verify output is identical on second run
- Regression: run `scripts/check-adaptive-agents.sh` after install, verify no new failures

## Supporting Documents

- [Backlog: Claude Code Support](../backlog/PL-20260711-claude-code-support.md) — original backlog entry
- Playbook: `playbooks/adaptation-cycle.md` (repo root) — lifecycle guidance
- Reference: `scripts/install-opencode.sh` (repo root) — parallel implementation
- Reference: `scripts/install-vscode.sh` (repo root) — parallel implementation
- [PL-20260711-claude-code-support memory](PL-20260711-claude-code-support.memory.md) — cross-session learnings and decisions
