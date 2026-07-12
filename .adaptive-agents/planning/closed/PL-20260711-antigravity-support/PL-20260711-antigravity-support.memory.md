# PL-20260711-antigravity-support Memory

Curated cross-session context for the Antigravity 2.0 Support work unit.

## Status

Closed 2026-07-12 — Completed (with caveats).

## Caveat (critical for future integrations)

Antigravity 2.0 stores file-access permission grants in **undocumented protobuf binary format** at `~/.gemini/antigravity/implicit/*.pb`. This storage cannot be safely written by a shell installer — the only way to populate it is through the interactive permission dialog (select "Yes, and always allow").

Three attempted scriptable approaches all failed:

1. `settings.json` with `permissions.allow` — CLI-only, desktop app ignores it
2. `projects.json` with Project entry — doesn't control file-read dialogs
3. `trustedFolders.json` TRUST_FOLDER entry — doesn't control file-read dialogs

The Part A (`@` import in `~/.gemini/GEMINI.md`) approach is proven correct — AGENTS.md content is loaded in every Antigravity 2.0 session. Dogfood confirmed the sentinel probe works.

## Decisions

Same as SDD. No changes from active phase.
