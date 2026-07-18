# PL-20260717-markdown-browser — Working Memory

- Work Unit: PL-20260717-markdown-browser
- Activated: 2026-07-17
- Status: Completed

## Trigger

IDE markdown preview lacks navigation (no back/forward, no history). Users need a proper browser-based markdown reader for the repo's guidance files.

## Design Constraints

- **One external dependency**: `watchdog` for OS-native file notifications. Everything else is stdlib or CDN.
- **System-wide ownership pivot**: The browser should be delivered by the canonical Adaptive Agents install, not copied into every Project Layer. It should target a current project root and read that project's `.adaptive-agents/` content/config.
- **Current implementation**: `scripts/ui.py` is the canonical entrypoint, `scripts/markdown_browser.py` owns the server/generator, and generated browser assets live under `ui/markdown-browser/`. The old `.adaptive-agents/scripts/ui.py` path is only a compatibility wrapper.
- **Read-only MVP**: No editing, creating, or deleting files through the UI. Browser only.
- **Server runs from repo root**: Relative links and image references resolve naturally without rewriting.
- **Reactivity via SSE**: Watchdog publishes through a broadcast broker; every SSE connection owns a subscriber queue so all clients receive each event. Debounce 300ms.
- **Navigation**: Sidebar is a collapsible index-page navigator, not a full file browser. It shows `.adaptive-agents` directories that contain `INDEX.md` and recurses into child directories that also contain `INDEX.md`.
- **System navigation**: The Project Layer tree and system-wide Adaptive Agents tree are separate roots. Project entries remain project-relative; system entries use `system:` paths resolved from `adaptiveAgentsHome` in `.adaptive-agents/project-layer.json`. The system tree is an area navigator: canonical top-level areas, `INDEX.md`/`README.md`/`SKILL.md` fallbacks, virtual folder labels when an area has no index, and no root Markdown link dumps.
- **Area indexes**: Canonical system-wide top-level folders should have concise `INDEX.md` files. These documents provide human browseability and model guidance for future additions without increasing startup context unless they are explicitly routed and loaded.
- **External-project validation direction**: Validate from another project by running `py -3 scripts/ui.py serve --target <project-root>` from the canonical Adaptive Agents install, not by copying the full browser into the Project Layer template.
- **Template versioning**: Project Layer template versions use SemVer-style pre-1.0 numbering (`0.<minor>.<patch>`). Patch versions handle additive docs/metadata/bug fixes; minor versions handle new capabilities or migrations; `1.0.0` waits for a stable contract.

## Open Questions

- Default port? 8099 (avoiding 8080 which commonly conflicts). Could add `--port` later.
- Should `generate` re-run automatically on `serve` if files are missing? Yes — auto-generate on serve if output doesn't exist.
- What image types to support in `/api/file`? Start with png, jpg/jpeg, gif, svg, webp.

## Sources

- `marked.js` documentation: <https://marked.js.org/>
- `watchdog` documentation: <https://python-watchdog.readthedocs.io/>
- Prior abandoned UI scaffold at `ui/` (has `node_modules` with `marked` installed but zero source files).

## Decisions

See ACTIVE.md Decisions table.

## Closure

Completed and approved on 2026-07-18. MVP delivered as a system-owned Adaptive Agents Markdown Browser, committed as `745134c`, and pushed to `origin/pl-20260717-markdown-browser` with upstream tracking.
