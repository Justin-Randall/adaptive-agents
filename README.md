# Adaptive Agents

Adaptive Agents is a versioned, user-wide guidance repository for coding agents.

It is designed to keep reusable guidance in one place (instead of duplicating setup and rules in every project repository), while preserving a clear boundary between:

- Adaptive Agents repository (this repository)
- Current project repository (the codebase currently being modified)

## What Is In Place

The current repository includes:

- Core entrypoints:
  - `AGENTS.md` for operating model and boundary rules
  - `INDEX.md` as the discovery and routing map
  - `README.md` (this file) as the user-facing overview
- Durable guidance areas:
  - `instructions/` for default cross-project behavior
  - `skills/` for task-specific workflows, including repository maintenance and Project Layer bootstrap/upgrade
  - `playbooks/` for repeatable lifecycle workflows
  - `prompts/` for guided, reusable task flows
  - `memory/` for durable promoted lessons
  - `retrospectives/inbox/` for captured observations pending triage/promotion
  - `schemas/` for structured metadata/validation contracts
  - `agents/` for specialized role definitions
- Tool integration wiring:
  - `scripts/install-vscode.sh` and generated pointer file `vscode/user-wide.instructions.md`
  - `scripts/install-claude-code.sh` for Claude Code's native user-level import and repository access grant
  - `scripts/install-opencode.sh` and `opencode/` assets for the experimental OpenCode integration
  - `scripts/install.sh` for detected-tool routing
- Project Layer bootstrap:
  - canonical source under `templates/project-layer/`
  - model-led workflow in `skills/bootstrap-project-layer/SKILL.md`
  - deterministic mechanics in `scripts/bootstrap-project-layer.sh`
  - review-first upgrades through `skills/upgrade-project-layer/SKILL.md`

## How It Works

Adaptive Agents uses a routed, layered model.

**Entry and routing.** Start from `AGENTS.md`, then `INDEX.md`, and load only relevant guidance for the current task.

**Default instruction split.** `instructions/global.instructions.md` routes to task-specific defaults covering repository boundaries, coding, TDD, command-failure pivots, and temporary-artifact hygiene.

**Adaptation lifecycle.** Choose `Project Layer`, `User-wide`, or `Undetermined` scope before target type. Capture project-specific observations in `.adaptive-agents/retrospectives/inbox/` and established cross-project observations in `retrospectives/inbox/`. Triage and promote only durable lessons to the narrowest target within the selected scope (`memory/`, `instructions/`, `skills/`, `playbooks/`, etc.), then update `INDEX.md` when discoverability changes.

**Boundary protection.** When working in other repositories, Adaptive Agents is user-wide guidance, not project-local content. Agents should not copy Adaptive Agents directories into project repositories unless explicitly instructed.

**Project Layer.** An installed Adaptive Agents system can bootstrap a project-owned `.adaptive-agents/` directory after interviewing the user. The layer contains routed project instructions, skills, memory, retrospectives, indexed planning, lifecycle playbooks, and a read-only validator. The user chooses whether the layer is tracked, clone-locally excluded through `.git/info/exclude`, or repository-wide ignored through `.gitignore`. Installed user-wide guidance discovers `.adaptive-agents/INDEX.md`; bootstrap does not add root agent files or editor settings to the project.

Reference workflow:

- `playbooks/adaptation-cycle.md`
- `playbooks/adaptive-automation-roadmap.md`

## How To Use It

### 1) Install VS Code Integration

From this repository root:

```bash
./scripts/install-vscode.sh
```

Useful options:

```bash
./scripts/install-vscode.sh --dry-run
./scripts/install-vscode.sh --code-flavor insiders
./scripts/install-vscode.sh --settings "$APPDATA/Code/User/settings.json"
```

What the installer does:

- detects repository root path
- writes or refreshes `vscode/user-wide.instructions.md`
- updates VS Code user `settings.json` additively
- registers the repository guidance location for chat instructions
- enables instruction loading/apply settings
- creates a timestamped backup before editing settings

What it does not do:

- modify unrelated project repositories
- copy Adaptive Agents structure into other repositories
- store secrets

Note: the current checked-in installer is Bash (`scripts/install-vscode.sh`).

### 2) Install OpenCode Integration

> **Experimental:** Dogfooding has shown intermittent `AGENTS.md` loading in OpenCode. The installer remains available for diagnosis and existing users, but the integration is not considered verified while [OpenCode Installer Rework](.adaptive-agents/planning/backlog/PL-20260711-opencode-installer-rework.md) is pending. Validate with multiple fresh sessions rather than treating a successful installer exit as proof of instruction loading.

From this repository root:

```bash
./scripts/install-opencode.sh
```

Useful options:

```bash
./scripts/install-opencode.sh --dry-run
./scripts/install-opencode.sh --opencode-config PATH
./scripts/install-opencode.sh --skip-commands
```

What the installer does:

- detects repository root path
- creates or updates the OpenCode global config (`opencode.json` or `opencode.jsonc`) with `instructions` referencing Adaptive Agents files
- installs a global `~/.config/opencode/AGENTS.md` intended to expose the Adaptive Agents entrypoint
- installs custom slash commands (`/capture-retrospective`, `/triage-retrospective`, `/review-retrospective-inbox`, `/review-promotion-candidates`, `/apply-approved-promotion`, `/check-adaptive-agents`) to OpenCode's global commands directory
- detects whether the OpenCode CLI is installed
- creates a timestamped backup before modifying any config

What it does not do:

- modify VS Code settings
- modify project repositories
- copy Adaptive Agents structure into other repositories
- store secrets

### 3) Install Claude Code Integration

Prerequisites: Bash and Python 3. On Windows, run the installer through Git Bash or WSL.

From this repository root:

