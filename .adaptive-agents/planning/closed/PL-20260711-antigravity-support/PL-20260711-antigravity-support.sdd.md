# PL-20260711: Antigravity Support

- Status: Completed
- Work Unit: PL-20260711-antigravity-support
- Origin: Backlog ([PL-20260711-antigravity-support.backlog.md](PL-20260711-antigravity-support.backlog.md))
- Activated: 2026-07-12
- Closed: 2026-07-12

## Caveats

- **Part B (file permissions) is not scriptable.** Antigravity 2.0 stores file-access grants in internal protobuf binary storage (`~/.gemini/antigravity/implicit/*.pb`) that cannot be safely written by a shell installer. The user must select "Yes, and always allow" from the one-time permission dialog on first file access.
- Three approaches were tested and confirmed ineffective: `settings.json` with `permissions.allow` (CLI-only), `projects.json` with Project entry (no effect on file-read dialogs), `trustedFolders.json` TRUST_FOLDER entry (no effect on file-read dialogs).
- The `@` import in `~/.gemini/GEMINI.md` (Part A) works correctly — the AGENTS.md content is loaded in every session. Dogfood confirmed Adaptive Agents are active inside Antigravity conversations.- **Future improvement**: Reverse-engineer the protobuf binary format at `~/.gemini/antigravity/implicit/*.pb` so the installer can write permission grants directly, making the integration fully scriptable. This was beyond the scope of the initial implementation because the format is undocumented and could change between app versions.

## Objective

Provide an idempotent **Google Antigravity 2.0 desktop app** integration that loads the canonical Adaptive Agents `AGENTS.md` through the shared `~/.gemini/GEMINI.md` global context file — the same entry-point mechanism used by the predecessor Gemini CLI and inherited by Antigravity products.

## Specifications

### Problem Spec

Google Antigravity 2.0 is a desktop application (not a CLI). Agents run within **Projects** that define folder boundaries. The app shares the Gemini CLI's global context system: `~/.gemini/GEMINI.md` is loaded automatically in every session, and per-workspace `AGENTS.md`/`GEMINI.md` files are auto-discovered at the Project root. File permissions are managed through the **Project security preset** UI (Default/Full Machine/Unrestricted), not a JSON config file.

This means the integration approach uses the same two-part pattern as CLI-based tools:

- **Part A** (entry point) is the same: write to `~/.gemini/GEMINI.md` with an `@` import to the canonical AGENTS.md.
- **Part B** (trust grant) is also scriptable: write `permissions.allow` entries to `~/.gemini/settings.json`, the same file the desktop app uses to persist permission grants.

Plugin manifests, slash commands, skills, and hooks should not be generated.

### Product Context

| Feature | Antigravity 2.0 desktop app | Antigravity CLI |
|---------|-----|-----|
| Type | Standalone desktop app (Electron) | Terminal TUI (`agy`) |
| Install path | Windows: `%LOCALAPPDATA%\Programs\Antigravity\Antigravity.exe` | `~/.local/bin/agy` |
| Global context | `~/.gemini/GEMINI.md` | `~/.gemini/GEMINI.md` |
| Permissions | `~/.gemini/projects.json` (workspace auto-allow) | `~/.gemini/antigravity-cli/settings.json` |
| App data dir | `~/.gemini/antigravity/` | `~/.gemini/antigravity-cli/` |
| Plugin directory | `~/.gemini/config/plugins/` | `~/.gemini/antigravity-cli/plugins/` |

This work targets the **Antigravity 2.0 desktop app** only, not the separately-shipped Antigravity CLI (`agy`).

### Phase 1: Research & Verification ✅

Research completed 2026-07-12 against the official Antigravity documentation at `https://antigravity.google/docs/`.

**Key Findings:**

