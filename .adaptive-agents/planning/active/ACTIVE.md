# PL-20260711: Gemini CLI Support

- Status: Active
- Work Unit: PL-20260711-gemini-cli-support
- Origin: Backlog ([PL-20260711-gemini-cli-support.md](../backlog/PL-20260711-gemini-cli-support.md))
- Activated: 2026-07-12

## Objective

Provide an idempotent Gemini CLI integration that loads the canonical Adaptive Agents `AGENTS.md` through one verified native entrypoint — following the two-part installer pattern (native entry point + read/write trust grant) proven by Claude Code, OpenCode, and VS Code Agent Mode.

## Specifications

### Problem Spec

Gemini CLI uses a `GEMINI.md`-equivalent file for user-wide agent configuration, but the exact native loading syntax, import semantics (whether it supports `@file` references, `file://` URIs, or requires inline content), and external-repository read/write access boundaries must be verified before an installer can be written. Installing copied commands or skills would duplicate routing already owned by `AGENTS.md` and `INDEX.md`, violating the Adaptive Agents principle of a single canonical entrypoint.

The cross-tool integration contract (established by PL-20260711 Claude Code and OpenCode Rework) requires every integration to deliver: a single native entry point at user scope, a trusted source-directories grant, legacy migration (detect and remove prior-gen artifacts), isolated automated tests against temp-dir config, a live health check in `scripts/check-adaptive-agents.sh`, version pinning, and three-probe dogfood (sentinel, content-proof, routed write-back).

### Phase 1: Research & Verification ✅

Research completed 2026-07-12 against the official Gemini CLI documentation at `https://google-gemini.github.io/gemini-cli/`.

**Gemini CLI Version Target:** `@google/gemini-cli` (npm), latest stable. Version pinning determined at install time via `gemini --version`.

**Part A — Native Entry Point:**

The Gemini CLI uses a **hierarchical context file system** with `GEMINI.md` as the default context filename (configurable via `context.fileName`):

1. **Global context file**: `~/.gemini/GEMINI.md` — loaded automatically in EVERY Gemini CLI session. This is the canonical user-wide entry point.
2. **Project-level context files**: `GEMINI.md` files discovered hierarchically from the project root and subdirectories.
3. **Import syntax**: The Memory Import Processor supports `@path/to/file.md` syntax to import external Markdown files. Supported formats:
   - Relative: `@./file.md`, `@../file.md`, `@./components/file.md`
   - Absolute: `@/absolute/path/to/file.md`
   - Nested imports supported (max depth: 5 levels)
   - Circular import detection built in
   - Imports inside code blocks are ignored
4. **Custom context filename**: The `context.fileName` setting in `settings.json` can rename context files from `GEMINI.md` to `["AGENTS.md", "CONTEXT.md", "GEMINI.md"]`.

**Native entry point mechanism:** An `@` import line in `~/.gemini/GEMINI.md` referencing the canonical `AGENTS.md` file. Example:

```
@/absolute/path/to/adaptive-agents/AGENTS.md
```

This loads AGENTS.md content into every session's system context via the native Memory Import Processor. Single entry point — AGENTS.md → INDEX.md → instructions/ fan-out handles all routing.

**Part B — Read/Write Trust Grant:**

Gemini CLI uses a multi-layered security model for external directory access:

1. **`context.includeDirectories`** (in `~/.gemini/settings.json`): An array of directory paths added to the workspace context. The sandbox and file system service explicitly allow reads/writes to these paths. This is the primary trust grant mechanism.
2. **`context.loadMemoryFromIncludeDirectories`** (boolean): When `true`, the `/memory refresh` command scans include directories for `GEMINI.md` files.
3. **`security.folderTrust.enabled`** + `~/.gemini/trustedFolders.json`: Folder trust feature for controlling project-level config loading. Managed via `/permissions` command in the CLI.
4. **`tools.allowed`**: Array of tool call patterns that auto-approve without confirmation dialog (e.g., `["run_shell_command(git)"]`).

**Trust grant mechanism for the installer:** Add the Adaptive Agents repository path to `context.includeDirectories` in `~/.gemini/settings.json`. This grants the Gemini agent permission to read and write files in that directory tree. The narrowest scoped grant is a single absolute directory path.

### Phase 2: Installer — `scripts/install-gemini-cli.sh`

Apply the proven two-part pattern:

**Part A — Native entry point:**

- Target file: `~/.gemini/GEMINI.md` — the global context file, loaded automatically in EVERY Gemini CLI session.
- Write a single `@` import line pointing to the canonical `AGENTS.md`:

  ```text
  @/absolute/path/to/AGENTS.md
  ```

- Use the absolute path format so the import resolves regardless of which directory the CLI is launched from.
- The Memory Import Processor resolves `@` paths, loads AGENTS.md content, and includes it in every session's system context.
- Preserve and deduplicate any existing user content in `~/.gemini/GEMINI.md` — append or update the `@` import line, never overwrite user prose.
- Guarantee content-idempotent reruns: same-version reruns produce byte-identical `~/.gemini/GEMINI.md`.
- **Single entry point** — AGENTS.md → INDEX.md → instructions/ fan-out handles all routing.

