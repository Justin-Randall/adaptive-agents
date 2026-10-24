# Retrospective: Project Layer validator Bash wrapper failure

- Date: 2026-10-24
- Status: Captured
- Scope: User-wide
- Session or task: Closing a completed work packet and activating a backlog child in a Project Layer on Windows.

## Observation

The Project Layer validator Bash wrapper failed during a planning-only change. Running its unchanged embedded Python checker directly succeeded. The user reports this workflow had been working well for a while; this is a new occurrence, not an established pattern. The cause remains unknown.

## Evidence

- A tool invocation containing a long PowerShell command and a Bash validation call failed at process launch with an access-denied error. Subsequent inspection confirmed that invocation had not written the intended activation files. This launcher failure is distinct from the wrapper result below; no common cause was established.
- After the planning changes were applied in a separate invocation, running the validator through an explicitly selected Git Bash executable exited with code 1 and no actionable Bash diagnostics. A PowerShell filesystem-provider initialization warning was also present; its causal relevance is unknown.
- The agent read the existing Bash script, extracted its embedded Python checker without changing its logic, and supplied the same Project Layer root as its argument through an available Python 3 interpreter.
- The direct checker reported zero failures, including after the final planning evidence update. This proves that the checker passed via that invocation; it does not prove the Bash wrapper or launch environment was repaired.
- The user explicitly characterized this as newly observed after prior successful operation and requested global inbox capture.

## Impact

Validation required a fallback to complete planning verification. Misclassifying the incident as a persistent Bash limitation could cause unnecessary workflow changes or conceal a transient environment issue. Direct checker success should be distinguished from wrapper health.

## Scope Decision

- Candidate: User-wide
- Rationale: Explicit user instruction places this observation in the canonical global inbox. The shell/validator execution boundary may matter across projects, but cross-project recurrence has not been demonstrated.
- Project Layer considered: A project-local capture was considered; the user explicitly selected global scope instead. No project-specific names, personal paths, or proprietary logs are retained.

## Proposed User-Wide Target

- Not sure yet. Keep the observation in this inbox pending investigation. If repeated evidence establishes a general execution issue, review existing Windows shell-selection or command-failure guidance before proposing any change.

## Promotion Decision

- Status: Captured
- Decision: Capture only; no triage or promotion approved.
- Rationale: One newly observed incident in a previously working workflow, unknown root cause, and no established recurring pattern. Neither a default Python bypass nor a Bash policy change is justified by this evidence.

## Promotion Links

- None yet.

## Resolution

- Status: Pending verification
- Evidence: The embedded checker passed directly; the Bash wrapper failure itself remains unexplained and unresolved.
- Suggested dogfood check: At the next normal Project Layer validation on Windows, run the documented Bash wrapper first. Record executable selection, exit status, and bounded diagnostics if it fails. Compare with the same embedded Python checker and root only if needed. Do not declare recurrence or resolution without evidence.
