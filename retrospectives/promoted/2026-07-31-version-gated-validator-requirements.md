# Retrospective: Version-gate validator requirements for backward compatibility

- Date: 2026-07-31
- Status: Promoted
- Scope: User-wide
- Session or task: Making tests part of planning guidance; verifying Project Layer upgrade compatibility

## Observation

A patch release (0.5.2) added a new validator requirement — `## Test Plan` in `ACTIVE.md` — that would break existing Project Layers if they adopted the newer validator through the review-based upgrade flow before adding the required content. The fix was to version-gate the requirement: it activates only when the layer's `project-layer.json` `templateVersion` is at or above the version that introduced it, with a missing/unparseable version treated as an older layer.

## Evidence

1. A 0.5.1 fixture layer with the `## Test Plan` section stripped passes the new validator after the gate; the same fixture at 0.5.2 fails — proving the gate is the activation switch.
2. The upgrade path is review-based (`inspect-project-layer-upgrade.sh` is read-only; patches are user-approved), so a gated requirement is inert for older layers until content and version migrate together.
3. Two regression tests now cover the backward-compat cases (old version passes, missing version passes) alongside the forward case (current version fails without content).

## Impact

Template-driven validators must remain backward-compatible with lower-version layers. New content requirements should be opt-in via a version bump: the requirement activates only after the layer migrates content and its `project-layer.json` version together. This is a generalizable pattern for future template changes.

## Scope Decision

- Candidate: User-wide
- Rationale: The canonical template ships to every bootstrapped Project Layer; the version-gating pattern applies to any future template validation change.
- Project Layer considered: The change is in the canonical template, validators, and upgrade skill — system-level by definition.

## Proposed User-Wide Target

- `skills/upgrade-project-layer/SKILL.md` — the Backward Compatibility section added during this session; possibly `playbooks/` for the upgrade workflow.

## Promotion Decision

- Status: Promoted
- Decision: Promoted to existing guidance
- Rationale: The version gate, its documentation, and regression tests already exist (check-project-layer.sh `>= 0.5.2` gate, upgrade-project-layer skill Backward Compatibility section, and backward-compat fixtures in test-project-layer.sh). No new durable update is needed.

## Promotion Links

- [Upgrade Project Layer skill](../../skills/upgrade-project-layer/SKILL.md) (Backward Compatibility section)
