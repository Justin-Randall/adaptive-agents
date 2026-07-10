# Adaptive Agents

This repository is the canonical user-wide adaptive agent system.

For clarity, this file uses these terms:

* **Adaptive Agents repository**: the repository containing this file.
* **Current project repository**: the project the agent is currently helping modify, which may be a different repository.
* **User-wide guidance**: reusable preferences, skills, memories, agents, prompts, playbooks, and retrospectives intended to help across multiple projects.

## Purpose

The Adaptive Agents repository is not a normal application repository.

It is a versioned knowledgebase for coding agents. Its job is to help agents:

* discover relevant user-wide preferences
* apply reusable engineering standards
* select task-specific skills
* record retrospectives
* propose improvements to skills and memories
* avoid repeating known mistakes

## Repository Boundary Rules

Agents must not confuse the Adaptive Agents repository with the Current project repository.

When operating inside the Adaptive Agents repository:

* It is valid to create or modify files such as `INDEX.md`, `instructions/`, `skills/`, `agents/`, `prompts/`, `memory/`, `playbooks/`, `retrospectives/`, and `schemas/`.

When operating inside a different Current project repository:

* Treat the Adaptive Agents repository as read-only user-wide guidance.
* Do not create Adaptive Agents files or directories in the Current project repository unless explicitly instructed or applying the user-approved Project Layer bootstrap workflow.
* Do not create `skills/`, `memory/`, `retrospectives/`, `agents/`, `playbooks/`, or `schemas/` in the Current project repository merely because this file mentions them.
* Only modify files that belong to the Current project repository and are relevant to the user’s task.
* If a retrospective or memory should be captured, write it to the Adaptive Agents repository, not the Current project repository, unless the user explicitly asks for project-local notes.

An Adaptive Agents Project Layer is an explicit exception:

* It lives at `.adaptive-agents/` in the Current project repository or directory.
* It is project-owned guidance and planning, not a copy of this canonical user-wide repository.
* Bootstrap requires explicit user approval and must follow the routed bootstrap skill.
* Its own instructions override user-wide guidance when they are more specific.

## Discovery Protocol

Before doing non-trivial work:

1. Determine whether the current working directory is the Adaptive Agents repository or a different Current project repository.
2. Read this file.
3. Read `INDEX.md` in the Adaptive Agents repository if it exists.
4. Load only the instructions, skills, memories, agents, and playbooks relevant to the current task.
5. Prefer narrow, task-specific context over loading the entire Adaptive Agents repository.
6. If working inside another project, check for `.adaptive-agents/INDEX.md` and read its routed instructions and current planning context after the user-wide guidance.
7. Also read other project-local instructions that exist outside the Project Layer.
8. Project-local instructions override Adaptive Agents guidance when they are more specific.
9. Do not treat raw retrospectives as durable rules until they have been promoted.

## Operating Principles

* Prefer test-driven development for production code changes.
* Code must be testable. Its dependencies should be injectable.
* Read existing code and conventions before proposing changes.
* Do not invent APIs, file paths, project structure, or tool behavior.
* Verify claims against source code, local files, documentation, compiler output, tests, MCP output, or command output when possible.
* Prefer small, reversible changes.
* Preserve existing project style unless explicitly asked to refactor.
* Favor clean seams for testing: interfaces, factories, mocks, fakes, dependency injection, and narrow adapters.
* Capture reusable lessons after substantial work.

## Self-Improvement Rules

Agents may create retrospective notes.

Agents may propose new memories, skills, playbooks, or instruction updates.

Agents must not silently promote raw observations into durable instructions.

Durable changes should be promoted through an explicit review workflow.

Learning flow:

```text
retrospectives/inbox
  -> memory
  -> skills
  -> playbooks
  -> instructions
```

## Expected Adaptive Agents Root Structure

The Adaptive Agents repository should eventually contain:

```text
AGENTS.md
INDEX.md
README.md
instructions/
skills/
agents/
prompts/
memory/
playbooks/
retrospectives/
schemas/
```

These paths refer to the Adaptive Agents repository, not to arbitrary Current project repositories.

## Bootstrap Behavior

If `INDEX.md` does not exist in the Adaptive Agents repository, create it next.

`INDEX.md` is the top-level routing map that helps agents discover the right skill, memory, prompt, or playbook without reading the whole repository.

Until `INDEX.md` exists, agents should treat this file as the only authoritative Adaptive Agents entrypoint.

## Modification Rules

When modifying the Adaptive Agents repository:

1. Prefer adding narrow, focused files over expanding this file.
2. Keep `AGENTS.md` short and stable.
3. Put detailed workflows in `skills/`, `playbooks/`, or `prompts/`.
4. Put durable preferences and recurring project-agnostic patterns in `memory/`.
5. Put raw observations and session learning in `retrospectives/inbox/`.
6. Do not duplicate the same rule across many files unless it is intentionally repeated for discoverability.
7. When in doubt, add a retrospective note rather than modifying durable instructions.

When modifying a Current project repository:

1. Follow the Current project repository’s own local instructions.
2. Apply Adaptive Agents guidance only where relevant.
3. Do not copy Adaptive Agents structure into the Current project repository unless explicitly asked.
4. Do not store user-wide memories inside the Current project repository.

## Scope

The Adaptive Agents repository contains user-wide guidance.

It should not contain secrets, credentials, client-private data, proprietary source code, or large copied sections from external documentation.

Project-specific facts belong in the relevant project repository unless they are reusable across many projects.

## Next Step

Create `INDEX.md` in the Adaptive Agents repository root.
