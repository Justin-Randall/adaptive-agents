# PL-20260712: Branch Development Guidance

- Status: Completed
- Work Unit: PL-20260712-branch-development-guidance
- Origin: Direct (no backlog item)
- Activated: 2026-07-12
- Closed: 2026-07-12

## Objective

Define and document branch workflow conventions for the Adaptive Agents repository, codified first as a project-layer instruction, then promoted to a user-wide instruction in `instructions/` that governs when to branch, how to name branches, how planning artifacts map to branch strategy, and how to prepare PRs/MRs for automerge.

## Problem Spec

The Adaptive Agents repository documents its `main` branch as protected (README.md line 74), but the project layer has no explicit guidance about:

1. When to create a feature branch vs. working directly on `main`.
2. How to name branches that correspond to active plans.
3. How to handle planning artifacts (which live in `.adaptive-agents/planning/`) when they need to be created or modified — should they go directly to `main` via PR, or be developed on a branch?
4. What signals an agent should check before deciding on branch strategy (README protection mentions, CI workflows, PR templates, etc.).

Without documented conventions, an agent has no principled basis for choosing a branch strategy, leading to inconsistency and potential protection-rule violations.

## Specifications

### 1. Project-Layer Instruction (`.adaptive-agents/instructions/branch-workflow.md`)

The project-layer instruction covers:

- **1a. Decision logic**: When to branch vs. commit directly. Check README, CONTRIBUTING, CI workflows, PR/MR templates, forge API (fallback), default to branch.
- **1b. Branch naming**: `pl-<short-slug>` for plans, kebab-case for features, `explore/<topic>` for experiments.
- **1c. Safety properties**: No force push, no history rewrites, plan artifacts survive merge, branch recovery from merge commit.
- **1d. Commit strategy**: Local commits encouraged for checkpoints/reverts. Squash before PR/MR. Push only when ready.
- **1e. Planning artifact lifecycle**: Branch from main, create artifacts on branch, work on branch, sync before PR/MR, PR/MR to main, delete branch post-merge.
- **1f. Automerge-ready PR/MR workflow**: Sync → validate → squash → push → the branch is automerge-ready. PR/MR creation is a mechanical convenience (gh/glab or paste template). Description makes review trivial: title summarises change, body references work unit ID, validation note confirms sync and clean state.
- **1g. Cross-session branch awareness**: On session start, check for unmerged `pl-*` branches and load the active one.
- **1h. Detection heuristics**: Forge-agnostic probe table — local README/CONTRIBUTING/CI/template checks preferred over auth-requiring API calls.

### 2. User-Wide Promotion

After the project-layer instruction is settled, promote a forge-agnostic version to `instructions/branch-workflow.instructions.md` as user-wide guidance:

- **2a. New file**: `instructions/branch-workflow.instructions.md` — same content, generalised for any repo.
- **2b. Update `global.instructions.md`**: Add reference in the "Read:" section.
- **2c. Update `INDEX.md`**: Add entry to guidance areas and default instructions tables.
- **2d. Project-layer redirect**: Replace `.adaptive-agents/instructions/branch-workflow.md` body with a redirect to the user-wide file.

### 3. Active Plan for This Work

The current session's active plan self-applies the branch workflow: created `pl-branch-development-guidance` from `main`, developed guidance on this branch.

### 4. Meta-Learning Capture

After completing this work unit, capture a retrospective note if the process revealed any friction — particularly around the branch-and-PR workflow for planning artifacts.

## Outcome

All specifications implemented and validated. Retrospective captured for SDD scope drift lesson. Branch `pl-branch-development-guidance` is on `origin` with a PR ready for user dogfooding and merge.

## Applicable Guidance

| Rule | Source |
|------|--------|
| Planning artifact lifecycle (create ACTIVE.md, SDD, memory) | `.adaptive-agents/skills/manage-planning/SKILL.md` |
| Repository boundary rules (don't create Adaptive Agents structure outside this repo) | `AGENTS.md` / `instructions/repository-boundaries.instructions.md` |
| Branch protection documented | `README.md` line 74 |
