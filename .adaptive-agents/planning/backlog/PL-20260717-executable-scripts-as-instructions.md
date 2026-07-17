# PL-20260717: Executable Scripts as Dynamic Instruction Sources

- Status: Backlog
- Readiness: Research
- Created: 2026-07-17
- Tags: research, instructions, skills, playbooks, architecture

## Objective

Research the feasibility of having executable scripts (e.g., `session-start.sh`) serve as dynamic instruction sources in the Adaptive Agents system. When a script's stdout contains actionable instructions, those instructions become part of the session context without requiring the agent to discover, load, and interpret separate playbook files.

## Problem Spec

Currently, instructions are static Markdown files. When the agent needs to perform a startup workflow (e.g., check for upgrades), the instructions must either:

- Pre-load the full workflow into every session (context bloat), or
- Tell the agent to read a separate file and follow it (discovery + loading overhead).

If the agent runs a script and the script's stdout can serve as instructions directly, then:

- No separate playbook loading step is needed — the instructions are already in context as tool output.
- New probes can be added to the script without changing any instruction files.
- The script itself becomes the instruction source, not a trigger that points elsewhere.

## Scope

1. Research whether VS Code Copilot (and other target tools) treat shell command stdout as effectively instructive — does the model reliably follow procedural instructions emitted by a script it ran?
2. Identify any tools where stdout from a shell command is truncated, ignored, or not treated as authoritative.
3. Compare against the current playbook-loading pattern: is there a reliability gap?
4. Document findings and recommend whether to adopt stdout-as-instructions as the primary pattern for `session-start.sh` and future dynamic probes.

## Out of Scope

- Implementing specific probes (upgrade check, health check, etc.) — those belong in their own work units.
- Changes to the instruction file format or routing.
