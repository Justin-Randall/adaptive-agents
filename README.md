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
  - `skills/` for task-specific workflows (currently includes `update-adaptive-agents`)
  - `playbooks/` for repeatable lifecycle workflows
  - `prompts/` for guided, reusable task flows
  - `memory/` for durable promoted lessons
  - `retrospectives/inbox/` for captured observations pending triage/promotion
  - `schemas/` for structured metadata/validation contracts
  - `agents/` for specialized role definitions
- VS Code bootstrap wiring:
  - `scripts/install-vscode.sh`
  - generated pointer file: `vscode/user-wide.instructions.md`

## How It Works

Adaptive Agents uses a routed, layered model:

1. Entry and routing
   - Start from `AGENTS.md`, then `INDEX.md`.
   - Load only relevant guidance for the current task.

2. Default instruction split
   - `instructions/global.instructions.md` routes to:
     - `instructions/repository-boundaries.instructions.md`
     - `instructions/coding.instructions.md`
     - `instructions/tdd.instructions.md`

3. Adaptation lifecycle
   - Capture observations in `retrospectives/inbox/`.
   - Triage and promote only durable lessons.
   - Promote to the narrowest target (`memory/`, `instructions/`, `skills/`, `playbooks/`, etc.).
   - Update routing in `INDEX.md` when discoverability changes.

4. Boundary protection
   - When working in other repositories, Adaptive Agents is user-wide guidance, not project-local content.
   - Agents should not copy Adaptive Agents directories into project repositories unless explicitly instructed.

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

### 2) Verify Guidance Is Loaded

In VS Code Chat, ask:

```text
Use my Adaptive Agents guidance. What user-wide instructions are available for this task?
```

You can also verify the global instruction sentinel response:

```text
ADAPTIVE_AGENTS_GLOBAL_LOADED
```

### 3) Invoke Prompts via Natural Language or Slash Commands

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

### 4) Run the Adaptation Loop

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

### 5) Check Repository Health

Run the deterministic checker before or after guidance changes:

```bash
bash scripts/check-adaptive-agents.sh
```

Use verbose output when you need to see every passing check:

```bash
bash scripts/check-adaptive-agents.sh --verbose
```

The checker is read-only. It validates prompt routing, retrospective statuses, promotion links, blocked private/raw link patterns, local Markdown links, and whether guidance Markdown files are reachable from `INDEX.md`. By default it prints only warnings, failures, and the final summary.

## Current Status

This repository is in an actively used bootstrap-plus-hardening phase:

- routing is in place (`INDEX.md`)
- default instruction split is in place (`instructions/*.instructions.md`)
- adaptation playbooks and prompt workflows are present
- retrospective inbox includes active dogfooded examples

## Design Intent

Adaptive Agents guidance should remain:

- reusable across projects
- evidence-backed before promotion
- easy to discover through routing
- explicit and reviewable in source control
- separate from project-local source repositories unless explicitly requested
