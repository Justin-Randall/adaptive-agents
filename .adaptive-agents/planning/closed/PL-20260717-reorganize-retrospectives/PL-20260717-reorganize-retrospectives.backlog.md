# PL-20260717: Reorganize retrospectives directory structure

- Status: Backlog
- Readiness: Ready
- Created: 2026-07-17

## Objective

Reorganize the `retrospectives/` directory so the `inbox/` folder contains only notes awaiting initial triage (status `Captured`). Promoted, deferred, and rejected retrospectives live in sibling directories so a glance at the directory tree reveals how many items remain open.

## Problem Spec

The current `retrospectives/inbox/` contains a mix of all statuses — 14 `Promoted`, 9 `Captured`, 1 `Deferred`, 0 `Rejected` (as of 2026-07-17). A quick glance at the directory does not distinguish between "items that still need triage" and "items that have already been resolved." This makes prioritization, review, and inbox shipping harder than necessary.

## Scope

Reorganize the retrospectives directory: create sibling directories for promoted, deferred, and rejected notes; update checkers, templates, and migration script; wire into upgrade skill.