**Part B — Read/write trust grant:**

- Target file: `~/.gemini/settings.json` — the user-level settings file.
- Add the Adaptive Agents repository root path to `context.includeDirectories`:

  ```json
  {
    "context": {
      "includeDirectories": ["/absolute/path/to/adaptive-agents"]
    }
  }
  ```

- This grants the Gemini agent permission to read and write files within that directory tree.
- Preserve and deduplicate any existing `context.includeDirectories` entries and all other settings.
- Guarantee content-idempotent reruns: same-version reruns produce byte-identical settings.
- The narrowest scope is a single directory path — no wildcards, no parent directory grants.

**Legacy migration:**

- Detect and remove any prior-generation artifacts written by earlier installer versions.
- Match installer-generated signatures only — never delete user-authored files.
- If no prior artifacts exist, skip migration silently.

**Contract:**

- `scripts/install-gemini-cli.sh` — idempotent, dry-run support via `--dry-run`, exit 0 on no-op.
- `--dry-run` writes nothing but reports what would change.
- Validate the exact destination file content after write (not just "file exists").
- Support same-version rerun producing byte-identical config.

### Phase 3: Health Check — `scripts/check-adaptive-agents.sh`

Add a `check_gemini_cli` function to `scripts/check-adaptive-agents.sh` that:

1. Detects whether Gemini CLI is installed (`which gemini` or equivalent).
2. If installed, reads the Gemini CLI user-level config file.
3. Parses the config file to confirm the canonical `AGENTS.md` entry point reference is present (string-aware parsing; naive comment-stripping corrupts URLs).
4. Validates the trusted-directories grant includes the Adaptive Agents repository.
5. Reports PASS/FAIL with diagnostic detail.
6. Returns non-zero on any validation failure.

### Phase 4: Isolated Tests — `scripts/test-install-gemini-cli.sh`

Create a focused test script that runs entirely against temporary directories (never touches real user configuration):

1. **Fresh install**: Install into empty temp config → verify entry point and trust grant present.
2. **Legacy migration**: Seed temp config with prior-gen artifact → run installer → verify artifact removed and canonical entry point in place.
3. **Byte-stable rerun**: Run installer twice → verify second run produces identical output.
4. **Dry-run writes nothing**: Run `--dry-run` → verify no files modified.
5. **Unrelated-config preservation**: Seed temp config with unrelated configuration lines → run installer → verify unrelated content preserved and deduplicated.
6. **User-file preservation**: Seed temp config with a file that looks like a user-authored file (no installer signature) → verify it is not deleted.

### Phase 5: Dogfood & Verification

From an unrelated repository across fresh Gemini CLI sessions, verify:

1. **Sentinel probe**: `ADAPTIVE_AGENTS_GLOBAL_LOADED` is echoed when asked if Adaptive Agents is loaded.
2. **Content-proof probe**: A question answerable only from repository content, e.g., "What is the current active plan?" — the sentinel alone is a false positive (a stale installed copy can echo it, as PL-20260711 OpenCode proved).
3. **Routed write-back**: A routed workflow persists a retrospective or planning artifact back to the Adaptive Agents repository (e.g., capture a retrospective note).
4. Intermittent loading is a failure, not a pass.

## Applicable Guidance

- `.adaptive-agents/ARCHITECTURE.md` — preserve canonical routing, Project Layer ownership, and cross-tool integration boundaries.
- `instructions/global.instructions.md` — load routed engineering guidance and run the completion retrospective checkpoint.
- `instructions/repository-boundaries.instructions.md` — keep this repository's canonical and Project Layer ownership distinct.
- `instructions/coding.instructions.md` — use testable seams, source-backed claims, and focused reversible changes.
- `instructions/tdd.instructions.md` — begin behavior changes with focused failing tests and validate each slice.
- `instructions/command-failure-pivot.instructions.md` — classify command failures and pivot rather than retrying equivalent guesses.
- `instructions/temp-artifact-hygiene.instructions.md` — keep generated test artifacts isolated and cleaned up.
- `.adaptive-agents/skills/manage-planning/SKILL.md` — maintain active progress, decisions, verification, and work-unit memory.
- `scripts/install-claude-code.sh` and `scripts/install-opencode.sh` — reference implementations for the two-part installer pattern.
- `scripts/test-install-claude-code.sh` and `scripts/test-opencode.sh` — reference implementations for isolated temp-dir tests.

## Scope

- Research Gemini CLI's configuration mechanism, import syntax, and trust model.
- Implement `scripts/install-gemini-cli.sh` with the two-part pattern, legacy migration, and dry-run support.
- Add `check_gemini_cli` to `scripts/check-adaptive-agents.sh`.
- Create `scripts/test-install-gemini-cli.sh` with isolated temp-dir tests.
- Version-pin the verified Gemini CLI release.
- Dogfood from an unrelated repository with three probes (sentinel, content-proof, write-back).
- Update `README.md` with Gemini CLI install and verification commands.
- Update `install.sh` to include Gemini CLI in the all-tools install if applicable.

