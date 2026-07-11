# PL-20260711-opencode-installer-rework Memory

Cross-session learnings, verification findings, and decisions for the OpenCode Installer Rework.

## Restart Context

- This reworks the OpenCode installer that was closed as `PL-20260710-opencode-installer-support` and **Reopened** because dogfooding showed OpenCode did not reliably load `AGENTS.md`.
- Goal: match the Claude Code integration's reliability using **one** tool-native entrypoint that loads the canonical repo `AGENTS.md`.

## Carried-Forward Facts (still valid)

- **Single-entrypoint fan-out beats stacked layers** (proven in `PL-20260711-claude-code-support`): one native entrypoint → canonical `AGENTS.md` → `INDEX.md` → `instructions/`. Do not generate per-file rule copies.
- **Prose ≠ native import** (retrospective `retrospectives/inbox/2026-07-11-claude-entrypoint-not-loaded.md`, repo root): a path written as prose/backticked text is not loaded; only the tool's native import/instruction mechanism pulls content into startup context. A runtime read of an out-of-directory path may be rejected.
- **Do not duplicate the sentinel**: canonical `AGENTS.md` is the only place `ADAPTIVE_AGENTS_GLOBAL_LOADED` is defined. The current `opencode/AGENTS.md` copy violates this.
- **External-path access is a distinct requirement**: Claude Code needed `permissions.additionalDirectories`; OpenCode's equivalent (if any) must be verified, not assumed.
- **Fresh-session discipline**: only uncached, fresh sessions prove loading. Intermittent success is a failure.
- **Windows/Python friction**: installer uses a Python JSON merge; `find_python` tries `python3`/`python`/`py -3`. Follow command-failure-pivot guidance — diagnose, don't retry-loop.

## Current Installer Layers To Rework (as of reopen)

`scripts/install-opencode.sh` currently writes THREE overlapping layers:

1. `instructions` array in `opencode.json` with 4 entries (`AGENTS.md`, `INDEX.md`, `global.instructions.md`, `instructions/*.instructions.md`).
2. A **copied** `~/.config/opencode/AGENTS.md` generated from `opencode/AGENTS.md` with `<REPO_ROOT>` substituted — this copy re-defines the sentinel and uses prose. **Prime suspect for the flakiness.**
3. Six slash commands copied to the global commands dir.

Idempotency currently uses an external `.adaptive-agents-installed` marker file (good — keeps the sentinel out of the JSON, which previously caused OpenCode `ConfigInvalidError`).

## Verification Findings (Feature Spec 1.0 — resolved 2026-07-11, OpenCode v1.14.22)

Docs links are recorded in the SDD → Official Documentation References.

