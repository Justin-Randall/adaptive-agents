---
applyTo: "**"
description: "Use when: deciding branch strategy, creating a feature branch, naming a branch, preparing a PR/MR, or checking whether to work on the primary branch directly."
---

# Branch Workflow Instructions

These are user-wide conventions for branch development workflow. They help agents make consistent, safe decisions about when to branch, how to name branches, how to handle planning artifacts, and how to close work.

Project-local instructions and repository conventions override these defaults when they are more specific.

## Decision Logic

Before starting work that will create or modify tracked files, determine branch strategy:

1. **Is the primary branch protected?** Check these sources in order:
   - `README.md` — look for "branch is protected" or similar language.
   - `CONTRIBUTING.md` — look for PR/MR requirements, branch conventions.
   - CI workflow directories — `.github/workflows/`, `.gitlab-ci.yml`, etc.
   - PR/MR template files — `.github/pull_request_template.md`, `.gitlab/merge_request_templates/`, etc.
   - Git remote config — check `git config` for push restrictions.
2. **How substantial is the change?**
   - **Trivial** (single-file docs fix, typo, wording tweak): working directly on the primary branch is acceptable if it is not protected.
   - **Substantive** (new artifacts, structural changes, planning changes, cross-file edits): create a feature branch.
3. **When in doubt, branch.** Branching is cheap and reversible.

## Branch Naming Convention

| Purpose | Pattern | Example |
|---------|---------|---------|
| Active plan work | `pl-<short-slug>` | `pl-branch-workflow` |
| Non-plan feature | `<kebab-case-description>` | `fix-installer-path` |
| Experimental | `explore/<topic>` | `explore/idea-validation` |
| Repository-specific | Follow project conventions if they exist | See `CONTRIBUTING.md` |

## Safety Properties

| Property | How it is enforced |
|----------|--------------------|
| **No force push** | Never force-push a plan branch. Use `git merge`, not `git rebase`, when syncing with the primary branch. |
| **No history rewrites** | Once pushed, branch history is append-only. Squash locally before push, but do not replace published commits. |
| **Plan artifacts survive merge** | Planning artifacts (ACTIVE.md, SDD, memory) are on the primary branch after PR/MR merge. Deleting the branch post-merge loses nothing. |
| **Branch recovery** | After merge, `git checkout -b <branch> <merge-commit-hash>` reinstates the branch. Then merge the primary branch to bring it up to date. |

## Commit Strategy

- **Local commits are encouraged.** Commit freely for checkpoints, reverts, and experimentation. This thrash stays local.
- **Only the feature delivery reaches the primary branch.** Before raising a PR/MR, squash into a single clean commit (or one per logical change). Message format: `PL-<work-unit-id>: <summary>` when a work unit exists.
- **Push only when ready.** The branch is pushed only when the PR/MR is about to be created.

## Planning Artifact Lifecycle

When a project layer (`.adaptive-agents/planning/`) is present:

1. **Branch** from the primary branch after activation approval.
2. **Create** `ACTIVE.md`, `<work-unit>.sdd.md`, and `<work-unit>.memory.md` on the branch.
3. **Work** on the branch. Push only when ready for PR/MR.
4. **Sync** the primary branch into your branch before opening a PR/MR. Resolve conflicts. Re-run validation.
5. **PR/MR** to the primary branch. Planning artifacts merge as part of the same change.
6. **Delete** the local branch post-merge. Recovery is always possible (see Safety Properties).

### Exception: Urgent planning-only updates

If only planning artifacts change and the primary branch is unprotected or review is waived, a direct commit may be acceptable.

## PR/MR Workflow

The goal is a PR/MR that a human can approve in one read and the forge can automerge. The CLI tool that creates it is a convenience — what matters is the state of the branch and the quality of the description.

### Preparing the branch for automerge

1. **Sync**: Merge the primary branch into your branch. Resolve any conflicts.
2. **Validate**: Run any project-local checks — linters, tests, project-layer validator. All must pass.
3. **Squash and commit**: One clean commit with work unit reference.
4. **Push**: `git push -u origin <branch>`. The `-u` sets upstream tracking so IDEs like VS Code recognise the branch as published.

### Creating the PR/MR

Creating the PR/MR is a mechanical step. Use the appropriate tool if available and the user is present; otherwise present a ready-to-paste template.

| Situation | Approach |
|-----------|----------|
| `gh` available and authenticated | `gh pr create` with title + description |
| `glab` available and authenticated | `glab mr create` with title + description |
| Otherwise | Present a paste-ready PR/MR description |

Detect the forge with: `git remote get-url origin`.

### PR/MR description

The description should make review trivial:

- **Title**: Summarises what changed, not the branch name.
- **Body**: References the work unit ID (e.g., `Closes: PL-20260712-branch-development-guidance`).
- **Context**: One or two sentences on what was done and why.
- **Validation note**: Confirms the branch is synced, validated, and clean.

A human reading this can approve immediately. A forge with automerge rules can merge as soon as CI passes.

## Cross-Session Branch Awareness

A new session may load the primary branch by default. On session start:

1. List feature branches: `git branch --list 'pl-*'` (or the project's convention).
2. If an unmerged feature branch exists, check it out and load its `ACTIVE.md`.
3. If multiple exist, ask the user which to resume or close.

## Detection Heuristics Summary

| # | Signal | Method | Cost |
|---|--------|--------|------|
| 1 | README protection mention | `grep -i "branch is protected\|main.*protected" README.md` | Free, local |
| 2 | CONTRIBUTING conventions | Check `CONTRIBUTING.md` for PR/MR requirements | Free, local |
| 3 | CI infrastructure | `ls .github/workflows/` or `.gitlab-ci.yml` | Free, local |
| 4 | PR/MR templates | `ls .github/pull_request_template.md` or `.gitlab/merge_request_templates/` | Free, local |
| 5 | Forge API | Detect remote via `git remote get-url origin`; API check requires auth | Requires auth |
| 6 | Default fallback | Branch if uncertain | — |