## Out Of Scope

- Generating `.gemini/` project-local configuration, hooks, or skill markers.
- Creating standalone `GEMINI.md` — fan-out from `AGENTS.md` handles it.
- Modifying anything outside the installer, health check, tests, README, and user-level config.
- Supporting Gemini CLI versions older than the pinned verified version.
- Chronicling, slash commands, or plugin manifests.

## Acceptance Criteria

- [x] Research phase complete: Gemini CLI config path (`~/.gemini/GEMINI.md`), import syntax (`@path`), trust grant mechanism (`context.includeDirectories`), and version (`@google/gemini-cli`) documented in memory.
- [ ] `scripts/install-gemini-cli.sh` exists, is idempotent, supports `--dry-run`, and installs only the two-part pattern.
- [ ] No copied `AGENTS.md` content, prose load directives, or duplicate guidance — only native imports.
- [ ] Existing user config is preserved and deduplicated on rerun.
- [ ] Legacy prior-gen artifacts are detected and removed (installer-signed files only).
- [ ] `scripts/test-install-gemini-cli.sh` passes all scenarios against temp directories.
- [ ] `scripts/check-adaptive-agents.sh --verbose` includes a `check_gemini_cli` function and passes.
- [ ] Three-probe dogfood confirmed from an unrelated repository:
  - Sentinel (`ADAPTIVE_AGENTS_GLOBAL_LOADED`).
  - Content-proof (e.g., current active plan name).
  - Routed write-back (e.g., retrospective capture).
- [ ] Intermittent loading is classified as a failure, not a pass.
- [ ] README documents install, verify, dogfood commands.
- [ ] No prior-installer artifacts remain after migration.

## Progress

- [x] Phase 1: Research Gemini CLI config mechanism (path, import syntax, trust grant, version).
- [ ] Phase 2: Implement `scripts/install-gemini-cli.sh`.
- [ ] Phase 3: Add health check to `scripts/check-adaptive-agents.sh`.
- [ ] Phase 4: Create isolated temp-dir tests.
- [ ] Phase 5: Dogfood from unrelated repository (three probes).
- [ ] Phase 6: Update README and any remaining documentation.

## Decisions

- Follow the established two-part pattern exactly (Claude Code and OpenCode are reference implementations).
- Research completed 2026-07-12: documented in memory and SDD.
- **Part A mechanism**: Single `@` import line in `~/.gemini/GEMINI.md` → AGENTS.md → INDEX.md → instructions/ fan-out.
- **Part B mechanism**: `context.includeDirectories` in `~/.gemini/settings.json` granting read/write access to the repo.
- The global `~/.gemini/GEMINI.md` is the correct user-wide entry point (not project `.gemini/settings.json`).
- Require three-probe dogfood for closure (sentinel alone is insufficient — prior false-positive evidence from OpenCode).
- No project-local `.gemini/` or `.rules/` files — fan-out from `AGENTS.md`.

## Verification

- Research findings documented in work-unit memory before implementation begins.
- All temp-dir tests pass.
- `check-adaptive-agents.sh --verbose` includes `check_gemini_cli` and passes.
- Three-probe dogfood recorded with evidence.
- `bash .adaptive-agents/scripts/check-project-layer.sh` passes after all changes.

## Supporting Documents

- [Backlog specification](../backlog/PL-20260711-gemini-cli-support.md) — approved lightweight objective, problem spec, and scope.
- [PL-20260711-gemini-cli-support memory](PL-20260711-gemini-cli-support.memory.md) — research findings, decisions, and handoff state.
- `scripts/install-claude-code.sh` — reference two-part installer for Claude Code.
- `scripts/install-opencode.sh` — reference two-part installer for OpenCode.
- `scripts/test-install-claude-code.sh` — reference isolated test pattern.
- `scripts/test-opencode.sh` — reference isolated test pattern.
- [Gemini CLI Configuration](https://google-gemini.github.io/gemini-cli/docs/get-started/configuration.html) — settings files, context system, `context.includeDirectories`, `context.fileName`.
- [GEMINI.md Context Files](https://google-gemini.github.io/gemini-cli/docs/cli/gemini-md.html) — context hierarchy: global (`~/.gemini/GEMINI.md`), project, subdirectory.
- [Memory Import Processor](https://google-gemini.github.io/gemini-cli/docs/core/memport.html) — `@path` import syntax, supported formats, security, circular detection.
- [Trusted Folders](https://google-gemini.github.io/gemini-cli/docs/cli/trusted-folders.html) — `security.folderTrust.enabled`, `~/.gemini/trustedFolders.json`.
- [Gemini CLI Deployment](https://google-gemini.github.io/gemini-cli/docs/get-started/deployment.html) — Installation via `npm install -g @google/gemini-cli`.
