# Retrospective: Project Layer Template Links Must Respect Validator Boundaries

- Date: 2026-10-24
- Status: Promoted
- Scope: User-wide
- Session or task: Moving stack-specific browser guidance out of the Project Layer template

## Observation

A canonical Project Layer instruction was changed to link directly to a reusable instruction outside the generated `.adaptive-agents/` directory. The generated validator rejects links that escape the Project Layer root, so the new canonical template failed its own baseline validation. The appropriate pattern is to keep generated Project Layer links within the layer and name the installed guidance area to load, with user-wide routing maintained separately in the canonical Adaptive Agents repository.

## Evidence

- A template edit introduced a relative link from a generated Project Layer instruction to an external user-wide instruction.
- The Project Layer validator reported that the link escaped the Project Layer boundary, and the canonical health check failed.
- Replacing the external link with stack-guidance routing language restored template validation; the Project Layer regression suite and canonical health check then passed.

## Impact

Canonical templates must remain valid after rendering and must not depend on files absent from the generated project-owned layer. A validator failure can otherwise make every newly bootstrapped project appear structurally invalid, even when the referenced guidance exists in the agent's home repository.

## Scope Decision

- Candidate: User-wide
- Rationale: The shared Project Layer template and validator are used across unrelated projects, so this boundary constraint applies to future template changes generally.
- Project Layer considered: This is not specific to one project's runtime or workflow; it concerns the canonical template and the validator contract.

## Proposed User-Wide Target

Where in the canonical Adaptive Agents repository might this belong if promoted?

- `skills/update-adaptive-agents/SKILL.md`

## Promotion Decision

- Status: Promoted
- Decision: Promote the Project Layer link-boundary rule into the Adaptive Agents maintenance workflow.
- Rationale: Canonical templates generate project-owned layers used across unrelated repositories, and the validator enforces this boundary.

## Promotion Links

- [Update Adaptive Agents skill](../../skills/update-adaptive-agents/SKILL.md) — requires generated Project Layer template links to stay within the layer and the validator to run after changes.

## Resolution

- Status: Verified in the originating work
- Evidence: The canonical Project Layer regression suite passed with 41 tests, and the Adaptive Agents health check passed with 244 checks and no failures or warnings.

---

*After triage, move this note to `promoted/`, `deferred/`, or `rejected/` and update its status and promotion links.*
