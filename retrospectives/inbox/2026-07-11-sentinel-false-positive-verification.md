# Retrospective: Sentinel checks can false-positive when installers copy guidance

- Date: 2026-07-11
- Status: Captured
- Scope: User-wide
- Session or task: Reworking the OpenCode installer after a completed-then-reopened integration

## Observation

An earlier tool integration was closed as verified because sessions returned the installation sentinel. Dogfooding later showed the sentinel came from an installer-generated local copy of the guidance file that re-defined the sentinel — the tool had never read the canonical repository. Separately, the tool's permission model blocked reads outside the working directory by default, so even loaded routing instructions could not be followed, and stale artifacts at a wrong, never-consumed config destination muddied diagnosis across a full plan cycle.

## Evidence

1. The installed copy contained the sentinel string, so the model could echo it without any canonical repository access.
2. Official tool documentation confirmed external-directory tool calls default to ask-per-use; no persistent grant had been configured.
3. After reworking to a single native config entry loading the canonical file plus a narrow read/write directory grant — and deleting the copy — a fresh session passed the sentinel, a content-proof probe, and a write-back probe.
4. A health-check bug was found in passing: stripping JSONC comments with a naive pattern corrupts URL strings; comment removal must be string-aware.

## Impact

A false "verified" state persisted through plan closure and required a reopen. Verification that relies on a string the installer itself distributes proves distribution, not integration.

## Scope Decision

- Candidate: User-wide
- Rationale: Sentinel-style verification and permission-gated external reads recur across every agent-tool integration, not one project.
- Project Layer considered: The failure occurs in user-level tool configuration before any project routing.

## Proposed User-Wide Target

- The cross-tool integration contract and installer verification guidance: require a three-probe dogfood (sentinel, content-proof probe answerable only from repository content, routed write-back) across fresh sessions, and forbid installers from distributing any file that re-defines the sentinel.

## Promotion Decision

- Status: Captured
- Decision: Pending triage
- Rationale: The three-probe protocol and installer duties were already applied to the backlog contract and README during the plan; a durable promotion into instructions or a playbook has not been reviewed.

## Promotion Links

- None yet.
