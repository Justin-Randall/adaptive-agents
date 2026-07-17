# PL-20260717-markdown-browser — Working Memory

- Work Unit: PL-20260717-markdown-browser
- Activated: 2026-07-17
- Status: Active

## Trigger

IDE markdown preview lacks navigation (no back/forward, no history). Users need a proper browser-based markdown reader for the repo's guidance files.

## Design Constraints

- **One external dependency**: `watchdog` for OS-native file notifications. Everything else is stdlib or CDN.
- **Project Layer scope**: Everything lives under `.adaptive-agents/`. Future graduates to canonical `ui/`.
- **Read-only MVP**: No editing, creating, or deleting files through the UI. Browser only.
- **Server runs from repo root**: Relative links and image references resolve naturally without rewriting.
- **Reactivity via SSE**: Watchdog background thread feeds a queue; SSE handler reads and pushes to connected clients. Debounce 300ms.

## Open Questions

- Default port? 8080 seems conventional. Could add `--port` later.
- Should `generate` re-run automatically on `serve` if files are missing? Yes — auto-generate on serve if output doesn't exist.
- What image types to support in `/api/file`? Start with png, jpg/jpeg, gif, svg, webp.

## Sources

- `marked.js` documentation: <https://marked.js.org/>
- `watchdog` documentation: <https://python-watchdog.readthedocs.io/>
- Prior abandoned UI scaffold at `ui/` (has `node_modules` with `marked` installed but zero source files).

## Decisions

See ACTIVE.md Decisions table.
