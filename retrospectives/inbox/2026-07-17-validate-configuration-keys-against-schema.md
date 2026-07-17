# Retrospective: Validate configuration keys against product schemas

- Date: 2026-07-17
- Status: Captured
- Scope: User-wide
- Session or task: Correcting an installer setting after live integration testing falsified the first implementation

## Observation

An installer inferred a configuration key from documentation wording without verifying the exact registered setting in the product schema or source. Its health check repeated the same inferred key, so installation and validation agreed with each other while the product ignored the setting. A live test still displayed the permission prompt and exposed the false positive.

## Evidence

1. The installer wrote a plausible but unregistered configuration key derived from prose documentation.
2. The health check reported success because it validated the installer-authored value rather than an independently established product contract.
3. A fresh-session behavioral test contradicted the health result.
4. The product's public package schema, configuration definition, implementation, and unit tests identified a different exact key and clarified that it applies only to read-only tool calls.
5. After migrating to the schema-backed key, isolated tests passed for fresh installation, legacy-key removal, structured-config parsing, preservation, dry-run behavior, and idempotence.

## Impact

A self-consistent installer and checker can produce a convincing false pass when both share the same unverified assumption. This can leave integrations broken until users perform live dogfood, and it can overstate the scope of a setting when source behavior is narrower than documentation prose.

## Scope Decision

- Candidate: User-wide
- Rationale: Exact configuration-key validation applies across unrelated editors, CLIs, extensions, SDKs, and deployment tools whenever automation writes product-owned configuration.
- Project Layer considered: The failure concerns a general installer and validation method, not behavior unique to one project.

## Proposed User-Wide Target

A future promotion should update installer or coding guidance to require:

- verification of exact keys, types, and scope against an authoritative schema or source;
- a health check whose expected contract is independently established rather than copied from installer output; and
- a behavioral dogfood check for configuration that changes external product behavior.

Likely targets are `instructions/coding.instructions.md` or a focused installer-validation playbook.

## Promotion Decision

- Status: Captured
- Decision: Pending triage
- Rationale: The lesson is evidence-backed and reusable, but the narrowest durable target and wording have not been reviewed through the promotion workflow.

## Promotion Links

- None yet.
