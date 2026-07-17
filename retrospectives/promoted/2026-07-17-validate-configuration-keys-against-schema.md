# Retrospective: Verification must independently falsify claims

- Date: 2026-07-17
- Status: Promoted
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

## Durable Lesson

Verification requires evidence capable of disproving the claim. When deterministic checks exist, agents must run them and establish expected results from a contract or evidence independent of the implementation under test. Re-reading a changed artifact or checking output against the same assumptions that produced it is self-review, not verification.

The configuration incident is one concrete instance: exact keys, types, and scope must come from an authoritative schema or source, and a health check cannot establish correctness merely by finding what its installer chose to write.

## Promoted User-Wide Target

- `instructions/coding.instructions.md` — requires independent, falsifiable deterministic validation when available and distinguishes self-review from verification.

## Promotion Decision

- Status: Promoted
- Decision: Promoted to existing guidance
- Rationale: The failure mode is broader than product configuration and belongs in the already-routed default coding standard. A focused rule is sufficient; a new playbook would duplicate the existing TDD requirement for falsifying checks.

## Promotion Links

- [Coding instructions](../../instructions/coding.instructions.md)
