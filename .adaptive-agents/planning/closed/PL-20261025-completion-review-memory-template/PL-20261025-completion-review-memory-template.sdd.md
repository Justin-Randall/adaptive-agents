# PL-20261025: Add Completion Review to the Memory Template and Upgrade Existing Layers

- Status: Completed
- Work Unit: PL-20261025-completion-review-memory-template
- Origin: Direct

## Progress

- [x] Read the canonical and Project Layer planning guidance, memory template, and upgrade workflow.
- [x] Add the required completion-review record to the work-unit memory template and align canonical and Project Layer closure guidance.
- [x] Document the review-based upgrade path for existing layers and advance the Project Layer template version to 0.9.2.
- [x] Add LF checkout rules for shell scripts and prompt Markdown after Git Bash exposed line-ending failures.
- [x] Correct the dogfood and template validators for the documented retained closed-backlog source flow, with regression coverage.
- [x] Run Project Layer validation and the full health check under Git Bash; inspect the final changes.

## Objective

Require a recorded, concise completion review before closing planned work, and make the requirement available to new and existing Project Layers through the canonical template and review-based upgrade workflow.

## Specifications

### Problem Spec

The canonical planning skill now requires a completion review, but Project Layers use copied planning skills and a work-unit memory template that does not yet provide a consistent place to record that review. Existing Project Layers also need an explicit, approval-gated upgrade route for the new template material.

### Feature Specs

- Add a `## Completion Review` section to the canonical Project Layer work-unit memory template. It must record final-change review, acceptance-criteria evidence and gaps, engineering-quality assessment (clarity, maintainability, discoverability, scope, and semantic duplication), and the disposition of findings.
- Align canonical Project Layer `manage-planning` guidance and the end-work playbook with the required memory record and the rule that a blocking gap prevents closure.
- Keep user-wide planning guidance and the new Project Layer template behavior consistent.
- Extend the existing review-based upgrade guidance so an existing Project Layer can adopt the new section and guidance by an approved focused patch, without rewriting historical memories or closed packets.
- Keep shell scripts and prompt Markdown executable/readable under Git Bash checkouts.
- Align Project Layer validator behavior with the documented closure flow that retains an unindexed backlog source alongside its immutable closed-packet copy.

### Interface / Contract Specs

- Work-unit memories record the review under the exact heading `## Completion Review`.
- Bump the Project Layer template version to 0.9.2 only after the new template and guidance content is complete. Existing project upgrades retain the existing inspect, propose, approve, apply, and validate sequence.
- Existing active memory is updated with the review when that work is closed; historical closed memories are not retroactively rewritten.

## Applicable Guidance

- `.adaptive-agents/skills/manage-planning/SKILL.md` — activate direct work explicitly, keep plan and memory linked, and follow the end-work approval boundary.
- `.adaptive-agents/playbooks/end-work.md` — closure requires a proposed disposition and user approval; archive and verify before clearing active state.
- `instructions/planning-conventions.md` — Project Layer sizing, testing and DRY assessment conventions.
- `skills/upgrade-project-layer/SKILL.md` — upgrade existing layers through focused comparison and user-approved patches.
- `instructions/coding.instructions.md` — keep changes scoped, review the final work product, and validate claims against evidence.

## Test Plan

This is a documentation and template contract change with a focused validator correction required by the full-check failure. Run the Project Layer regression suite and full repository health check under Git Bash, and review the source diff for the required heading, prompts, version, upgrade steps, shell line-ending policy, and closed-backlog lifecycle behavior.

## User-Facing Surface

- Surface: Project Layer work-unit memory and closure workflow.
- Runtime scenario: Not applicable; this changes planning templates and instructions, not an application runtime.
- Endpoint or runtime: Not run.

## User-Facing Validation

