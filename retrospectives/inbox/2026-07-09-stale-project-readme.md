# Retrospective: Project README becomes stale after active sessions

- Date: 2026-07-09
- Status: Promoted
- Session or task: Updating the Adaptive Agents root README.md to reflect current repository state

## Observation

After a period of active development, the project root README.md drifted out of sync with the actual repository contents. It referenced files that did not exist (e.g., `scripts/Install-VSCode.ps1`), described setup behavior as aspirational rather than implemented, and omitted several guidance areas that had been added (prompts, playbooks, memory, schemas, agents). The README had to be rewritten from scratch to match what was actually in the repository.

## Evidence

- The README mentioned a PowerShell installer (`scripts/Install-VSCode.ps1`) that does not exist in the repository.
- The "First Milestone" section listed a set of files that was both incomplete and partially aspirational.
- Several guidance areas (`prompts/`, `playbooks/`, `memory/`, `schemas/`, `agents/`) existed in the repository but were not described in the README.
- The adaptation lifecycle workflow and prompt invocation patterns were not documented.
- The README was rewritten in a single session to align with the current state.

## Impact

A stale root README undermines the repository's purpose as a discoverable knowledgebase. New users (human or agent) cannot quickly understand what is available, how the system works, or how to use it. This increases friction for onboarding, reduces trust in the documentation, and makes it harder to dogfood the adaptation lifecycle.

## Proposed Durable Target

- `instructions/`

## Promotion Decision

- Status: Promoted
- Decision: Promote with proposed patch.
- Rationale: The lesson is durable across ordinary project work, not only Adaptive Agents maintenance. The narrowest durable target is the general coding instructions because agents should check user-facing documentation whenever changes affect project structure, setup commands, public workflows, user-facing behavior, or discoverability.

## Promotion Links

- [Coding instructions](../../instructions/coding.instructions.md)
