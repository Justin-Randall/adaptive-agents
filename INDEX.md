# Adaptive Agents Index

`INDEX.md` is the first-stop routing map for agents working with the Adaptive Agents repository. Use it to decide which guidance area to inspect next, then follow the authoritative rules in `AGENTS.md` and the setup overview in `README.md`.

## Repository Role

This repository stores user-wide guidance for coding agents. It is not an ordinary application repository and should not be copied into project repositories.

When working inside another project, treat Adaptive Agents content as reusable guidance unless the user explicitly asks you to update this repository.

## Start Here

| Need | Read |
| --- | --- |
| Agent operating rules, repository boundaries, bootstrap behavior | [AGENTS.md](AGENTS.md) |
| User-facing overview and VS Code setup expectations | [README.md](README.md) |
| Top-level routing for future guidance areas | [INDEX.md](INDEX.md) |
| Default user-wide engineering preferences for non-trivial coding work | [instructions/global.instructions.md](instructions/global.instructions.md) |
| Promoting retrospectives or updating Adaptive Agents guidance | [skills/update-adaptive-agents/SKILL.md](skills/update-adaptive-agents/SKILL.md) |
| Bootstrapping project-specific guidance and indexed planning | [skills/bootstrap-project-layer/SKILL.md](skills/bootstrap-project-layer/SKILL.md) |
| Reviewing structural upgrades for an existing Project Layer | [skills/upgrade-project-layer/SKILL.md](skills/upgrade-project-layer/SKILL.md) |
| Reusable Project Layer source | [templates/project-layer/template.json](templates/project-layer/template.json) and [template routing root](templates/project-layer/.adaptive-agents/INDEX.md) |
| Running the adaptation lifecycle | [playbooks/adaptation-cycle.md](playbooks/adaptation-cycle.md) |
| Using temporary diagnostics with searchable IDs and cleanup gates | [playbooks/temporary-diagnostic-logging.md](playbooks/temporary-diagnostic-logging.md) |
| Planning adaptive automation layers | [playbooks/adaptive-automation-roadmap.md](playbooks/adaptive-automation-roadmap.md) |
| Capturing raw session learning | [retrospectives/inbox/README.md](retrospectives/inbox/README.md) |
| Capturing a retrospective from a session observation | [prompts/capture-retrospective.prompt.md](prompts/capture-retrospective.prompt.md) |
| Reviewing a session for capture-worthy learning | [prompts/end-of-session-capture.prompt.md](prompts/end-of-session-capture.prompt.md) |
| Triage a captured retrospective without applying changes | [prompts/triage-retrospective.prompt.md](prompts/triage-retrospective.prompt.md) |
| Run a guided retrospective review session before user approval | [prompts/review-retrospective-session.prompt.md](prompts/review-retrospective-session.prompt.md) |
| Apply an approved retrospective promotion patch | [prompts/apply-approved-promotion.patch.prompt.md](prompts/apply-approved-promotion.patch.prompt.md) |
| Review the retrospective inbox queue | [prompts/review-retrospective-inbox.prompt.md](prompts/review-retrospective-inbox.prompt.md) |
| Review captured and deferred promotion candidates | [prompts/review-promotion-candidates.prompt.md](prompts/review-promotion-candidates.prompt.md) |
| Run deterministic repository health checks | [scripts/check-adaptive-agents.sh](scripts/check-adaptive-agents.sh) |
| Run Project Layer validator regression tests | [scripts/test-project-layer.sh](scripts/test-project-layer.sh) |

## Guidance Areas

These areas are expected to grow over time. Some directories may not exist yet while the repository is still in its bootstrap stage.

| Area | Purpose |
| --- | --- |
| `instructions/` | Durable user-wide rules and coding preferences for agents. |
| `skills/` | Task-specific workflows and domain knowledge that agents can load on demand. |
| `agents/` | Specialized agent definitions or role descriptions. |
| `prompts/` | Reusable prompt templates and task starters. |
| `memory/` | Promoted, durable lessons and preferences that apply across projects. |
| `playbooks/` | Repeatable engineering workflows and operational procedures. |
| `retrospectives/` | Raw observations and session learnings before promotion into durable guidance. |
| `schemas/` | Shared schemas for structured guidance, metadata, or validation. |
| `templates/` | Canonical reusable source trees for explicitly bootstrapped project-owned features. |
| `vscode/` | Generated or VS Code-facing integration files when setup scripts create them. |