- Agent proof: Complete for the documentation/template contract and shell execution; no application runtime is involved.
- Evidence: Git Bash full health check passed with 257 checks, 0 failures, and 0 warnings. The Project Layer regression suite passed 42/42. `.gitattributes` now enforces LF for shell scripts and prompt Markdown. The dogfood validator and template validator allow an unindexed backlog source retained in its closed packet, while still detecting indexed duplicate lifecycle records. `git diff --check` passed, and `template.json` parses with version `0.9.2`.
- User handoff: Closed as Completed with user approval on 2026-10-26.

## DRY Assessment

- Status: Required.
- Scope: The paired dogfood/template Project Layer validator changes and the repeated completion-review guidance across user-wide and Project Layer surfaces.
- Decision: Keep the validator correction duplicated in the dogfood layer and distributable template because they are independently maintained/deployed copies; centralizing this small check would add coupling without removing the need to ship both validators. Keep only the short completion-review requirement on each relevant skill/playbook surface and retain the detailed fields in the memory template.
- Result: Reviewed. The validator condition is narrow and equivalent in both copies; the test proves the retained-source case passes and an indexed duplicate remains rejected. Guidance repetition is intentional and semantically consistent. No additional extraction or duplication detector is warranted for this small documentation-plus-validator change.
- Intentional/deferred duplication: The dogfood and template validator copies must stay behaviorally aligned. The completion-review requirement is repeated briefly for discoverability; detailed review prompts remain centralized in the memory template.

## Scope

- Update the canonical Project Layer work-unit memory template, Project Layer planning and closure guidance, and upgrade instructions.
- Update the dogfood Project Layer copies and the Project Layer template version for the new additive template material.
- Enforce LF for shell scripts and prompt Markdown, and fix the discovered dogfood/template validator mismatch with focused regression coverage.
- Do not modify existing project-owned active or closed work-unit memories as part of the canonical template update.

## Acceptance Criteria

- [x] The work-unit memory template contains a concise required `## Completion Review` section with fields/prompts for all agreed review dimensions.
- [x] The canonical Project Layer planning and end-work guidance requires the recorded review and blocks closure when a blocking gap remains.
- [x] New Project Layers receive the updated template and guidance at the new template version.
- [x] The upgrade guidance tells existing Project Layers how to adopt the changes through a focused, approval-gated patch, without rewriting closed history.
- [x] Git Bash executes the shell and prompt checks with enforced LF endings.
- [x] The Project Layer validator permits the documented retained backlog-source closure flow and continues to reject indexed duplicate lifecycle records.
- [x] The full health check and regression suite pass.
- [x] Changes respect the existing user-owned working-tree edits and introduce no unrelated cleanup.

## Decisions

- Use `## Completion Review` as the stable record heading.
- Treat this as an additive documentation/template release at 0.9.2, following the current working-tree template version 0.9.1.
- Upgrade existing layers through the established review workflow; do not auto-migrate closed work-unit memories.
- Do not mark the dogfood `.adaptive-agents` layer as 0.9.2; its manifest remains 0.7.2, and this work does not complete a full approved upgrade from that version.

## Verification

- `git diff --check` — passed.
- Git Bash Project Layer regression suite — 42 passed, 0 failed.
- Git Bash full repository health check — 257 passed, 0 failed, 0 warnings.
- Shell execution diagnosis — the original Windows checkout used CRLF despite LF in the Git index, causing Bash `pipefail` parsing failures. Added `.gitattributes` rules for `*.sh` and `/prompts/*.prompt.md`; `git ls-files --eol` confirms `i/lf w/lf` for those files.
- Closed backlog source diagnosis — closure guidance retains the backlog source while the closed packet keeps an immutable copy. Updated the dogfood and template validators to treat only an unindexed source with a matching closed packet as historical, and added a regression case; indexed duplicates still fail.
- `templates/project-layer/template.json` — parsed successfully; `templateVersion` is `0.9.2`.
- New focused regression coverage was added for the retained closed-backlog source behavior.

## Supporting Documents

- [PL-20261025-completion-review-memory-template memory](PL-20261025-completion-review-memory-template.memory.md)
