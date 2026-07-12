# Process friction: SDD scope drift during active development

Status: Captured
Date: 2026-07-12
Work Unit: PL-20260712-branch-development-guidance

## Evidence

During development of the branch workflow guidance, the SDD's "Out of Scope" clause explicitly excluded user-wide promotion. Three design iterations later, the user requested exactly that promotion. The SDD had to be retroactively updated — its "Out of Scope" removed, Objective expanded, and Acceptance Criteria recast.

## Root Cause

The initial spec was written too narrowly. The problem (branch workflow conventions) was clearly repo-agnostic and durable from the outset, but the spec prematurely constrained it to project-layer only. This happened because the spec was written before exploring the design space with the user — the conversation about forge-agnostic, automerge-ready, safety properties, and cross-session awareness revealed scope that should have been visible at spec time.

## Lesson

When writing an SDD for a new durable instruction, don't prematurely constrain scope to "project-layer only." The spec should acknowledge the possibility of user-wide promotion when the content is repo-agnostic. A better pattern: write the spec as if it may go user-wide, use "initially project-layer" as a deployment constraint rather than a content constraint.

## Durable Guidance Impact

None directly. The `instructions/branch-workflow.instructions.md` is already user-wide. The insight is about SDD-writing practice, which may merit a note in `manage-planning/SKILL.md` or the SDD template if it repeats.
