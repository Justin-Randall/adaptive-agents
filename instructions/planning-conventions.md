# Planning Conventions

These are user-wide conventions for planning and backlog management across all Adaptive Agents Project Layers. They help keep work units appropriately sized, discoverable, and dependency-aware.

Project-local conventions override these defaults when more specific.

## Work Unit Sizing

A backlog item should be sized so the agent can close it in a single activation. As a rule of thumb, the total estimated context to implement and verify the item should not exceed half the model's context window (512k tokens for a 1M-token model; 128k for a 256k-token model).

If the estimated size exceeds this threshold, the item is a candidate for splitting into smaller work units (see "Epic / Child Pattern" below).

## Epic / Child Pattern

When a backlog item grows too large for a single activation, split it into an epic with children:

- **Epic**: A container item with `Status: Epic`. Holds the high-level Objective, Problem Spec, architecture overview, and resolved decisions. Never activated directly — only children are activated.
- **Children**: Independent backlog items, each sized for a single activation. Each has its own Objective, Scope, Acceptance Criteria, and Readiness. They follow the same lifecycle as standalone items — when activated, they receive the full SDD treatment in `ACTIVE.md`.

### Directory Structure

```
backlog/
  INDEX.md
  PL-YYYYMMDD-descriptive-slug.md                    ← epic file
  PL-YYYYMMDD-descriptive-slug/                       ← children directory
    PL-YYYYMMDD-descriptive-slug-child-one.md
    PL-YYYYMMDD-descriptive-slug-child-two.md
    ...
```

The epic file lives at the backlog root alongside other items. Children live in a subdirectory matching the epic's filename stem (minus the `.md` extension).

Child filenames carry the full epic name followed by a short description. They are self-describing without needing a numeric prefix.

### Link Graph

All files in the hierarchy must be connected. The validator will check:

- **INDEX.md** links to the epic file.
- **Epic file** links to each child file (typically in a children table).
- **Child files** link back to the epic file (as a `Parent` field).
- **Child files** may link to sibling children for dependency ordering (as a `Depends on` field).

This makes the hierarchy traversable for both humans and automated checks.

### Activation Rules

1. **Epics are never activated directly**. If the user selects an epic for activation, ask which child they want to work on.
2. **Activate one child at a time**. Each child represents a single-session work unit. Close it before activating the next.
3. **Check dependencies**. Before activating a child, verify its dependencies are in `Completed` or `Ready` state. If a dependency is not ready, the child cannot be activated.
4. **Epic context is available**. Load the epic file alongside the child during activation for architecture context and resolved decisions. The child's own Objective, Scope, and AC drive the session — the epic provides supporting context only.

### Closure Lifecycle

When a child closes, it follows the standard end-work playbook — its ACTIVE.md is saved to `planning/closed/PL-YYYYMMDD-slug-child-description/` along with its curated memory.

When the last child closes, the epic itself is fully delivered. The entire hierarchy moves to `planning/closed/`, mirroring the backlog structure:

```
closed/
  PL-YYYYMMDD-descriptive-slug/
    PL-YYYYMMDD-descriptive-slug.sdd.md              ← epic epilogue
    PL-YYYYMMDD-descriptive-slug-child-one/
      PL-YYYYMMDD-descriptive-slug-child-one.sdd.md
      PL-YYYYMMDD-descriptive-slug-child-one.memory.md
    PL-YYYYMMDD-descriptive-slug-child-two/
      PL-YYYYMMDD-descriptive-slug-child-two.sdd.md
      PL-YYYYMMDD-descriptive-slug-child-two.memory.md
    ...
```

The epic epilogue is a lightweight SDD summarizing what was delivered, any deferred scope, and links to each child. The backlog INDEX.md entry is removed; the closed INDEX.md entry links to the epic directory.

### Upgrade Path

An item does not need to start as an epic. If during spec review or implementation it becomes clear that the scope exceeds the sizing threshold, propose splitting it. The original spec becomes the epic file, and focused child files are created from the existing scope and acceptance criteria.