```bash
./scripts/install-claude-code.sh
```

Or install all detected tools at once:

```bash
./scripts/install.sh
```

Useful options:

```bash
./scripts/install-claude-code.sh --dry-run
./scripts/install.sh --tool claude
```

What the installer does:

- detects repository root path
- creates or updates a marker-delimited section in `~/.claude/CLAUDE.md`
- uses Claude Code's native absolute `@` import to load the canonical `AGENTS.md` at session startup
- adds the repository to `permissions.additionalDirectories` in `~/.claude/settings.json` so routed files remain readable
- preserves existing Claude Code settings and deduplicates the repository access entry

Claude Code may ask you to approve the external AGENTS.md import the first time it encounters it.

What it does not do:

- generate rule files, hooks, skills markers, or copies of Adaptive Agents guidance
- modify provider config, model selection, or unrelated permissions
- modify project repositories
- copy Adaptive Agents structure into other repositories
- store secrets

### 4) Verify Guidance Is Loaded

In any supported tool, ask:

```text
Are Adaptive Agents active?
```

Expected response:

```text
ADAPTIVE_AGENTS_GLOBAL_LOADED
```

If you get `ADAPTIVE_AGENTS_GLOBAL_LOADED`, Adaptive Agents is active and your AI coding tool is reading the user-wide guidance from this repository.

**Verified integrations**: VS Code / GitHub Copilot (after `install-vscode.sh`) and Claude Code (after `install-claude-code.sh`).

**Experimental integration**: OpenCode (after `install-opencode.sh`) remains under rework because fresh sessions do not yet load guidance consistently.

### 5) Invoke Prompts via Natural Language or Slash Commands

The prompt files under `prompts/` are designed to be invoked from VS Code Chat. You can trigger them with a natural language request or a slash command, depending on how the prompt is configured.

**Natural language examples:**

```text
Capture a retrospective about the repeated validation loop issue we hit today.
```

```text
Review the retrospective inbox and tell me what needs attention.
```

```text
Triage the latest retrospective note and recommend next steps.
```

**Slash command examples** (for prompts that define an `agent` frontmatter field):

```text
/capture-retrospective Repeated validation loops when editing instructions
```

```text
/review-retrospective-inbox
```

```text
/review-promotion-candidates
```

```text
/review-retrospective-session
```

```text
/triage-retrospective
```

```text
/apply-approved-promotion
```

If a prompt has an `argument-hint` in its frontmatter, you can pass a short argument after the slash command to focus the invocation.

### 6) Run the Adaptation Loop

Common flow:

1. Capture one observation in `retrospectives/inbox/YYYY-MM-DD-short-title.md`.
2. Triage with prompts and playbooks.
3. Promote only when durable.
4. Keep generated bootstrap files disposable and durable guidance checked in.

Helpful prompt files:

- `prompts/capture-retrospective.prompt.md`
- `prompts/end-of-session-capture.prompt.md`
- `prompts/triage-retrospective.prompt.md`
- `prompts/review-retrospective-session.prompt.md`
- `prompts/apply-approved-promotion.patch.prompt.md`
- `prompts/review-retrospective-inbox.prompt.md`
- `prompts/review-promotion-candidates.prompt.md`

### 7) Check Repository Health

Run the deterministic checker before or after guidance changes:

```bash
bash scripts/check-adaptive-agents.sh
```

Use verbose output when you need to see every passing check:

```bash
bash scripts/check-adaptive-agents.sh --verbose
```

The checker is read-only. It validates required repository structure, prompt routing, retrospective statuses and privacy patterns, local Markdown links and guidance reachability, canonical and dogfood Project Layers, Project Layer regression tests, and the installed Claude Code import and access grant when present. By default it prints only warnings, failures, and the final summary.

### 8) Bootstrap A Project Layer

Ask Adaptive Agents to bootstrap a Project Layer in the current project. The bootstrap skill inspects existing guidance and Git state, then asks for project-specific instructions, initial active work, and one persistence mode before previewing any changes.

The deterministic command used after approval is:

```bash
bash scripts/bootstrap-project-layer.sh \
  --target "/path/to/project" \
  --project-name "Example Project" \
  --active-plan-id "PL-20260710" \
  --active-title "Initial project work" \
  --persistence tracked
```

Use `--dry-run` to preview mechanics. Bash and Python 3 are required; on Windows, run through Git Bash or WSL.

Each active plan declares a canonical `PL-YYYYMMDD-descriptive-slug` work-unit ID and keeps curated handoff context in `<work-unit-id>.memory.md`. Closure preserves the plan, original backlog item when present, and memory under the same work-unit identity. Reopened work receives a new identity and links to immutable prior context rather than overwriting it.

Existing layers are project-owned and are never recopied from the template. Use `scripts/inspect-project-layer-upgrade.sh` with the Project Layer upgrade skill to compare versions and prepare an approval-gated merge.

Run the focused Project Layer regression suite with:

```bash
bash scripts/test-project-layer.sh
```

## Current Status

This repository is in an actively used bootstrap-plus-hardening phase:

- routing is in place (`INDEX.md`)
- default instruction split is in place (`instructions/*.instructions.md`)
- adaptation playbooks and prompt workflows are present
- retrospective inbox includes active dogfooded examples
- the canonical Project Layer template, bootstrap/upgrade workflows, regression tests, and tracked dogfood layer are present
- VS Code and Claude Code integrations are verified through their native loading mechanisms
- OpenCode integration remains experimental pending the queued installer rework
- related tool integrations are captured as lightweight backlog items with a shared native-entrypoint verification contract

## Design Intent

Adaptive Agents guidance should remain:

- reusable across projects
- evidence-backed before promotion
- easy to discover through routing
- explicit and reviewable in source control
- separate from project-local source repositories unless explicitly requested
