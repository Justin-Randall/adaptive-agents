---
name: dry-refactoring
description: "Use when: removing duplicated code identified by jscpd, consolidating clone pairs, or planning a duplication-reducing refactor."
---

# Dry Refactoring

Use this workflow after [jscpd](../jscpd/SKILL.md) has identified duplication. Detection alone does not establish that two fragments have the same behavior or that an abstraction will improve the design.

## Workflow

1. Run a scoped jscpd scan with `--reporters ai`, respecting `.gitignore` and excluding generated or vendored paths.
2. Prioritize meaningful clones by line count, token count, or architectural impact rather than fixing every short match.
3. Parse each reported pair and read both source ranges plus their nearby call sites.
4. Confirm whether the fragments have the same behavior, inputs, error handling, lifecycle, and ownership.
5. Choose the smallest clear refactoring: extract a function, shared module, constant/configuration value, or template/base abstraction.
6. Write or update focused tests before changing behavior, and preserve intentional differences between the original sites.
7. Apply the refactor and update every affected call site, import, export, and test helper.
8. Run the narrowest relevant tests, then the project's normal static checks when warranted.
9. Rerun the same jscpd command and inspect the result. A lower count is not sufficient if the new abstraction creates confusing coupling or hides a changed behavior.
10. Repeat only for remaining high-value clones. Stop when the remaining duplication is intentional, low-value, generated, or not worth the added abstraction.

## Strategy guide

- **Extract a function** for repeated logic with stable inputs and outputs.
- **Extract a module or utility** when multiple domains need the same behavior and the ownership is genuinely shared.
- **Extract a constant or configuration value** for repeated data rather than repeated literals.
- **Use a template or base abstraction** only when the repeated structure represents a real, stable relationship; avoid inheritance solely to satisfy a clone report.

## Review cautions

- Test-file clones may indicate a useful fixture or helper, but extracting a helper can make tests harder to read. Prefer clarity over a zero-duplication score.
- Do not refactor generated, vendored, minified, or fixture files unless the project explicitly owns them.
- Clones across unrelated modules can signal coincidental syntax rather than shared responsibility.
- For JavaScript/TypeScript cross-format clones, consolidate the source of truth when appropriate instead of introducing a third shared copy.
- Keep a refactor separate from unrelated cleanup so focused tests and the post-change scan remain diagnostic.
- Preserve the original command, options, version, and scan scope when verifying the result.
