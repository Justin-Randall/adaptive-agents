# Backlog: User-Specific Project Guidance Layer

Plan: PL-20261025-user-specific-project-guidance-layer

Readiness: Needs Review: directory placement and discovery boundaries are undecided.

Test approach: Verify that user-specific guidance is discovered for the intended project and remains untracked, while tracked Project Layer guidance remains shared and unchanged.

## Objective

Provide a project-specific place for one user's local guidance and instructions that agents can discover without committing those personal preferences to the project repository.

## Problem Spec

The tracked Project Layer holds guidance shared by project contributors, while user-wide guidance applies across projects. A user working in a particular project may need private local instructions that belong to neither layer. Without a clear location and discovery contract, those instructions are either committed for everyone or kept in an ad hoc location agents may not find.

## Scope

In scope:

- Define ownership, content boundaries, and discovery/routing for user-specific guidance associated with a project.
- Ensure the guidance location is excluded from source control without hiding or weakening the tracked Project Layer.
- Resolve how agents distinguish user-specific project guidance from tracked project guidance and user-wide guidance.

Deferred:

- Whether the user-specific layer resides inside `./.adaptive-agents/` or in a separate hidden directory in the project. This placement is intentionally undecided and should be debated during planning.
- Tool-specific integration details until the location and discovery contract are agreed.

## Open Questions

- Should the user-specific layer be a local, ignored subdirectory of `./.adaptive-agents/`, or a separate hidden project directory?
- What should its minimal files and routing entrypoint be, and how should agents handle conflicts with tracked project guidance?