- [x] **`instructions` loads content**: "All instruction files are combined with your `AGENTS.md` files"; supports glob patterns; remote URLs fetched with 5s timeout. ([docs/config](https://opencode.ai/docs/config/), [docs/rules](https://opencode.ai/docs/rules/))
- [x] **No native import syntax**: "opencode doesn't automatically parse file references in `AGENTS.md`" — routed files must be read at runtime via the Read tool. ([docs/rules](https://opencode.ai/docs/rules/))
- [x] **Precedence**: remote → global (`~/.config/opencode/opencode.json`) → `OPENCODE_CONFIG` → project → `.opencode` dirs → inline → managed. ([docs/config](https://opencode.ai/docs/config/))
- [x] **External access is gated**: `permission.external_directory` defaults to **`"ask"`** for "tool calls that touch paths outside the working directory". Persistent grant: `"permission": {"external_directory": {"<repo>/**": "allow"}}`. **This missing grant is the confirmed routing blocker.**
- [x] **Write coverage**: "Any directory allowed here inherits the same defaults as the current workspace" — writes follow workspace defaults (`edit` permission) once the directory is allowed. Write-back must still be proven in the dogfood.
- [x] **Actual config file**: `~/.config/opencode/opencode.jsonc` exists and is preferred; docs name `~/.config/opencode/opencode.json` as the only global location. **`%APPDATA%/opencode/` is NOT consumed** — the `opencode.json` there (containing the schema-invalid `_adaptive_agents_installed` key) plus 6 command files are leftovers from the first buggy installer run and must be cleaned up.

## Live Machine State (inspected 2026-07-11)

- `~/.config/opencode/` is the user's own **git repo** (has `.git`, `package.json`, personal `agents/`, `skills/`, templates) — merge surgically, never clobber.
- Present from old installer: sentinel-duplicating `AGENTS.md` copy, 4 AA entries in `opencode.jsonc` `instructions`, 6 command files in `commands/`, `.adaptive-agents-installed` marker, two `.bak` files.
- `$APPDATA/opencode/`: entirely old-installer artifacts (`opencode.json` with 4 AA instructions entries + invalid key; 6 command files; no AGENTS.md).
- OpenCode CLI v1.14.22 at `~/.opencode/bin/opencode`; desktop app is the user's primary client.

## False-Positive Chain (root-cause summary)

1. Copied `~/.config/opencode/AGENTS.md` defines the sentinel → model echoes it without reading the canonical repo (user-confirmed false positive).
2. Even when canonical `AGENTS.md` content loaded via `instructions`, routing failed: runtime reads of repo files hit `external_directory: ask`.
3. Redundant layers made diagnosis ambiguous — impossible to tell which layer produced observed behavior.

## Decisions Captured

- **User-confirmed diagnosis (2026-07-11)**: prior "success" was a false positive — sentinel echoed from the copied `~/.config/opencode/AGENTS.md` (which locally defines it) while canonical repo content was never loaded; routed file access failed. Confidence that guidance was ever actually read: low.
- **Dogfood must include a content-proof probe**: a question answerable only from canonical repo files (e.g., current active plan + top backlog item). Sentinel-only checks are banned as pass criteria for this integration.
- **Primary client: OpenCode desktop app** — verify its config consumption and trust model first; other clients are secondary.
- **Commands: remove unless proven needed** (user decision).
- **Installer performs migration cleanup** of prior-generation artifacts (copied AGENTS.md, redundant instructions entries, command files, stale markers), with backups (user decision).

## Verified Behavior (implementation, 2026-07-11)

- Reworked `scripts/install-opencode.sh` installed live: final `opencode.jsonc` contains provider config (untouched), a single `instructions` entry (`<repo>/AGENTS.md`), and `permission.external_directory` `<repo>/**` = `allow` — nothing else changed.
- Live migration removed: sentinel-duplicating `~/.config/opencode/AGENTS.md`, 3 legacy `instructions` entries, 6 command files (+ empty `commands/` dir), and the entire stale `%APPDATA%/opencode/` tree (config with invalid `_adaptive_agents_installed` key + 6 commands).
- Live rerun: byte-for-byte identical config, zero new backups. `--dry-run` previews every action and writes nothing.
- Repo cleanup: `opencode/` templates (AGENTS.md, opencode.jsonc, commands/) deleted — no copied-guidance source remains.
- `scripts/test-opencode.sh` rewritten for the new contract: 16/16 (fresh install, legacy migration, user-file preservation, byte-stable rerun, dry-run, APPDATA cleanup, README).
- `scripts/check-adaptive-agents.sh`: new `check_opencode` validates the live single-entrypoint contract with a string-aware JSONC parser (naive regex comment-stripping broke on `https://` URLs — fixed); 128 passed, 0 failures, 0 warnings.

## Closure (2026-07-11, disposition: Completed)

- Dogfood user-confirmed 2026-07-11: fresh OpenCode desktop session in an unrelated repository passed the three-probe protocol (sentinel, content-proof, write-back).
- The user's `~/.config/opencode/` is a git repo — changes remain reviewable there via `git diff` (backup also written: `opencode.jsonc.adaptive-agents.20260711-143110.bak`).
- Uninstall/removal support was raised at closure and ruled **out of scope** by the user; no backlog item created.
- Generalized lessons were promoted to the backlog contract header (three-probe dogfood, migrate-don't-accumulate, isolated installer tests, live health checks, tool-version pinning) and to the universal README verification section.

## Restart Context (if reopened)

- Findings above are pinned to OpenCode v1.14.22; re-verify docs on major upgrades before trusting them.
- If loading regresses, check in order: (1) the `instructions` entry still present in the global config, (2) the `permission.external_directory` grant still present, (3) no re-generated local AGENTS.md copy shadowing the sentinel, (4) OpenCode changelog for config-schema or permission-model changes.
