---
description: "Use when: running shell commands, diagnosing failed terminal/tool invocations, or deciding whether to retry a command."
---

# Command Failure Pivot Instructions

Use a retry budget for command-line failures. A command failure is meaningful when the tool returns a non-zero exit code, reports invalid arguments, rejects the shell syntax, cannot find expected files, or produces output that contradicts the intended diagnostic.

## Retry Budget

- After the first meaningful failure, read the error and identify the failure class before retrying.
- Do not run equivalent variants that only reshuffle flags, quoting, paths, or output filters unless the error clearly points to that exact fix.
- After two equivalent failures, stop varying the command line and pivot to a different diagnostic path.
- If a command succeeds but output is too noisy or not what was needed, prefer narrowing with a smaller command or reading generated output directly instead of rerunning broad variants.

## Pivot Strategy

When pivoting, choose one of these instead of another equivalent retry:

- Inspect the tool's help or usage for the exact subcommand and flag ordering.
- Split a compound command into smaller commands to isolate shell, path, tool, and output-processing failures.
- Use a simpler built-in diagnostic such as `git status`, `git diff --name-only`, `go test -run`, `task --list`, or the tool's native summary output.
- Redirect intentional intermediate output to the active workspace's approved scratch or temporary-output location, then inspect that file.
- Switch shells only when the failure class is shell-specific; account for differences between Bash, PowerShell, and Windows path syntax.

## Windows Shell Selection

When running Bash-oriented scripts on Windows, prefer a full Git Bash implementation over wrapper shells.

- If `git` is available, probe for Git Bash first and use it by default for `.sh` workflows.
- Keep PowerShell as the default for Windows-native command and tooling workflows.
- Treat `invalid option` failures from strict shell flags (for example `set -euo pipefail`) as shell-environment failures; pivot shells before retrying equivalent command variants.
- If Git Bash is unavailable, report the fallback shell and continue with the most compatible option.

## Tool Examples

The rule is general, but common examples include:

- For `git`, distinguish revision/pathspec parsing problems from actual repository state before trying more flags.
- For `go`, verify flag placement and package/test selection before rerunning coverage or test commands.
- For `task`, inspect `task --list` or the owning Taskfile before guessing task names or variable syntax.
- For `pwsh` and Bash, treat quoting, command substitution, and path syntax errors as shell-semantics issues, not tool failures.

## Reporting

When a pivot is needed, briefly state the failure class and the new diagnostic path. If the failure loop itself is reusable evidence, consider the retrospective capture triggers in [adaptation-cycle.md](../playbooks/adaptation-cycle.md).
