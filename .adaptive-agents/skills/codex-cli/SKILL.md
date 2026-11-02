---
name: codex-cli
description: "Use when: an AI agent needs to discover, invoke, or coordinate with OpenAI Codex CLI for bounded code exploration, implementation, tests, or dogfooding, especially when codex is not on PATH."
---

# Using Codex CLI from an Agent

Use Codex CLI as a supporting coding agent when its separate context or runtime behavior is useful. Keep the task bounded, preserve the current agent's ownership of the work, and verify all Codex-reported changes independently.

## Safety and coordination

- Do not pass credentials, secrets, or unauthorized source to Codex. Treat prompts and files in its working scope as potentially sent to the configured model provider.
- Check the worktree state before launching Codex. It may edit the same files as the calling agent; do not let concurrent agents modify overlapping files.
- State the objective, allowed files, constraints, and expected evidence in the Codex prompt. Prefer one bounded task over open-ended instructions.
- Never ask Codex to commit, push, or change global configuration unless the user explicitly requests it.
- Use read-only sandboxing for inspection and the narrowest write sandbox required for edits. Never use approval/sandbox-bypass flags as a shortcut. Only consider hook-trust bypass for disposable, isolated tests with fully inspected hook commands.
- Do not install or upgrade Codex or mutate the user's real Codex configuration without approval. Use temporary homes for installer tests.
- After Codex exits, inspect `git status` and the relevant diff, verify every claimed file/test result, and run the project's own checks. Codex's summary is not proof.

## Discover the CLI executable

1. Start with the active shell's normal command lookup:

   ```powershell
   Get-Command codex -All -ErrorAction SilentlyContinue
   where.exe codex
   ```

   ```sh
   command -v codex
   type -a codex
   ```

2. If not on `PATH`, query the installation source for its actual install location; never assume a path from another host or recursively scan the whole filesystem.

   **Windows Store desktop app:** use the registered package location and check the bundled CLI candidate:

   ```powershell
   $package = Get-AppxPackage -Name OpenAI.Codex
   if ($package) {
       $candidate = Join-Path $package.InstallLocation 'app\resources\codex.exe'
       if (Test-Path -LiteralPath $candidate) { $candidate }
   }
   ```

   **npm installation:** inspect the configured global prefix and package registration, then check only the prefix's executable location:

   ```powershell
   $prefix = (npm prefix -g).Trim()
   npm ls -g @openai/codex --depth=0
   @((Join-Path $prefix 'codex.cmd'), (Join-Path $prefix 'codex.exe')) |
       Where-Object { Test-Path -LiteralPath $_ }
   ```

   **Bash or zsh on macOS/Linux:** inspect the package manager used for installation and query npm's actual global prefix:

   ```sh
   prefix="$(npm prefix -g 2>/dev/null || true)"
   npm ls -g @openai/codex --depth=0 2>/dev/null || true
   for candidate in "$prefix/bin/codex" "$prefix/codex"; do
       if [ -n "$prefix" ] && [ -x "$candidate" ]; then printf '%s\n' "$candidate"; fi
   done
   ```

   For other package managers, use their metadata to locate the installed package or app, then inspect only its reported install prefix. For a desktop-bundled CLI, locate the installed app through that OS's application/package metadata and inspect only that app bundle. Do not assume the Windows Store layout applies.

   **WSL:** resolve Linux Codex independently with `command -v codex` and Linux package metadata. If the only installation is the Windows desktop package, use Windows PowerShell to resolve it; do not assume a Windows executable is a WSL-native CLI or that the two environments share `CODEX_HOME`.

3. Verify the candidate is a file and run its `--version`; then read that executable's `--help` before choosing invocation flags. Record both the resolved path and the discovery method. If no supported location resolves, report the blocker instead of guessing or installing another CLI.

## Run a bounded task

1. Confirm the selected Codex home, authentication source, working directory, and sandbox behavior. `--ephemeral` avoids persisted session files where supported; `--ignore-user-config` skips `CODEX_HOME/config.toml` but authentication still uses `CODEX_HOME`. Neither flag should be treated as a general guarantee that no state is read or written.
2. Use `codex exec --help` to verify options supported by the installed version. `codex exec` is non-interactive; the initial prompt can be passed as an argument or through stdin. Use `--cd` to set the workspace and a read-only sandbox for exploration. For changes, choose the narrowest write sandbox and ask for approval as required by the environment.

   Example read-only request after assigning `$codex` to the discovered executable and `$repo` to the authorized workspace:

   ```powershell
   & $codex exec --cd $repo --sandbox read-only --ephemeral "Inspect the focused test failures. Do not edit files. Report the likely cause and exact evidence."
   ```

3. Keep the Codex task within explicit boundaries, for example: “Inspect these test failures; do not edit files. Report the likely cause and exact evidence.” For implementation, name the allowed files and ask Codex to run only the relevant tests.
4. Review the output and all worktree changes independently. Run the relevant tests yourself; do not accept a reported test pass without command output.
5. If the required workflow is interactive (for example, an interactive compaction action), use the interactive CLI and its version-specific documented command. Do not present a non-interactive `exec` smoke test as equivalent.

## Project-specific checks

- For Codex installer or hook work, read the active project plan first. Use isolated temporary Codex homes for automated installation tests; real-profile installation or upgrades require explicit user approval and a preservation plan.
- For Total Recall compaction dogfood, follow the active plan's Codex surface and bounded event procedure. Verify captured events, adapter diagnostics, root-index checkpoint links, semantic-maintenance status, and graph validation. CLI evidence does not substitute for desktop acceptance when the active plan requires desktop testing.
- Do not modify or use the separate deterministic recall benchmark as evidence of live-model recall. Record the tested Codex surface/version, resolved executable path, commands, outcome, and remaining gaps in the active work memory.
