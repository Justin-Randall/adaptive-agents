# PL-20260711: OpenCode Installer Rework

- Status: Closed — Completed (2026-07-11)
- Work Unit: PL-20260711-opencode-installer-rework
- Origin: Backlog ([PL-20260711-opencode-installer-rework.backlog.md](PL-20260711-opencode-installer-rework.backlog.md))
- Activated: 2026-07-11
- Closed: 2026-07-11

## Objective

Rework the OpenCode installer and integration to implement the Adaptive Agents architectural pattern proven by the Claude Code and VS Code integrations: **one native entry point inserted into the agent application's user-level startup configuration, plus a grant marking the user-wide Adaptive Agents source directories as safe to read and write**. A fresh OpenCode session in any repository must load the canonical `AGENTS.md` at startup, return `ADAPTIVE_AGENTS_GLOBAL_LOADED`, route planning questions through `manage-planning`, and be able to write routed artifacts (e.g., retrospectives) back into the Adaptive Agents repository.

## Specifications

### Architecture Spec (the pattern this rework must implement)

Every Adaptive Agents tool integration has exactly two parts, applied at **user scope** so they take effect in every project the agent tool opens:

1. **Single entry point** — one tool-native mechanism in the tool's user-level startup config that loads the canonical `<repo>/AGENTS.md` **content** into session context when a new session starts. `AGENTS.md → INDEX.md → instructions/` fan-out handles all further routing. No copies, no per-file rule generation, no second sentinel definition.
2. **Trusted source directories** — the tool's narrowest available access grant marking the Adaptive Agents repository as safe to **read and write** from sessions whose working directory is elsewhere. Read access is needed to follow routing (`INDEX.md`, instructions, skills, planning); write access is needed for routed workflows that persist state back to the repo (retrospective capture, memory/planning updates).

Proven instances of this pattern:

- **Claude Code** (`scripts/install-claude-code.sh`): entry point = bare native `@<repo>/AGENTS.md` import in a marker-delimited section of `~/.claude/CLAUDE.md`; trust grant = `<repo>` in `permissions.additionalDirectories` of `~/.claude/settings.json` (grants read/write file-tool access outside the working directory).
- **VS Code / Copilot** (`scripts/install-vscode.sh`): entry point = user-wide instructions file registered via `chat.instructionsFilesLocations` in user `settings.json`, referencing the canonical repo files; related `chat.*` settings ensure referenced instructions are applied.

Both integrations share the same installer discipline: marker/managed-section idempotency, narrow JSON merges that preserve all unrelated user configuration, byte-for-byte stable reruns, `--dry-run`, and fresh-session dogfooding.

This rework maps that pattern onto OpenCode's verified native equivalents.

### Problem Spec

The prior OpenCode installer (`scripts/install-opencode.sh`) was closed as completed but dogfosting showed sessions did **not** reliably honor `AGENTS.md` or return the sentinel. Root causes visible in the current implementation:

1. **Three redundant, overlapping layers** instead of one entrypoint:
   - a 4-entry `instructions` array (`AGENTS.md`, `INDEX.md`, `global.instructions.md`, `instructions/*.instructions.md`) written into `opencode.json`,
   - a **copied** `~/.config/opencode/AGENTS.md` (generated from `opencode/AGENTS.md` with `<REPO_ROOT>` substituted),
   - six slash-command files copied into the global commands dir.
2. **The copied global `AGENTS.md` re-defines the sentinel** (`ADAPTIVE_AGENTS_GLOBAL_LOADED`) and uses **prose** ("Read AGENTS.md and INDEX.md…"). Canonical `AGENTS.md` explicitly states installers must **not** duplicate the sentinel, and the retrospective `retrospectives/inbox/2026-07-11-claude-entrypoint-not-loaded.md` (repo root) shows prose pointing at an external path does not reliably load its content and may trigger a rejected out-of-directory read.
3. **Unverified loading mechanism**: it was never established which OpenCode mechanism actually pulls file *content* into startup context, whether external-path/trust boundaries are satisfied, or whether success survives a fresh (uncached) session.

### Feature Spec 1.0 — Verify OpenCode's native loading behavior (blocking, do first)

Before redesigning, establish from official OpenCode docs plus a live probe the OpenCode-native equivalent of each half of the Architecture Spec:

**Entry point:**

