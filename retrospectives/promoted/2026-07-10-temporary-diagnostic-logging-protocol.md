# Retrospective: Temporary Diagnostic Logging Protocol

- Date: 2026-07-10
- Status: Promoted
- Scope: User-wide
- Session or task: Hierarchical character transform replication for spherical multiplayer

## Observation

During a complex multiplayer replication fix, the agent and user agreed on a temporary diagnostic logging protocol: each diagnostic log statement received a stable searchable ID (e.g., `DS_HIER_REPL D1`), was registered in the plan's diagnostic ledger with purpose/expected-evidence/removal-condition, and was removed once dogfood proof satisfied the exit criteria.

This workflow made it easy to:

- prove or disprove the working hypothesis without scattering ad-hoc logs
- correlate log output across multiple files and subsystems
- search and audit all active diagnostics with a single grep
- clean up every temporary log at the end with confidence nothing was missed

## Evidence

- Four diagnostics (D1-D4) were registered in the plan, each with a stable `DS_HIER_REPL D[1-4]` prefix, file location, purpose, and removal condition.
- Two-client dogfood produced clean evidence: D1 proved `BaseBodyId` retention across connect/reconnect/SOI/reconnect-on-different-body; D2 proved the local-controller gate blocked remote proxies; D4 proved correct body-relative composition.
- After dogfood passed, `grep -r "DS_HIER_REPL"` returned zero hits, confirming complete cleanup.
- All diagnostics removed in a single edit pass, followed by build and test validation (30/30 + 62/62 passes).

## Impact

Without this protocol, temporary logs tend to accumulate, become noise, or get left behind after the fix is proven. The structured approach (stable IDs + ledger registration + removal condition) makes temporary diagnostics predictable and disposable.

## Proposed Durable Target

- `playbooks/` — A lightweight playbook or instruction for running temporary diagnostic logging slices.
- `instructions/` — Could also fit as a sub-instruction under coding or TDD instructions.

## Promotion Decision

- Status: Promoted
- Decision: Promoted to a focused playbook after explicit user approval.
- Rationale: The pattern is a repeatable engineering procedure, not a tool-specific capability: stable IDs, a plan ledger, evidence collection, and cleanup on proof.

## Promotion Links

- [playbooks/temporary-diagnostic-logging.md](../../playbooks/temporary-diagnostic-logging.md)
