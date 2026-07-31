# Retrospective: Retrospective promotion apply errors recurred twice

- Date: 2026-07-31
- Status: Captured
- Scope: User-wide
- Session or task: Triaging and promoting inbox retrospectives (two sequential promotions)

## Observation

Two sequential retrospective promotions hit the same two mechanical errors:

1. **Stale frontmatter status line.** The promotion patch updated the `## Promotion Decision` section's `- Status:` to `Promoted`, but the document's frontmatter `- Status: Captured` (near the top) was left unchanged. The health checker reads the first `- Status:` line, so the promoted note failed validation as `Captured` in `promoted/`.
2. **Wrong relative promotion-link path.** The promotion link was written as `../instructions/...`, but the note moves from `retrospectives/inbox/` to `retrospectives/promoted/` — one directory deeper — so the correct path is `../../instructions/...`. The health checker reported `missing link target`.

Both errors occurred in the substring-placeholder-detection promotion and again, identically, in the submodule-push-order promotion.

## Evidence

1. `check-adaptive-agents.sh --verbose` reported `uses known status: Captured` and `FAIL: ... in promoted/ has status Captured but must be Promoted` for both notes after their patches.
2. `grep -c "^- Status:"` showed two `- Status:` lines per file — one `Captured` (frontmatter), one `Promoted` (Promotion Decision).
3. `missing link target: ../instructions/...` for both promoted notes; direct path resolution confirmed `retrospectives/promoted/../instructions/` does not exist while `retrospectives/promoted/../../instructions/` does.

## Impact

The promotion apply flow has two deterministic failure modes that the health checker catches but that should never reach the checker. The apply step should (a) update the single frontmatter `- Status:` line to match the destination directory's expected status, and (b) compute the promotion-link relative path from the destination directory (`promoted/`), not the source (`inbox/`).

## Scope Decision

- Candidate: User-wide
- Rationale: The promotion apply flow (`apply-approved-promotion.patch.prompt.md` and `update-adaptive-agents` skill) is used for every retrospective promotion across all projects.
- Project Layer considered: The failure is in the canonical promotion workflow, not in any single project layer.

## Proposed User-Wide Target

- `prompts/apply-approved-promotion.patch.prompt.md` — add explicit apply-step rules: update the frontmatter status line (single occurrence) and compute relative links from the destination directory.
- Possibly `skills/update-adaptive-agents/SKILL.md` validation guidance.

## Promotion Decision

- Status: Captured
- Decision: Pending triage
- Rationale: Recurred twice in one session with a deterministic fix; needs triage to decide the exact durable home.

## Promotion Links

- None yet.