- Which mechanism loads external instruction **content** into session startup context: the `instructions` array (does OpenCode read the file bodies, or only pass paths?), a global `AGENTS.md`, native import/`@`-style includes, or `~/.claude/CLAUDE.md` compatibility.
- Precedence and merge order across global config, project `.opencode/`, and `OPENCODE_CONFIG`.
- The exact global config destination actually consumed by the user's OpenCode (`~/.config/opencode/` vs. platform variants; `.jsonc` vs `.json`).

**Trusted source directories:**

- How OpenCode gates file access outside the session's working directory (trust prompts, permission config, allow-lists), for both **read** (following `INDEX.md` routing) and **write** (persisting retrospectives/planning updates back to the repo).
- The narrowest persistent grant that marks the Adaptive Agents repository safe for read/write without prompting per session — the `permissions.additionalDirectories` analogue.

Capture findings in the work-unit memory before writing installer changes. If a required behavior cannot be verified from docs, probe a live session rather than assuming.

### Feature Spec 2.0 — Single canonical entrypoint + trusted source directories

Redesign `scripts/install-opencode.sh` to install exactly the two parts of the Architecture Spec, using the mechanisms verified in Feature Spec 1.0:

**Entry point:**

- Reference the canonical `<repo>/AGENTS.md` directly via OpenCode's verified native loading mechanism; do **not** generate a copy that inlines guidance or re-defines the sentinel.
- Let `AGENTS.md → INDEX.md → instructions/` fan-out do the routing; do not enumerate `global.instructions.md` / `instructions/*.instructions.md` as separate entrypoints unless verification proves the single entrypoint does not chain-load them.
- Remove the sentinel-duplicating `opencode/AGENTS.md` template (or reduce it to a bare native include of the canonical file with no second sentinel), consistent with the Claude Code decision that `AGENTS.md`/`INDEX.md` are the only routing source of truth.

**Trusted source directories:**

- Configure OpenCode's verified narrowest persistent grant so the Adaptive Agents repository is safe to **read and write** from sessions in unrelated working directories (mirroring `permissions.additionalDirectories` in the Claude Code integration).
- Grant exactly the repository root, deduplicated; touch no other permission or trust settings.
- If OpenCode has no persistent grant mechanism, record that as a verified constraint in memory and document the per-session trust behavior the user should expect — do not fake it with file copies.

### Feature Spec 3.0 — Narrow, idempotent config merge

- Preserve all existing OpenCode config keys and entries; change only what the single entrypoint requires; deduplicate.
- A same-version rerun leaves managed files **byte-for-byte** unchanged.
- Keep `--dry-run`; reassess `--opencode-config` and `--skip-commands` against the reduced surface.

### Feature Spec 4.0 — Rationalize the command layer

The six slash commands are convenience, not the loading mechanism. Keep them only if they add value beyond `AGENTS.md` fan-out; otherwise remove them so the install surface matches the single-entrypoint model. Decide based on Feature Spec 1.0 findings; do not let commands remain a redundant guidance-loading path.

### Feature Spec 5.0 — Health check + tests + docs

- Update `scripts/check-adaptive-agents.sh` to validate the reworked OpenCode config against the single-entrypoint contract (references canonical `AGENTS.md`, no duplicated sentinel, no orphaned layers).
- Update `scripts/test-opencode.sh` for the new contract (generation, path resolution, idempotency/byte-stability, removal of retired layers).
- Update `README.md` OpenCode section to match the reworked install.

### Interface / Contract Spec

| Aspect | Spec |
| --- | --- |
| Invocation | `bash scripts/install-opencode.sh [--dry-run] [--opencode-config PATH]` |
| Stdout | One human-readable line per action |
| Stderr | Actionable errors (config path undetectable, repo root undetectable, Python missing) |
| Exit 0 | Install complete | 
| Exit 1 | Error described on stderr |
| Dry-run | Each action prefixed `[dry-run]`; nothing written |
| Idempotency | Marker-based (external marker file, not an in-JSON key that trips OpenCode schema validation); reruns byte-stable |

### Behavioral Spec

- **User scope**: install to OpenCode's global config so guidance applies in every project the tool opens.
- **Two parts, nothing more**: one entry point + one trusted-directory grant. Any additional generated layer is scope creep.
- **Read and write**: the trust grant must support routed workflows that read guidance from and persist artifacts (retrospectives, planning/memory updates) to the Adaptive Agents repository from sessions rooted elsewhere.
- **Preservation**: retain all unrelated config; modify only the narrow entrypoint/access surface; dedupe.
- **Single source of truth**: the canonical repo `AGENTS.md` defines the sentinel and routing; no generated copy re-defines them.
- **Fresh-session truth**: success is defined by uncached, fresh sessions — intermittent loading is a failure, not a pass.

