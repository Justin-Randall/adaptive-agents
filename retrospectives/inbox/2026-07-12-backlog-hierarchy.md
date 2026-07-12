# Retrospective: Backlog Hierarchy for Large Items

- Date: 2026-07-12
- Status: Promoted
- Scope: User-wide
- Work Unit: PL-20260710-project-layer-web-ui

**Captured:** 2026-07-12
**Promoted:** 2026-07-12

## Observation

The PL-20260710 Project Layer Web UI backlog item grew too large for a single activation — it covered Go scaffolding, React front-end, mDNS discovery, installer integration, CI, and more. The flat backlog format (one file per ID) had no way to decompose large items into session-sized work units.

## Evidence

- The spec went through 10+ design iterations in a single session, all in one file.
- Breaking it into 10 children (a–j) immediately made each piece fit one session.
- The directory hierarchy (`PL-YYYYMMDD-slug/PL-YYYYMMDDX-slug.md`) makes the epic-child relationship discoverable without parsing INDEX.md.
- The `Depends on:` field in children provides simple ordering.

## Impact

Without hierarchy support, any moderately complex feature becomes an unwieldy spec file that can't be activated or tracked. The flat backlog format works for items that fit in one session but fails for anything multi-session.

## Scope Decision

- Candidate: User-wide
- Rationale: The epic/child pattern is a generic planning convention applicable to any Project Layer, not specific to this repository. I verified it applies elsewhere when the user confirmed this applies to all Adaptive Agents work.

## Proposed Target

- `instructions/` — a new instruction file for planning conventions, or an addition to the branch-workflow instructions.
- The conventions have already been applied to this Project Layer's backlog INDEX.md and manage-planning SKILL.md as a dogfood.

## Promotion Decision

- Status: Promoted
- Decision: Promoted to `instructions/planning-conventions.md` and `templates/epic/EPIC.md`
- Rationale: User confirmed user-wide applicability. Conventions established via three design decisions:
  (1) guidance lives in user-wide instructions, not project-layer,
  (2) split heuristic is half the model's context window (512k for 1M, 128k for 256k),
  (3) children use the full epic slug as a prefix, no numeric suffixes needed.

## Promotion Links

- [instructions/planning-conventions.md](../../instructions/planning-conventions.md)
- [templates/epic/EPIC.md](../../templates/epic/EPIC.md)
