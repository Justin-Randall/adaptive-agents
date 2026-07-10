# PL-20260710: OpenCode Installer Support

- Status: Active
- Origin: Backlog (PL-20260710)

## Objective

Add an OpenCode installer that generates OpenCode-standard configuration pointing to the Adaptive Agents repository, so users of OpenCode-compatible editors (Cursor, Windsurf, continue.dev CLI/TUI, etc.) can discover and use Adaptive Agents — checking retrospectives, querying active work, and confirming Adaptive Agents is active — without requiring GitHub Copilot or VS Code.

## Specifications

### Problem Spec

The current installer (`scripts/install-vscode.sh`) produces VS Code settings and GitHub Copilot-specific instructions for discovering the Adaptive Agents repository. OpenCode is a rapidly growing open source AI coding agent ecosystem with a model-agnostic configuration layer (see [opencode.ai/docs/config](https://opencode.ai/docs/config/)). Without OpenCode support, users who prefer OpenCode-compatible editors or the OpenCode CLI/TUI receive no Adaptive Agents guidance, and the installer produces Copilot-locked output. This limits adoption, creates vendor lock-in, and misses the opportunity to position Adaptive Agents as editor-agnostic.

### Feature Specs

#### 1. OpenCode Configuration Generation (Primary)

The installer must generate an OpenCode config file (JSON/JSONC) at OpenCode's standard global config location, using the `instructions` field to reference Adaptive Agents files as instruction sources — the closest parallel to VS Code's `chat.instructionsFilesLocations`.

The generated `instructions` array must include:

- `<REPO_ROOT>/AGENTS.md` — operating rules
- `<REPO_ROOT>/INDEX.md` — routing index
- `<REPO_ROOT>/instructions/global.instructions.md` — user-wide guidance
- `<REPO_ROOT>/instructions/*.instructions.md` — all instruction files (glob pattern)
- When a Project Layer `.adaptive-agents/INDEX.md` is present in the current project, OpenCode's native discovery should pick it up (via `instructions` or via AGENTS.md chain-loading)

#### 2. Custom Slash Commands

Create command files for OpenCode's global commands directory that map to Adaptive Agents prompts:

| Command File | Maps To | Slash Command |
|---|---|---|
| `opencode/commands/capture-retrospective.md` | `prompts/capture-retrospective.prompt.md` | `/capture-retrospective` |
| `opencode/commands/triage-retrospective.md` | Access to retrospective skills | `/triage-retrospective` |
| `opencode/commands/review-retrospective-inbox.md` | Retrospective review prompts | `/review-retrospective-inbox` |
| `opencode/commands/review-promotion-candidates.md` | Promotion review prompts | `/review-promotion-candidates` |
| `opencode/commands/apply-approved-promotion.md` | Promotion apply prompts | `/apply-approved-promotion` |
| `opencode/commands/check-adaptive-agents.md` | Verification prompt | `/check-adaptive-agents` |

Each command file is a Markdown file with YAML frontmatter (`description`, optional `agent`, `model`) with the body being the prompt text sent to the LLM. Native OpenCode commands dir can be global or project-level; the installer targets global.

#### 3. Global AGENTS.md (Optional)

A global agent rules file installed to OpenCode's standard AGENTS.md location. Contains the same bootstrapping instructions as `vscode/user-wide.instructions.md` — telling the agent to load Adaptive Agents files and respond with `ADAPTIVE_AGENTS_GLOBAL_LOADED` when asked. Controlled by `--global-rules` flag.

#### 4. Installer Script (`scripts/install-opencode.sh`)

A standalone idempotent installer analogous to `install-vscode.sh`. Must:

1. Detect the Adaptive Agents repository root (same logic as `install-vscode.sh`)
2. Create/update OpenCode's global config by merging:
   - Read existing config if present (preserve all keys)
   - Set/update `instructions` array with Adaptive Agents file paths (deduplicate)
   - Add custom commands under `command` key
   - Write a sentinel marker for idempotency detection
3. Copy `opencode/commands/*.md` → OpenCode's global commands directory (overwrite existing)
4. Optionally install `opencode/AGENTS.md` → OpenCode's global AGENTS.md location (with `--global-rules`)
5. Detect whether OpenCode CLI is installed (`command -v opencode`) and report status
6. Create a backup of any existing OpenCode config before modifying

Flags: `--dry-run`, `--global-rules`, `--opencode-config PATH`, `--skip-commands`

#### 5. Umbrella Installer (`scripts/install.sh`)

A routing script that detects the environment and runs appropriate sub-installers:

1. Detect the Adaptive Agents repository root
2. If VS Code is detected (`code` command or VS Code settings exists), run `install-vscode.sh`
3. If OpenCode compatibility is detected (OpenCode config dir exists, `opencode` CLI found, Cursor/Windsurf config exists), run `install-opencode.sh`
4. If neither, show a message suggesting both installation paths
5. Pass all flags through to sub-installers

#### 6. README Documentation Update

Add a new OpenCode installation section to `README.md` (analogous to the existing VS Code section). Also update the verification section to list OpenCode-compatible editors alongside VS Code.

#### 7. Repository Checker Update

Update `scripts/check-adaptive-agents.sh` to validate OpenCode configuration when present.

### Interface / Contract Specs

#### OpenCode Config Schema (Generated)

The installer produces a JSON/JSONC file conforming to the OpenCode config schema (`https://opencode.ai/config.json`):

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "instructions": [
    "<REPO_ROOT>/AGENTS.md",
    "<REPO_ROOT>/INDEX.md",
    "<REPO_ROOT>/instructions/global.instructions.md",
    "<REPO_ROOT>/instructions/*.instructions.md"
  ],
  "command": {
    "capture-retrospective": {
      "template": "...",
      "description": "Capture a retrospective observation about the current session"
    },
    // ... other commands
  }
}
```

#### Command File Format (Markdown + YAML frontmatter)

```markdown
---
description: One-line description shown in the TUI command list
agent: build (optional, defaults to current)
model: provider/model-id (optional)
---

The prompt text sent to the LLM when the command is invoked. May reference repo files
by path relative to the Adaptive Agents repository.
```

#### Idempotency Marker

The installer adds a sentinel key to the config:

```jsonc
"_adaptive_agents_installed": true
```

On re-run, if this marker exists and paths match, skip config write. If paths differ, update in-place.

### Data Model Specs

#### Config Merge Logic

When modifying an existing `opencode.json`:

- **`instructions`**: Append new paths not already present; deduplicate by exact path string match
- **`command`**: Merge/overwrite entries for Adaptive Agents command names; preserve all other command entries
- **`_adaptive_agents_installed`**: Set to `true`
- **All other keys**: Preserved as-is

#### Command File Deployment Logic

- Source: `opencode/commands/*.md` (in the Adaptive Agents repo)
- Target: OpenCode's global commands directory
- Strategy: Copy with overwrite (same filename = same command, no risk of collision with non-Adaptive-Agents commands since they have unique filenames)

### Behavioral Specs

#### Idempotency

Running any installer N times produces exactly the same state as running it once:

- No duplicate entries in `instructions` array
- No duplicate command entries
- Backup is created on first run only (subsequent runs overwrite the same backup if paths unchanged)
- Sentinel marker prevents redundant writes

#### Coexistence with VS Code

- The OpenCode installer must never read, write, or modify any VS Code settings file
- The VS Code installer (`install-vscode.sh`) must never read, write, or modify any OpenCode config
- Both installations can coexist on the same system
- The umbrella installer (`install.sh`) is the only script that touches both ecosystems

#### Error Handling

- If OpenCode config location cannot be determined, fail with a clear message and suggest `--opencode-config PATH`
- If the repo root cannot be detected (no `AGENTS.md` and `INDEX.md` present), fail same as `install-vscode.sh` does
- If Python is not available for JSON merge, fall back to a simple JSON write (with warning) or fail with instructions (same pattern as `install-vscode.sh`)
- Backup is always created before the first write to any config file

## Applicable Guidance

- `skills/manage-planning/SKILL.md` — governs activation, execution, and closure of this work
- `instructions/repository-boundaries.instructions.md` — this plan operates in the Adaptive Agents repository, where modifying scripts, documentation, and planning artifacts is in scope
- `instructions/coding.instructions.md` — general coding standards for implementation
- `vscode/user-wide.instructions.md` — the existing VS Code installer pattern that the OpenCode installer mirrors

## Scope

### In Scope

- OpenCode config template and installer (`opencode/opencode.jsonc`, `scripts/install-opencode.sh`)
- Custom command files for OpenCode (`opencode/commands/*.md`)
- Optional global AGENTS.md (`opencode/AGENTS.md`)
- Umbrella installer (`scripts/install.sh`)
- README documentation updates
- Repository checker updates for OpenCode config
- `.gitignore` update to exclude `.opencode/`
- Coexistence with existing VS Code setup

### Out of Scope (v0)

- Full OpenCode SDK/validator development — consume the standard, don't implement it
- Migrating or removing existing Copilot-specific configuration — both formats coexist
- Supporting non-OpenCode AI coding tools beyond Copilot and OpenCode
- A GUI installer
- Supporting per-project `opencode.json` — global config approach covers all projects
- MCP server integration — Adaptive Agents is a guidance repository, not a service

## Acceptance Criteria

- [ ] `scripts/install-opencode.sh` idempotently creates/updates the OpenCode global config with `instructions` pointing to Adaptive Agents files.
- [ ] After install, asking "Are Adaptive Agents active?" in any OpenCode-compatible editor returns `ADAPTIVE_AGENTS_GLOBAL_LOADED`.
- [ ] After install, the user can run `/capture-retrospective`, `/triage-retrospective`, `/review-retrospective-inbox`, `/review-promotion-candidates`, `/apply-approved-promotion`, and `/check-adaptive-agents` as OpenCode slash commands.
- [ ] Custom command files are installed to OpenCode's global commands directory without overwriting non-Adaptive-Agents commands.
- [ ] VS Code settings are never modified by any OpenCode installer.
- [ ] Re-running any installer produces the same result — no duplicate entries, no config bloat.
- [ ] `scripts/install.sh` detects the environment and routes to the appropriate sub-installer(s).
- [ ] `scripts/check-adaptive-agents.sh` validates OpenCode config when present.
- [ ] `README.md` documents both installation paths (VS Code and OpenCode).

## Progress

- [ ] Activate backlog item (this step).
- [ ] Create template files: `opencode/opencode.jsonc`, `opencode/commands/*.md`, `opencode/AGENTS.md`.
- [ ] Implement `scripts/install-opencode.sh`.
- [ ] Implement `scripts/install.sh`.
- [ ] Update `README.md` with OpenCode installation section.
- [ ] Update `.gitignore`.
- [ ] Update `scripts/check-adaptive-agents.sh`.
- [ ] Test idempotency — run installer N times, verify config stability.
- [ ] Test coexistence — verify VS Code config untouched.
- [ ] Verify end-to-end: install, confirm ADAPTIVE_AGENTS_GLOBAL_LOADED, run a command.

## Decisions

- **Global config** over per-project config: Installing to OpenCode's global config directory makes Adaptive Agents available in every project without each project needing its own `opencode.json`. The installer detects the correct location at runtime. Mirrors the VS Code approach of using global `settings.json`.
- **Both `instructions` + `AGENTS.md`**: The `instructions` field is the primary mechanism (exact file path references). The `AGENTS.md` is optional (requires `--global-rules` flag) and serves as a secondary discovery path.
- **Commands are installed, not symlinked**: Copy command files so they survive repo moves. The installer is re-runnable if the repo path changes.
- **No MCP server**: Adaptive Agents is a guidance repository, not a service. MCP is out of scope unless a future need for live tool access arises.
- **JSON merge strategy**: Use the same Python-based JSON merge approach as `install-vscode.sh` — read existing config, merge new keys, deduplicate arrays, write back with backup.
- **Idempotency marker**: Use `"_adaptive_agents_installed": true` as a sentinel key to detect prior installation.

## Verification

- Not run.
- Run `bash .adaptive-agents/scripts/check-project-layer.sh` after planning structure changes.

## Supporting Documents

- [Backlog item](../backlog/PL-20260710-opencode-installer-support.md)
- [Active memory](MEMORY.md)
- SDD template — see `templates/project-layer/.adaptive-agents/planning/active/ACTIVE.md` in the repo root
- `scripts/install-vscode.sh` in the repo root — reference pattern for the installer design
- [OpenCode config docs](https://opencode.ai/docs/config/)
- [OpenCode commands docs](https://opencode.ai/docs/commands/)
- [OpenCode rules docs](https://opencode.ai/docs/rules/)
- [OpenCode skills docs](https://opencode.ai/docs/skills/)