## Applicable Guidance

- `instructions/global.instructions.md` — default engineering guidance
- `instructions/coding.instructions.md` — coding standards for the installer script
- `instructions/repository-boundaries.instructions.md` — keep installer in the Adaptive Agents repo
- `instructions/tdd.instructions.md` — test-driven approach for installer behavior
- `instructions/command-failure-pivot.instructions.md` — avoid retry loops on Windows shell / Python path friction
- `skills/manage-planning/SKILL.md` — governs execution and closure of this work
- **Cross-tool integration contract** (backlog INDEX header, from PL-20260711 Claude Code) — verify native loading syntax, one entrypoint, handle external-path/trust boundaries, preserve+dedupe config, byte-stable reruns, dogfood fresh sessions
- Reference: `scripts/install-claude-code.sh` — proven entry-point + trusted-directory pattern to mirror
- Reference: `scripts/install-vscode.sh` — proven user-level instructions registration pattern
- Reference: closed [PL-20260711-claude-code-support.sdd.md](../PL-20260711-claude-code-support/PL-20260711-claude-code-support.sdd.md) — decisions and verified behavior

## Scope

### In Scope

- Verify OpenCode's native loading mechanism (docs + live probe) and record findings
- Redesign `scripts/install-opencode.sh` around one canonical entrypoint
- Retire/replace the sentinel-duplicating `opencode/AGENTS.md` copy
- Collapse the redundant `instructions` layers to the verified minimum
- Rationalize `opencode/commands/*.md` (keep only if justified)
- Update `scripts/check-adaptive-agents.sh`, `scripts/test-opencode.sh`, `README.md`
- Route detection in `scripts/install.sh` if the interface changes

### Out of Scope

- Other tools' installers (Codex, Cursor, Copilot, Cline, Antigravity, Gemini, Windsurf)
- MCP server integration
- GUI installer
- Per-project `opencode.json` support (global config covers all projects)
- Changing OpenCode provider/model configuration

## Acceptance Criteria

- [x] OpenCode's actual content-loading mechanism, precedence, and external-path read/write boundary are verified and recorded in the work-unit memory.
- [x] `scripts/install-opencode.sh` configures exactly **one** native entrypoint that loads the canonical repo `AGENTS.md`; no generated copy re-defines the sentinel.
- [x] The installer applies OpenCode's narrowest persistent grant marking the Adaptive Agents repository safe to read and write from sessions in unrelated directories (`permission.external_directory`).
- [x] Existing OpenCode config is preserved and deduplicated; only the narrow entrypoint/access surface changes (verified live: provider config untouched).
- [x] Same-version rerun leaves managed files byte-for-byte unchanged; `--dry-run` writes nothing (verified live and in tests).
- [x] Retired layers (duplicated `AGENTS.md`, redundant `instructions` entries, commands, stale `%APPDATA%` artifacts) are removed with no orphaned files left behind (verified live).
- [x] `scripts/check-adaptive-agents.sh` validates the reworked OpenCode config; `scripts/test-opencode.sh` passes against the new contract (16/16).
- [x] `README.md` documents the reworked OpenCode install.
- [x] **Dogfood (read path)**: user-confirmed 2026-07-11 — fresh OpenCode desktop session behaves as expected against the three-probe protocol.
- [x] **Dogfood (write path)**: user-confirmed 2026-07-11 as part of the same dogfood pass.

## Progress

- [x] Feature Spec 1.0 — verify native entry-point loading behavior; record findings in memory (docs verified; `instructions` loads content; no import syntax)
- [x] Feature Spec 1.0 — verify trusted-directory (read/write) grant mechanism; record findings in memory (`permission.external_directory` pattern → `"allow"`; defaults to `"ask"` — the confirmed routing blocker)
- [x] Feature Spec 2.0 — redesign installer to single entrypoint (one `instructions` entry: canonical `AGENTS.md`)
- [x] Feature Spec 2.0 — apply trusted source-directories grant (`permission.external_directory` `<repo>/**` = `allow`)
- [x] Feature Spec 2.0 — retire `opencode/AGENTS.md` copy and templates (deleted from repo; live copy migrated away)
- [x] Feature Spec 3.0 — narrow idempotent merge; live rerun verified byte-for-byte identical, no duplicate backups
- [x] Feature Spec 4.0 — command layer removed (user decision); live command files migrated away, user-authored commands preserved
- [x] Feature Spec 5.0 — `check-adaptive-agents.sh` validates the live contract (128 passed, 0 warnings); `test-opencode.sh` rewritten (16/16); README reworked
- [x] Dogfood across fresh sessions — read path (sentinel + content-proof probe) — user-confirmed 2026-07-11
- [x] Dogfood — write path (routed retrospective capture from an unrelated repository) — user-confirmed 2026-07-11
- [x] Dogfood — rerun idempotency and `--dry-run` (verified against the live config)
- [x] Run `bash .adaptive-agents/scripts/check-project-layer.sh` (0 failures)

