---
name: manage-planning
description: "Use when: reading, executing, or changing the Project Layer active plan, working memory, backlog, or closed-work history."
---

# Manage Planning

Use [Planning](../../planning/INDEX.md) as the authoritative planning router.

## Start Work

1. Read `planning/active/ACTIVE.md` and its linked supporting documents.
2. If the current request changes the active objective, explain the conflict and ask whether to close, replace, or retain the current plan.
3. Work may originate from a backlog plan or begin directly as approved research, debugging, maintenance, or implementation.
4. Assign one canonical work-unit ID in `PL-YYYYMMDD-descriptive-slug` form. When activating a backlog item, reuse its filename stem; for direct work, derive the slug from the approved title.
5. Create `ACTIVE.md` with `- Work Unit: <work-unit-id>` and create `<work-unit-id>.memory.md`. Link the memory from `ACTIVE.md` and `planning/INDEX.md`.
6. **When activating a backlog item**, use its Objective, Problem Spec, Scope, and other details as source material for the SDD sections. If the backlog does not cover a required section, ask rather than inventing. Never overwrite the backlog item.
   - **If the item is an Epic** (`Status: Epic`), it cannot be activated directly. Identify which child to activate based on the current request and the epic's children index. Load the epic for architecture context and the child for the specific scope and AC.
   - **If the item is a child** (lives in an epic subdirectory), load its parent epic for architecture decisions and then the child for its Objective, Scope, and AC. Load both into the active plan context.
7. **When a backlog item grows too large during spec review** (its scope spans multiple independent deliverables that won't fit one session), propose splitting it into an epic with children. Create the epic directory, move the original spec into `PL-YYYYMMDD-slug.md`, and create focused child files. Update INDEX.md.
8. **When reopening prior work**, assign a new work-unit ID. Link the prior closed SDD and memory from the new plan, then seed new memory with only still-valid facts, unresolved issues, and restart context. Never modify or restore the closed memory wholesale.
9. Never activate work silently.

## Record Deferred Work

1. Keep out-of-scope discoveries in the active `<work-unit-id>.memory.md` while evaluating them.
2. Scan `planning/backlog/INDEX.md` before opening detailed backlog plans.
3. Propose updating a matching detailed plan or creating a new `PL-YYYYMMDD-descriptive-slug.md` plan (or legacy `PL-YYYYMMDDTHHMMSSZ-...`, `PL-####-...`).
4. **Keep backlog items lightweight.** A backlog entry needs only an Objective, a Problem Spec, and a one-line Scope. The full SDD specification is written into `ACTIVE.md` during activation, not before. This keeps the backlog easy to scan and reduces stale-spec risk.
5. Wait for approval before changing the backlog index or detailed plans.

## Maintain Active Context

- Keep progress, acceptance criteria, decisions, and verification in `ACTIVE.md`.
- Curate the active `<work-unit-id>.memory.md` for handoff-critical state; replace stale details instead of appending a session transcript.
- Link every active supporting Markdown document from `ACTIVE.md`.

## Execute Work

Before executing work, load the project's relevant rules and apply them.

### Apply Project Rules

- Read the active plan's `## Objective`, `## Specifications`, `## Acceptance Criteria`, and `## Scope`.
- Load the rules defined in the project's instructions, skills, playbooks, and user-wide guidance. These encode the user's desired engineering standards, testing preferences, coding conventions, and process expectations.
- **Capture the relevant rules into the plan.** Add or update a `## Applicable Guidance` section in `ACTIVE.md` with short descriptions of each rule and a reference (file path, instruction name, or skill name) to its authoritative source. This makes the rules visible to anyone executing the plan without requiring re-discovery.
- The rules that apply depend on the project, not on this skill. Check what exists rather than assuming specific practices.
- Satisfy the acceptance criteria by fulfilling the spec; do not over-scope.

### Apply the Spec (SDD)

- The `## Specifications` section defines *what* must be built. Let it drive implementation order.
- When a spec item is ambiguous, stop and ask rather than inventing.

### Verification Discipline

- Verify claims against source code, local files, documentation, compiler output, test output, MCP output, or command output where practical.
- Do not invent APIs, file paths, project structure, or tool behavior.
- When changes affect project structure, setup commands, public workflows, or user-facing behavior, check whether `README.md` or related documentation needs updating.

### Repository Boundary Awareness

- Know which repository you are operating in. Adaptive Agents rules about repository boundaries apply during plan execution.
- In the Adaptive Agents repository: modifying planning artifacts, instructions, skills, and templates is in scope.
- In a Current project repository: treat the Adaptive Agents repository as read-only guidance; do not create Adaptive Agents structure unless performing a user-approved bootstrap.

### Change Discipline

- Prefer small, reversible changes.
- Preserve existing project style unless explicitly asked to refactor.
- Do not fix unrelated bugs or broken tests unless explicitly asked.
- Make changes that serve the spec and nothing more. Out-of-scope discoveries belong in the active work-unit memory's deferred discoveries.

### Completion Retrospective

- When work appears complete, run the retrospective checkpoint from the global instructions before summarizing.
- If process-friction evidence exists (failed approaches, retries, discarded hypotheses, user corrections, rollbacks), propose a sanitized `Captured` retrospective.
- Never promote retrospective observations into durable instructions without user approval.

## End Work

Follow [End work](../../playbooks/end-work.md). Closure, disposition, backlog continuations, and subsequent work all require user approval.

Run `bash .adaptive-agents/scripts/check-project-layer.sh` after planning structure changes.