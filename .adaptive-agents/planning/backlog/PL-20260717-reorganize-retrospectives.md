# PL-20260717: Reorganize retrospectives directory structure

- Status: Backlog
- Readiness: Research
- Created: 2026-07-17
- Tags: retrospectives, organization

## Objective

Reorganize the `retrospectives/` directory so the `inbox/` folder contains only unresolved notes. Promoted, deferred, and rejected retrospectives should live in sibling directories to provide a clear picture of how many items remain open.

## Problem Spec

The current `retrospectives/inbox/` contains a mix of all statuses — `Captured`, `Promoted`, `Deferred`, `Rejected`. A quick glance at the directory does not distinguish between "items that still need triage" and "items that have already been resolved." This makes it harder to prioritize, review, and ship the inbox.

## Scope

Define a new directory layout under `retrospectives/` (e.g., `inbox/`, `promoted/`, `deferred/`, `rejected/`), update the inbox README and template, and ensure all existing cross-references and routing remain valid.