## Default Instructions

For non-trivial coding work, load:

- [instructions/global.instructions.md](instructions/global.instructions.md)

This is the current checked-in entrypoint for default user-wide engineering guidance. It routes to the first instruction split:

- [instructions/repository-boundaries.instructions.md](instructions/repository-boundaries.instructions.md)
- [instructions/coding.instructions.md](instructions/coding.instructions.md)
- [instructions/tdd.instructions.md](instructions/tdd.instructions.md)
- [instructions/command-failure-pivot.instructions.md](instructions/command-failure-pivot.instructions.md)
- [instructions/temp-artifact-hygiene.instructions.md](instructions/temp-artifact-hygiene.instructions.md)

More specific instruction files may be added later for coding style, testing, Unreal Engine, Go, diagnostics, command-line tool behavior, or other recurring work.

## Skills

For Adaptive Agents repository maintenance, promotion, or routing changes, load:

- [skills/update-adaptive-agents/SKILL.md](skills/update-adaptive-agents/SKILL.md)

For creating a project-owned `.adaptive-agents/` Project Layer, load:

- [skills/bootstrap-project-layer/SKILL.md](skills/bootstrap-project-layer/SKILL.md)

For comparing an existing Project Layer with a newer canonical template, load:

- [skills/upgrade-project-layer/SKILL.md](skills/upgrade-project-layer/SKILL.md)

This skill covers promoting retrospectives, choosing durable guidance targets, using Markdown links between checked-in documents, and keeping generated bootstrap files disposable.

## Adaptation Lifecycle

For the end-to-end learning loop, use:

- [playbooks/adaptation-cycle.md](playbooks/adaptation-cycle.md)
- [playbooks/temporary-diagnostic-logging.md](playbooks/temporary-diagnostic-logging.md)
- [playbooks/adaptive-automation-roadmap.md](playbooks/adaptive-automation-roadmap.md)
- [playbooks/temp-artifact-hygiene.md](playbooks/temp-artifact-hygiene.md)
- [retrospectives/inbox/README.md](retrospectives/inbox/README.md)
- [retrospectives/inbox/template.md](retrospectives/inbox/template.md)

The lifecycle is capture first, triage second, and promote only when a lesson is durable, evidence-backed, and routed to the narrowest appropriate guidance area.

## Prompts

For assisted retrospective capture, use:

- [prompts/capture-retrospective.prompt.md](prompts/capture-retrospective.prompt.md)
- [prompts/end-of-session-capture.prompt.md](prompts/end-of-session-capture.prompt.md)
- [prompts/triage-retrospective.prompt.md](prompts/triage-retrospective.prompt.md)
- [prompts/review-retrospective-session.prompt.md](prompts/review-retrospective-session.prompt.md)
- [prompts/apply-approved-promotion.patch.prompt.md](prompts/apply-approved-promotion.patch.prompt.md)
- [prompts/review-retrospective-inbox.prompt.md](prompts/review-retrospective-inbox.prompt.md)
- [prompts/review-promotion-candidates.prompt.md](prompts/review-promotion-candidates.prompt.md)

These prompts capture one session observation into `retrospectives/inbox/`, review a session for capture-worthy learning, triage captured retrospectives without promoting them automatically, run a guided review session up to the user's approve/adjust/deny decision, apply only user-approved promotion patches, review the inbox queue, and recommend promotion candidates without editing files.

## Scripts

For deterministic repository health checks, run:

- [scripts/check-adaptive-agents.sh](scripts/check-adaptive-agents.sh)

The checker is read-only and validates prompt routing, retrospective statuses, promotion links, blocked private/raw link patterns, local Markdown links, and whether guidance Markdown files are reachable from `INDEX.md`.

## Current State

The repository is currently bootstrap-stage. `AGENTS.md` and `README.md` define the operating model, and this index provides the first routing layer. Missing directories are expected until guidance is added deliberately.

## VS Code / GitHub Copilot

VS Code integration should be installed through the setup flow documented in `README.md`. Generated VS Code-facing files should live under `vscode/` and should make the Adaptive Agents repository discoverable as user-wide guidance without modifying ordinary project repositories.

## Maintenance Notes

Keep this index concise. Prefer linking to the owning file or directory over duplicating detailed rules here. When adding a new top-level guidance area, update the routing table with its purpose and keep authoritative instructions in the owning document.
