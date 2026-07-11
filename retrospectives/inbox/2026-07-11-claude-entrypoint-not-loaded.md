# Retrospective: Claude entrypoint was not loaded at startup

- Date: 2026-07-11
- Status: Captured
- Scope: User-wide
- Session or task: Dogfooding a user-wide Claude Code integration

## Observation

A user-level instruction file contained prose directing Claude to read an external `AGENTS.md`, but the path was formatted as literal text rather than a native import. Generic prompts therefore did not receive the routed planning guidance, and an explicit request triggered a runtime file read that was rejected outside the allowed working directories.

## Evidence

1. The instruction file was loaded, but the external `AGENTS.md` content was absent from startup context.
2. Claude Code's documented `@path` syntax imports files at startup; paths inside code spans remain literal.
3. Claude Code documents `permissions.additionalDirectories` as the persistent access grant for files outside the active working directory.
4. After using a native absolute import and the narrow access grant, a fresh session outside the guidance repository returned the installation sentinel and routed a generic backlog question to the planning workflow.

## Impact

Stronger prompt wording could not overcome a client-enforced filesystem boundary. The integration appeared installed while failing the behavior it was intended to provide.

## Scope Decision

- Candidate: User-wide
- Rationale: Tool-native loading and external-directory boundaries recur in integrations used across unrelated projects.
- Project Layer considered: The failure occurs before project-specific routing and therefore is not confined to one Project Layer.

## Proposed User-Wide Target

- Installer guidance or a cross-tool integration playbook describing native entrypoint verification and narrowly required access settings.

## Promotion Decision

- Status: Captured
- Decision: Pending triage
- Rationale: The behavior is reproducible and supported by live verification, but no durable promotion has been approved.

## Promotion Links

- None yet.