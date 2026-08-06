---
name: jscpd
description: "Use when: detecting duplicated source code, measuring copy-paste duplication, or interpreting jscpd reports."
---

# jscpd

Use jscpd to identify duplicated source-code blocks and produce compact results an agent can inspect. This skill is a tool reference; use [dry-refactoring](../dry-refactoring/SKILL.md) only when the user also asks to remove duplication.

## Default command

Prefer the AI reporter because it lists file locations and summary metrics without embedding large code fragments:

```bash
npx --yes jscpd@5 --reporters ai <path>
```

Use an explicit version for reproducible work. The current `jscpd@5` package is the Rust-backed CLI and is substantially faster. `jscpd@4` is the Node/TypeScript engine and may be needed for legacy behavior or the Node programming API:

```bash
npx --yes jscpd@4 --reporters ai --gitignore <path>
```

Do not silently install a project dependency or commit generated reports. For an exploratory scan, write reports to a temporary directory or stdout. Check the package version and command exit status when the result will inform a quality gate.

## Useful options

| Option | Use |
| --- | --- |
| `--reporters ai` | Compact clone locations and duplication summary for agents |
| `.gitignore` behavior | jscpd v5 respects `.gitignore` by default; jscpd v4 exposes `--gitignore` |
| `--ignore "<globs>"` | Exclude generated, vendored, dependency, or fixture paths |
| `--format "javascript,typescript"` | Restrict the scan to selected formats |
| `--cross-formats "javascript,typescript"` | Compare related formats in one clone pool |
| `--min-lines <n>` | Ignore short duplicate blocks |
| `--min-tokens <n>` | Ignore small token-level matches |
| `--min-similarity <n>` | Require a similarity percentage from 1 to 100 |
| `--threshold <n>` | Make the command fail when duplication exceeds a percentage |
| `--output <path>` | Write reports to a selected directory |
| `--config <path>` | Load a project-specific `.jscpd.json` file |
| `--no-tips` | Suppress informational tips in automated output |

Start with the narrowest meaningful path. For a mixed JavaScript/TypeScript project, use `--cross-formats "js-ts"` or an explicit format group when ported code should be compared. Cross-format groups need at least two formats.

## AI reporter output

The reporter identifies the two source ranges and then prints a summary:

```text
src/a.ts:10-25 ~ src/b.ts:42-57
---
1 clones · 4.2% duplication
```

Read both ranges from the repository before drawing conclusions. A clone is evidence of similar tokens, not proof that the code should be unified. Check generated files, intentional repetition, tests, fixtures, and language boundaries before proposing a change.

## Configuration

A project may provide `.jscpd.json` when the scan is an established quality check. Keep exclusions explicit and review them with the project owner:

```json
{
  "threshold": 0,
  "reporters": ["ai"],
  "ignore": ["**/node_modules/**", "**/dist/**", "**/*.min.*"],
  "minLines": 5,
  "minTokens": 50,
  "output": "./reports/jscpd"
}
```

Do not add a threshold merely to make CI pass. First establish a baseline, decide which paths and formats are in scope, and verify that the exit behavior is useful for the project's workflow.
