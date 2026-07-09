# Adaptive Agents

`adaptive-agents` is a user-wide knowledgebase for agentic coding tools.

It stores reusable preferences, instructions, skills, agents, prompts, playbooks, memories, and retrospectives so coding agents can become more effective over time without duplicating project-specific setup in every repository.

## Goals

This repository is intended to help coding agents:

* apply user-wide engineering preferences
* discover relevant task-specific skills
* avoid repeating known mistakes
* run repeatable development workflows
* record lightweight retrospectives
* promote useful lessons into durable memories or skills
* stay out of project repositories unless explicitly instructed

## Important Terminology

This repository uses these terms consistently:

* **Adaptive Agents repository**: this repository.
* **Current project repository**: the codebase currently being modified.
* **User-wide guidance**: reusable guidance that applies across many projects.
* **Project-local guidance**: instructions that belong to a specific project.

When an agent is working inside another project, it should treat the Adaptive Agents repository as read-only guidance unless explicitly asked to update adaptive-agents.

## Current Tool Support

Initial focus:

* VS Code Chat / GitHub Copilot

Planned future integrations:

* OpenCode
* Claude Code
* GitHub Copilot CLI
* GitHub Copilot coding agent
* MCP-backed diagnostic agents
* other editor or terminal coding agents

---

# VS Code Chat / GitHub Copilot Setup

VS Code integration should be installed through a setup script rather than by manually copying instructions and editing settings.

The setup script should make VS Code aware of the Adaptive Agents repository as user-wide guidance while keeping ordinary project repositories clean.

## Install

From the Adaptive Agents repository root, run:

```bash
./scripts/install-vscode.sh
```

On Windows PowerShell, run:

```powershell
.\scripts\Install-VSCode.ps1
```

The exact scripts may vary by platform, but they should perform the same logical setup.

## What the VS Code Setup Does

The VS Code setup script should:

1. Detect the absolute path of the Adaptive Agents repository.
2. Create the VS Code-facing directory structure if needed.
3. Generate or update a VS Code user-wide instruction file.
4. Register the Adaptive Agents VS Code instruction directory with VS Code.
5. Preserve existing VS Code user settings where possible.
6. Avoid modifying unrelated settings.
7. Avoid copying Adaptive Agents files into ordinary project repositories.
8. Print a summary of what changed.

## Expected Generated Files

The script may generate files under:

```text
vscode/
```

For example:

```text
vscode/user-wide.instructions.md
```

This file is generated from the current local repository path and should not need to be edited manually.

## Expected VS Code Settings

The script should update VS Code user settings so Copilot Chat can discover Adaptive Agents instruction files.

At minimum, it should ensure the Adaptive Agents VS Code directory is included in the relevant VS Code instruction file locations setting.

The setup should be additive: if the user already has other instruction directories configured, they should remain configured.

## What the Setup Must Not Do

The VS Code setup script must not:

* copy Adaptive Agents directories into unrelated project repositories
* overwrite unrelated VS Code user settings
* store secrets or credentials
* require project-local changes
* assume a specific username or home directory layout
* require the repository to live at a specific path

## Verification

After running the setup script, open any project in VS Code and ask Copilot Chat something like:

```text
Use my Adaptive Agents guidance. What user-wide instructions are available for this task?
```

The expected result is that Copilot recognizes the Adaptive Agents repository as user-wide guidance and does not try to create Adaptive Agents files inside the current project.

## Project-Local Pointers

Most projects should not need any Adaptive Agents files copied into them.

If a particular project needs an explicit pointer, add a short project-local `AGENTS.md` or `.github/copilot-instructions.md` manually.

That project-local file should only point to the Adaptive Agents repository. It should not duplicate the Adaptive Agents structure.

## First Milestone

The initial working milestone is:

```text
AGENTS.md
README.md
INDEX.md
scripts/install-vscode.sh
scripts/Install-VSCode.ps1
vscode/user-wide.instructions.md
instructions/
skills/
memory/
retrospectives/inbox/
```

At that point, VS Code Chat / GitHub Copilot should have enough structure to:

1. discover user-wide preferences
2. avoid polluting project repositories
3. selectively load relevant guidance
4. support manual retrospectives
5. evolve toward skills and custom agents