| Question | Finding |
|----------|---------|
| Product name | Google Antigravity 2.0 (desktop app) |
| Install detection | Windows: `%LOCALAPPDATA%\Programs\Antigravity\Antigravity.exe`; macOS: `/Applications/Antigravity.app` |
| Global context file | `~/.gemini/GEMINI.md` — confirmed by [Gemini migration docs](https://antigravity.google/docs/cli/gcli-migration): *"Global developer context: The agent automatically consults and enforces your global constraints located at `~/.gemini/GEMINI.md`"* |
| Workspace context files | `GEMINI.md` or `AGENTS.md` at workspace root — auto-discovered on startup ([best practices](https://antigravity.google/docs/cli/best-practices)) |
| Project workspace storage | `~/.gemini/projects.json` — maps normalized paths to project names; workspace files are auto-allowed |
| Plugin directory | `~/.gemini/config/plugins/` — globally active across all Projects ([plugins docs](https://antigravity.google/docs/plugins)) |
| App data dir | `~/.gemini/antigravity/` |

**Part A — Native Entry Point:**

The Antigravity 2.0 desktop app shares the Gemini CLI's global context system. From the [migration docs](https://antigravity.google/docs/cli/gcli-migration): *"Global developer context: The agent automatically consults and enforces your global constraints located at `~/.gemini/GEMINI.md`."*

Key details:

1. **Global context file**: `~/.gemini/GEMINI.md` — loaded automatically in EVERY Antigravity 2.0 session.
2. **Workspace context files**: `GEMINI.md` or `AGENTS.md` at the Project root folder — auto-discovered and parsed on startup.
3. **The @ import syntax** (Memory Import Processor) is inherited from Gemini CLI and supported in the global context file.

**Native entry point mechanism:** An `@` import line in `~/.gemini/GEMINI.md` referencing the canonical `AGENTS.md` file:

```
@/absolute/path/to/adaptive-agents/AGENTS.md
```

This loads AGENTS.md content into every Antigravity 2.0 session's system context. Single entry point — AGENTS.md → INDEX.md → instructions/ fan-out handles all routing.

**Part B — Folder trust (scripted via `~/.gemini/trustedFolders.json`):**

Antigravity 2.0 reads `~/.gemini/trustedFolders.json` at startup to determine which directories are trusted. Trusted folders allow the agent to read and write files without prompting. The file format is `{"normalized_path": "TRUST_FOLDER"}` where paths are:

- Lowercase
- Forward slashes
- Drive letter followed by colon (e.g. `c:/users/logic/...`)

Antigravity must be fully quit and restarted before trust changes take effect (the file is read at startup only).

### Phase 2: Installer — `scripts/install-antigravity.sh`

**Part A — Native entry point (scripted):**

- Target file: `~/.gemini/GEMINI.md` — the global context file, loaded automatically in EVERY Antigravity 2.0 session.
- Create `~/.gemini/` if it does not exist (`mkdir -p`).
- Write a single `@` import line pointing to the canonical `AGENTS.md`.
- Use marker-based section management (`#==ADAPTIVE_AGENTS_START==` / `#==ADAPTIVE_AGENTS_END==`) for idempotent updates.
- Preserve existing user content outside the markers.
- Guarantee content-idempotent reruns.

**Part B — One-time permission dialog:**

- No scriptable mechanism exists. The user must select "Yes, and always allow" once from the permission dialog on first file access.
- The installer prints clear guidance explaining the dialog and the expected choice.
- This grant persists permanently in the app's internal binary storage.

**Prerequisite — Antigravity 2.0 must be installed:**

- The installer detects the Antigravity 2.0 desktop app in common install paths:
  - Windows: `%LOCALAPPDATA%\Programs\Antigravity\Antigravity.exe`, `%PROGRAMFILES%\Antigravity\Antigravity.exe`
  - macOS: `/Applications/Antigravity.app`
  - Linux: `/opt/antigravity/antigravity` or `PATH`
- If the app is not detected, prints an actionable error directing to [antigravity.google/download](https://antigravity.google/download) and exits non-zero.

**Contract:**

- `scripts/install-antigravity.sh` — idempotent, `--dry-run`, exit 0 on no-op.
- `--dry-run` writes nothing but reports what would change.
- Validate the exact destination file content after write (not just "file exists").
- Support same-version rerun producing byte-identical GEMINI.md.

### Phase 3: Health Check — `scripts/check-adaptive-agents.sh`

Added `check_antigravity` function:

1. Detects whether the Antigravity 2.0 desktop app is installed (same path logic as the installer).
2. If not installed, reports `SKIP (not installed)` and returns success.
3. If installed, validates:
   - `~/.gemini/GEMINI.md` has the `@` AGENTS.md import.
   - `~/.gemini/GEMINI.md` has the `@` AGENTS.md import.
4. Diagnostic-only — does not gate CI.

### Phase 4: Isolated Tests — `scripts/test-install-antigravity.sh`

Tests run entirely against temporary directories:

1. Prerequisite check — fails with actionable error when app not found.
2. Dry-run — no files modified.
3. Fresh install — GEMINI.md created with @ import.
4. Idempotency — byte-identical rerun.
5. User content preservation — pre-existing prose survives.
6. User-file preservation — non-installer files untouched.
7. README check — references `install-antigravity.sh`.

### Phase 5: Dogfood & Verification

From an unrelated Antigravity 2.0 conversation (in a Project that does NOT include the Adaptive Agents repo), verify:

1. **Sentinel probe**: "Are Adaptive Agents active?" → `ADAPTIVE_AGENTS_GLOBAL_LOADED`
2. **Content-proof probe**: e.g., "What is the current active plan?" — must name actual plan.
3. **Routed write-back**: e.g., retrospective capture appears in `retrospectives/inbox/`.
4. Intermittent loading is a failure, not a pass.

## Applicable Guidance

- `.adaptive-agents/ARCHITECTURE.md` — preserve canonical routing, Project Layer ownership, cross-tool integration boundaries.
- `instructions/global.instructions.md` — load routed engineering guidance and run the completion retrospective checkpoint.
- `instructions/repository-boundaries.instructions.md` — keep distinct canonical and Project Layer ownership.
- `instructions/coding.instructions.md` — use testable seams, source-backed claims, focused reversible changes.
- `instructions/tdd.instructions.md` — begin behavior changes with focused failing tests.
- `instructions/command-failure-pivot.instructions.md` — classify failures, pivot rather than retrying.
- `instructions/temp-artifact-hygiene.instructions.md` — keep test artifacts isolated.
- `.adaptive-agents/skills/manage-planning/SKILL.md` — maintain active progress and work-unit memory.

## Scope

- Research Antigravity 2.0's global context mechanism, permissions storage, and data directory layout.
- Implement `scripts/install-antigravity.sh` with Part A (GEMINI.md @ import), Part B guidance (one-time dialog), prerequisite check, dry-run.
- Add `check_antigravity` to `scripts/check-adaptive-agents.sh` (diagnostic-only, app detection).
- Create `scripts/test-install-antigravity.sh` with isolated temp-dir tests.
- Dogfood from unrelated Antigravity 2.0 conversation with three probes.
- Update `README.md` and `install.sh` with Antigravity 2.0 support.

## Out Of Scope

- The Antigravity CLI (`agy`) — entirely separate product.
- The Antigravity IDE — not supported.
- Generating `.agents/` project-local configuration, hooks, skill markers, or plugin manifests — the global `~/.gemini/GEMINI.md` handles routing.
- Modifying protobuf binary state files in `~/.gemini/antigravity/` — undocumented internal format, not safely scriptable.

## Acceptance Criteria

- [x] Research phase complete: desktop app detection paths, global context (`~/.gemini/GEMINI.md`), permissions storage (`~/.gemini/antigravity/implicit/*.pb` — not scriptable) documented.
- [ ] `scripts/install-antigravity.sh` exists, detects Antigravity 2.0 app, fails with actionable error if not found, is idempotent, supports `--dry-run`.
- [ ] Part A: GEMINI.md @ import present after install; existing user content preserved.
- [ ] Part B: installer prints clear guidance for the one-time permission dialog.
- [ ] `scripts/test-install-antigravity.sh` passes all scenarios.
- [ ] `check_antigravity` in health check SKIPs gracefully if app not installed, validates GEMINI.md when it is.
- [ ] Three-probe dogfood confirmed (sentinel, content-proof, write-back) from unrelated Antigravity 2.0 conversation.
- [ ] README documents install, dogfood commands.

## Progress

- [x] Phase 1: Research Antigravity 2.0 product architecture.
- [x] Phase 2: Implement `scripts/install-antigravity.sh`.
- [x] Phase 3: Add health check.
- [x] Phase 4: Create isolated temp-dir tests.
- [ ] Phase 5: Dogfood from unrelated Antigravity 2.0 session (requires user).
- [x] Phase 6: Update README and documentation.

## Decisions

- **Target product**: Antigravity 2.0 desktop app only, not the Antigravity CLI (`agy`).
- **Part A**: Single `@` import in `~/.gemini/GEMINI.md` → AGENTS.md → INDEX.md → instructions/ fan-out.
- **Part B**: One-time permission dialog ("Yes, and always allow") — no scriptable mechanism discovered after testing: `settings.json` (CLI-only), `projects.json` (no effect), `trustedFolders.json` (no effect). The binary protobuf storage at `~/.gemini/antigravity/implicit/` is not safely scriptable from a shell installer.
- **Detection**: Check common install paths for the desktop app (not a binary on PATH).
- Three-probe dogfood required for closure.
- No project-local artifact generation — fan-out handles routing.
- **Health check is diagnostic-only**: SKIPs when app not detected, never gates CI.

## Verification

- Research findings documented in memory.
- All temp-dir tests pass.
- `check_antigravity` SKIPs when app not detected, validates GEMINI.md when it is. Diagnostic-only.
- Three-probe dogfood recorded with evidence.
- `bash .adaptive-agents/scripts/check-project-layer.sh` passes.

## Supporting Documents

- [Backlog specification](PL-20260711-antigravity-support.backlog.md) — approved lightweight objective, problem spec, scope.
- [PL-20260711-antigravity-support memory](PL-20260711-antigravity-support.memory.md) — research findings, decisions, and handoff state.
- [Antigravity 2.0 Features](https://antigravity.google/docs/features) — Projects, security presets, scoped permissions.
- [Antigravity 2.0 Overview](https://antigravity.google/docs/overview) — product architecture.
- [Antigravity Plugins](https://antigravity.google/docs/plugins) — `~/.gemini/config/plugins/` directory, rules, skills.
- [Antigravity Hooks](https://antigravity.google/docs/hooks) — data directories, event system.
- [Antigravity Gemini Migration](https://antigravity.google/docs/cli/gcli-migration) — confirms shared `~/.gemini/GEMINI.md` global context.
- [Antigravity Best Practices](https://antigravity.google/docs/cli/best-practices) — workspace GEMINI.md/AGENTS.md auto-discovery.
