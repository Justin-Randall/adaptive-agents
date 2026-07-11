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
  - `scripts/install-opencode.sh` for OpenCode's native instructions entry point and external-directory access grant
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

Prerequisites: Bash and Python 3. On Windows, run the installer through Git Bash or WSL.

From this repository root:

```bash
./scripts/install-opencode.sh
```

Useful options:

```bash
./scripts/install-opencode.sh --dry-run
./scripts/install-opencode.sh --opencode-config PATH
```

The integration is two parts, applied to OpenCode's global config (`~/.config/opencode/opencode.json` or `.jsonc`):

- **Entry point**: one `instructions` entry loading the canonical repository `AGENTS.md` content at session start ([OpenCode rules docs](https://opencode.ai/docs/rules/)); `AGENTS.md → INDEX.md → instructions/` fan-out handles all further routing
- **Trusted source directories**: a `permission.external_directory` grant marking this repository safe to read and write from sessions in other projects — OpenCode blocks external paths behind an "ask" prompt by default ([OpenCode permissions docs](https://opencode.ai/docs/permissions/))

The installer also migrates away artifacts from earlier versions of this integration (a sentinel-duplicating global `AGENTS.md` copy, redundant `instructions` entries, installed slash commands, and stale `%APPDATA%/opencode` files), preserves all unrelated configuration, creates a timestamped backup before modifying the config, and leaves managed files byte-for-byte unchanged on re-run.

What it does not do:

- copy or generate guidance content (the repository stays the source of truth)
- modify provider, model, or unrelated permission configuration
- modify project repositories
- store secrets

After installing, verify from a fresh OpenCode session in an unrelated repository:

1. **Sentinel** — "Are Adaptive Agents active?" → `ADAPTIVE_AGENTS_GLOBAL_LOADED`
2. **Content proof** — "What is the current active plan and top backlog item?" → must name the actual plan from this repository (the sentinel alone can be a false positive)
3. **Write-back** — ask for a retrospective capture → a file appears in `retrospectives/inbox/`

Run the automated installer tests with `bash scripts/test-opencode.sh`.

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

Every integration is verified the same way, in a **fresh session in a repository unrelated to this one**, with three probes:

1. **Sentinel** — ask:

   ```text
   Are Adaptive Agents active?
   ```

   Expected response: `ADAPTIVE_AGENTS_GLOBAL_LOADED`

2. **Content proof** — ask:

   ```text
   What is the current active plan and top backlog item?
   ```

   The answer must name the actual plan from this repository's `.adaptive-agents/planning/`. The sentinel alone can be a false positive — a stale installed copy can echo it without the tool ever reading this repository — so a probe answerable only from repository content is required.

3. **Write-back** — ask the tool to capture a retrospective. A file must appear in `retrospectives/inbox/` without a permission failure, proving the integration's access grant covers writes.

Repeat across multiple fresh sessions; intermittent loading is a failure, not a pass.

**Verified integrations**: VS Code / GitHub Copilot (after `install-vscode.sh`) and Claude Code (after `install-claude-code.sh`).

**Reworked integration**: OpenCode (after `install-opencode.sh`) now uses the same two-part pattern; treat it as verified only after fresh-session dogfooding passes all three probes.

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
- OpenCode integration is reworked around a single native entry point plus an external-directory access grant, pending fresh-session dogfood confirmation
- related tool integrations are captured as lightweight backlog items with a shared native-entrypoint verification contract

## Design Intent

Adaptive Agents guidance should remain:

- reusable across projects
- evidence-backed before promotion
- easy to discover through routing
- explicit and reviewable in source control
- separate from project-local source repositories unless explicitly requested
