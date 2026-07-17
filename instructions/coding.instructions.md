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
- When a deterministic check exists, verification requires running it. The check must be capable of falsifying the claim, and its expected result must come from a contract or evidence independent of the implementation under test. Re-reading the changed artifact or checking output against the same assumptions used to produce it is self-review, not verification. When no deterministic check is available, use externally grounded evidence and report the validation limitation.
- Before reading from or writing to a derived file path, check whether the path (or its parent directory) actually exists. Handle the absence appropriately for the operation — creating the directory for a write, skipping the read for an optional cache, or reporting the error otherwise. Do not rely on blanket error suppression (`|| true`, empty `catch`, `except: pass`) to hide missing paths.
- Do not silently suppress errors from file, network, or process operations. Blanket suppression hides not just the expected failure but also unexpected ones — wrong paths, missing dependencies, corrupt data. If an error is expected and acceptable, handle it explicitly with a specific check or a narrow, documented exception.
- When changes affect project structure, setup commands, public workflows, prompt invocation, user-facing behavior, or discoverability, check whether `README.md` or other user-facing documentation needs to be updated. Do not describe aspirational files or workflows as implemented.
- Prefer small, reversible changes.
- Preserve project-local style unless explicitly asked to refactor.

## Completion Discipline

After the requested scope is complete and at least one focused validation has succeeded, run the completion-time retrospective checkpoint from [global.instructions.md](global.instructions.md), then stop and summarize. Do not repeat equivalent validation, readback, or status checks unless the latest result reveals a new issue, the task still has an unfinished requested step, the user asks for more detail, or a concrete blocker remains.

### Self-Review Before Presentation

Before presenting a work product (SDD, architecture document, design spec, implementation plan, or other deliverable) for user approval, run this structured self-review checklist. Self-review improves the work product but does not replace executable or externally grounded validation:

1. **Cross-reference claims** — Verify each factual claim against its source (docs, code, reference implementations) rather than relying on memory.
2. **Check for ambiguity** — Flag any "consider", "optional", "may", or otherwise non-decisive language and make it decisive.
3. **Verify completeness** — Does every section from the template, skill, or playbook have content? Are there sections with placeholder text or "TBD" markers?
4. **Test edge cases** — What happens on first-run (no directories, no config)? On re-run? On missing prerequisites?
5. **Check for speculative leaps** — Where is an assumption being treated as fact without a caveat or evidence?

Run the checklist immediately after completing the work product and before presenting it. This is distinct from the retrospective checkpoint below, which captures process-friction evidence after approval.

For multi-step tasks, validate each meaningful completed slice once, then continue to the next unfinished step. Do not rerun equivalent checks just to regain confidence.
