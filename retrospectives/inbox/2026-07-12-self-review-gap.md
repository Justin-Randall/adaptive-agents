# Retrospective: Self-Review Gap on Work Products

- Status: Captured
- Scope: User-wide

**Captured:** 2026-07-12

## Observation

After completing the Antigravity CLI SDD, the user asked me to critically review it before approving. That review immediately found 6 actionable issues (3 medium, 3 minor) that I could have caught myself — the research was solid, but the SDD had precision gaps and ambiguous language.

The same pattern occurred earlier with the Gemini CLI SDD where the user's feedback on CI assumptions and installer prerequisites led to corrections.

## Pattern

When I produce a significant work product (SDD, architecture doc, design spec), I **do** re-read it when prompted, but I don't proactively do a critical review pass before presenting it to the user. I tend to trust that "it looks right" because the components were individually correct.

## Lesson

A structured self-review checklist should be applied as the final step before presenting any work product for approval:

1. **Cross-reference claims** — verify each factual claim against the source (docs, code, reference implementations) rather than relying on memory.
2. **Check for ambiguity** — flag any "consider", "optional", "may" language and make it decisive.
3. **Verify completeness** — does every section from the template/playbook have content? Are there sections with placeholder text?
4. **Test edge cases** — what happens on first-run (no directories, no config)? On re-run? On missing prerequisites?
5. **Check for speculative leaps** — where is an assumption being treated as fact without a caveat?

## Promotion Candidates

- Add the self-review checklist to `instructions/coding.instructions.md` or as a step in the `manage-planning` skill's end-work workflow.
