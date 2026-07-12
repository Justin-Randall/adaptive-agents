# PL-20260712: Branch Development Guidance

- Work Unit: PL-20260712-branch-development-guidance
- SDD: [PL-20260712-branch-development-guidance.sdd.md](PL-20260712-branch-development-guidance.sdd.md)
- Memory: [PL-20260712-branch-development-guidance.memory.md](PL-20260712-branch-development-guidance.memory.md)
- Branch: `pl-branch-development-guidance`

## Objective

Define and document branch workflow conventions for the Adaptive Agents repository — first as a project-layer instruction, then promoted to user-wide guidance. Self-applying the branch-and-PR workflow for this work.

## Status

**Completed 2026-07-12** — All promotion patches applied. Branch workflow guidance promoted from project-layer to user-wide instruction. Project-layer redirect in place. Validation passes (0 failures). Closed as completed but available for dogfood-driven revisions.

## Completed Work

- [x] Create temp branch
- [x] Create SDD
- [x] Create memory.md
- [x] Update planning INDEX.md with active plan reference
- [x] Create `.adaptive-agents/instructions/branch-workflow.md`
- [x] Refine instruction: forge-agnostic PR/MR, automerge-ready philosophy, safety properties, commit strategy, cross-session awareness
- [x] Agree on promotion to user-wide guidance
- [x] Review and update all plan artifacts for correctness
- [x] Apply promotion patch set (user-wide instruction + INDEX.md + global.instructions.md + project-layer redirect)
- [x] Capture retrospective if process friction found

## Awaiting Dogfood

Branch `pl-branch-development-guidance` is at `origin`, committed and pushed. User is running the PR process. If dogfooding reveals issues or missing features, reactivate the plan and revise accordingly.

- [x] Merge `main` into branch (no merge needed — `main` had not advanced)
- [x] Squash and commit with work unit reference
- [x] Push branch to origin
- [ ] User opens PR/MR
- [ ] Dogfooding — if issues found, revise
- [ ] PR merges to `main`
- [ ] Delete local branch post-merge
