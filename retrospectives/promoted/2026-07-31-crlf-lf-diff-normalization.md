# Retrospective: Normalize line endings before diffing template and layer files

- Date: 2026-07-31
- Status: Promoted
- Scope: User-wide
- Session or task: Review-based Project Layer upgrade 0.5.1 → 0.5.2

## Observation

During a Project Layer upgrade comparison, raw `diff` between the canonical template files and the local layer files reported a single full-file rewrite for files whose content was nearly identical. The cause was a line-ending mismatch: the canonical template ships CRLF while the local layer files use LF. The full-file diff made it look like wholesale replacement was needed and hid the real, small content changes.

## Evidence

1. `diff -u` on `skills/manage-planning/SKILL.md` reported one hunk spanning all 81→87 lines and 78 removed lines, yet a normalized comparison showed only two small localized additions.
2. `file` inspection confirmed the mismatch: template files reported "with CRLF line terminators" while local files reported plain ASCII text.
3. Re-running the diffs through `diff <(tr -d '\r' < local) <(tr -d '\r' < template)` exposed the true change set (a few added lines), enabling a targeted merge that preserved the layer's existing line endings and project-owned content.

## Impact

Agents comparing canonical guidance/template files against project copies on Windows must account for line-ending differences before concluding files differ or were rewritten. A normalized diff (strip `\r`) is the correct first diagnostic; copying a file wholesale to "match the template" can silently flip an entire tree's line endings and create noisy future diffs. This applies to any template-vs-instance or repo-vs-repo comparison workflow.

## Scope Decision

- Candidate: User-wide
- Rationale: Line-ending mismatches between a canonical source and its copies are a general Windows/Windows-Git worktree concern, not specific to any single project. The upgrade flow is review-based and used across all bootstrapped layers.
- Project Layer considered: The lesson is about how to compare files in general; no single project layer should carry it.

## Proposed User-Wide Target

- `skills/upgrade-project-layer/SKILL.md` — a note in the Inspect step to normalize line endings before diffing; possibly a general note in `memory/` about Windows line-ending comparisons.

## Promotion Decision

- Status: Promoted
- Decision: Promoted to upgrade-project-layer skill
- Rationale: Evidence-backed, verified diagnostic; line-ending normalization before diffing is the correct first step in template-vs-instance comparison and belongs in the owning upgrade skill's Inspect step.

## Promotion Links

- [Upgrade Project Layer skill](../../skills/upgrade-project-layer/SKILL.md) (Inspect step: normalize line endings before diffing)
