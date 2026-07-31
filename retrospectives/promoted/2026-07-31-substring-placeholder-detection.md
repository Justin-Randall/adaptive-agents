# Retrospective: Substring placeholder detection is fragile

- Date: 2026-07-31
- Status: Promoted
- Scope: User-wide
- Session or task: Making tests part of planning guidance; verifying Project Layer upgrade compatibility

## Observation

Empty-plan detection in the Project Layer upgrade inspector and both validator copies used a naive substring check — `"No Active Plan" in active_text`. A newly authored active plan quoted the phrase in prose several times (describing the exemption), so the inspector misdetected an active plan as empty, rendered placeholder work-unit paths, and skipped version-specific validation branches. The same fragility would let any real plan that mentions the phrase in prose silently skip validator requirements.

## Evidence

1. `inspect-project-layer-upgrade.sh --target .` reported "Active plan is empty" and listed `planning/active/PL-19700101-no-active-work.memory.md` as missing while a real active plan with a real work-unit memory existed.
2. The active `ACTIVE.md` contained the literal phrase "No Active Plan" four times inside spec and acceptance-criteria prose.
3. The instruction-load budget checker already used the anchored form (`active_text.startswith("# No Active Plan")`); aligning the inspector and validators to that anchor fixed the misdetection immediately, with all regression tests still passing.

## Impact

Sentinel and placeholder detection must anchor on structural markers (first line, heading pattern), never substring presence. A substring match conflates "document is the placeholder" with "document mentions the placeholder", which produces wrong tool behavior exactly when guidance documents talk about the placeholder — a common and recurring case.

## Scope Decision

- Candidate: User-wide
- Rationale: Every Adaptive Agents tool that inspects active plans (inspector, validators, budget checker) performs this detection; any project layer's plan can quote the placeholder phrase in prose.
- Project Layer considered: The buggy checks ship in the canonical template, so the fix and the lesson belong at the system level.

## Proposed User-Wide Target

- `scripts/check-adaptive-agents.sh` or `instructions/coding.instructions.md` (verification discipline): prefer anchored structural detection over substring matching for sentinels and placeholders.

## Promotion Decision

- Status: Promoted
- Decision: Promoted to instructions/coding.instructions.md
- Rationale: Lesson is durable, evidence-backed, and user-wide; the anchored-detection rule is now part of the coding standards.

## Promotion Links

- [coding.instructions.md](../../instructions/coding.instructions.md)