## Decisions

- **Diagnosis (user-confirmed, 2026-07-11)**: prior dogfooding returned the sentinel but none of the specified Adaptive Agents behavior — a **false positive**. The copied `~/.config/opencode/AGENTS.md` defines the sentinel locally, so the model echoed it without reading the canonical repo; routed file access then failed ("loaded but couldn't follow routing"). The entry point must load canonical content, and the trust grant is a confirmed missing piece.
- **Dogfood hardening**: the sentinel alone is insufficient proof. Every dogfood pass must include a **content-proof probe** — a question answerable only by reading canonical repo files (e.g., "what is the current active plan and top backlog item?"), never from any installed artifact.
- **Primary client target**: OpenCode **desktop app** — verification and dogfooding target its config consumption and trust model first.
- **Commands removed unless proven needed**: the six slash commands are retired by default; reinstate only if Feature Spec 1.0 shows value beyond `AGENTS.md` fan-out.
- **Installer migrates old layers**: the reworked installer detects and removes prior-generation artifacts on the user's machine (copied `AGENTS.md`, redundant `instructions` entries, installed command files, stale markers), preserving backups.

## Verification

- Unit: `--dry-run` writes nothing; native entrypoint + narrow merge with dedup; rerun byte-stability
- Integration: full install → fresh OpenCode session dogfood → rerun → health check
- Regression: `scripts/check-adaptive-agents.sh` and `scripts/test-opencode.sh` pass; `scripts/check-project-layer.sh` reports 0 failures
- Fresh-session discipline: repeat sentinel + routed-workflow checks across multiple uncached sessions

## Official Documentation References

Verified 2026-07-11 against OpenCode v1.14.22 (user's installed version):

- [OpenCode Rules](https://opencode.ai/docs/rules/) — global `~/.config/opencode/AGENTS.md`; "All instruction files are combined with your `AGENTS.md` files" (i.e., `instructions` loads **content**); **no native import syntax** ("opencode doesn't automatically parse file references in `AGENTS.md`") — runtime reads are the routing mechanism.
- [OpenCode Config](https://opencode.ai/docs/config/) — global config at `~/.config/opencode/opencode.json` (the **only** documented global location; `%APPDATA%` is not consumed); `instructions` "takes an array of paths and glob patterns"; precedence: remote → global → `OPENCODE_CONFIG` → project → `.opencode` dirs → inline → managed.
- [OpenCode Permissions](https://opencode.ai/docs/permissions/) — `permission.external_directory` gates "tool calls that touch paths outside the working directory" and **defaults to `"ask"`**; persistent grant via path-pattern → `"allow"`; "Any directory allowed here inherits the same defaults as the current workspace"; rules are wildcard-matched, last match wins.
- [OpenCode Commands](https://opencode.ai/docs/commands/) — slash-command format (retired by this rework; kept for reference).
- [OpenCode config schema](https://opencode.ai/config.json) — `$schema` used by the generated/merged config.

## Supporting Documents

- [Backlog: OpenCode Installer Rework](PL-20260711-opencode-installer-rework.backlog.md) — original backlog entry (archived alongside)
- [Closed: PL-20260710 OpenCode Installer Support](../PL-20260710-opencode-installer-support/PL-20260710.sdd.md) — prior (reopened) implementation and its dogfood bugs
- [Closed: PL-20260711 Claude Code Support](../PL-20260711-claude-code-support/PL-20260711-claude-code-support.sdd.md) — proven single-entrypoint pattern
- `retrospectives/inbox/2026-07-11-claude-entrypoint-not-loaded.md` (repo root) — prose-vs-native-import lesson
- [PL-20260711-opencode-installer-rework memory](PL-20260711-opencode-installer-rework.memory.md) — cross-session learnings and verification findings
