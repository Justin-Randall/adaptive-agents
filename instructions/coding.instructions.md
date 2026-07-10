---
description: "Use when: making code changes, reviewing implementation choices, or applying default coding standards."
---

# Coding Instructions

Default coding standards:

- Code must be testable.
- Dependencies should be injectable.
- Prefer interfaces, factories, mocks, fakes, dependency injection, and narrow adapters when they improve testability or reduce coupling.
- Read existing code before introducing new patterns.
- Do not invent APIs, paths, project structure, or tool behavior.
- Verify claims against source code, local files, documentation, compiler output, test output, MCP output, or command output where practical.
- When changes affect project structure, setup commands, public workflows, prompt invocation, user-facing behavior, or discoverability, check whether `README.md` or other user-facing documentation needs to be updated. Do not describe aspirational files or workflows as implemented.
- Prefer small, reversible changes.
- Preserve project-local style unless explicitly asked to refactor.

## Completion Discipline

After the requested scope is complete and at least one focused validation has succeeded, run the completion-time retrospective checkpoint from [global.instructions.md](global.instructions.md), then stop and summarize. Do not repeat equivalent validation, readback, or status checks unless the latest result reveals a new issue, the task still has an unfinished requested step, the user asks for more detail, or a concrete blocker remains.

For multi-step tasks, validate each meaningful completed slice once, then continue to the next unfinished step. Do not rerun equivalent checks just to regain confidence.
