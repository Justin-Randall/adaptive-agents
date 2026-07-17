# PL-20260717: Adaptive Agents Markdown Browser

- Status: Active
- Work Unit: PL-20260717-markdown-browser
- Origin: Backlog ([PL-20260717-markdown-browser.backlog.md](../backlog/PL-20260717-markdown-browser.md))
- Activated: 2026-07-17
- Memory: [PL-20260717-markdown-browser.memory.md](PL-20260717-markdown-browser.memory.md)

## Objective

Build a standalone, browser-based markdown browser that lives in the Project Layer. It serves markdown from the repo root with proper link following, image rendering, back/forward navigation, and real-time reactivity to file changes — no more relying on clunky IDE preview.

## Specifications

### Problem Spec

The IDE's built-in markdown preview is sufficient for a quick glance but has no meaningful navigation: following a link opens the linked file but there is no back button, no forward button, no history. Browsing a set of related documents requires opening new tabs or clicking around and losing your place. Images, cross-references, and directory browsing are all clunky or absent.

Users spend extensive time in the IDE working with markdown documentation (instructions, plans, retrospectives, playbooks). A dedicated browser that understands the repo's directory structure, renders markdown faithfully, and lets the user navigate freely would dramatically improve the experience.

The MVP must be simple, zero-infrastructure, and live within the Project Layer so it's always available alongside the guidance it renders.

### Feature Spec

1. **Python HTTP server** at `.adaptive-agents/scripts/ui.py` with two subcommands:
   - `generate` — writes `index.html` and `app.js` to `.adaptive-agents/ui/`.
   - `serve` — starts the HTTP server, auto-generating output files if missing.

2. **File serving** from the repo root so relative Markdown links (`../instructions/coding.instructions.md`) and image references (`![](images/foo.png)`) resolve correctly.

3. **API endpoints:**
   - `/api/tree` — JSON directory tree of all markdown files and directories under the repo root.
   - `/api/file?path=...` — returns raw file content with correct Content-Type (text/markdown for .md, image/png for .png, etc.).
   - `/events` — SSE stream for file-change notifications.

4. **Frontend** at `.adaptive-agents/ui/index.html` + `.adaptive-agents/ui/app.js`:
   - Left sidebar: expandable file tree loaded from `/api/tree`.
   - Right pane: rendered markdown via `marked.js` (CDN).
   - History API navigation: back/forward work natively, URL reflects current file.
   - `.md` links: navigate within the app using `history.pushState`.
   - External links: open in new tab.
   - Images: render inline in markdown output.
   - SSE connection to `/events`: re-render current file on `file_changed`, refresh tree on `tree_changed`. Show a brief indicator on update.

5. **File watching:**
   - `watchdog.Observer` monitors the repo root recursively on a background thread.
   - Events debounced 300ms before dispatch.
   - Changes pushed to all connected SSE clients via a shared queue.

### Interface / Contract Spec

**SSE event format:**

```
event: file_changed
data: {"path": "instructions/coding.instructions.md"}

event: file_added
data: {"path": "retrospectives/inbox/new-note.md"}

event: file_removed
data: {"path": "retrospectives/inbox/old-note.md"}

event: tree_changed
data: {}  // client should refetch /api/tree
```

**`/api/tree` JSON shape:**

```json
{
  "name": "adaptive-agents",
  "type": "directory",
  "children": [
    {"name": "README.md", "type": "file", "path": "README.md"},
    {"name": "instructions", "type": "directory", "children": [
      {"name": "coding.instructions.md", "type": "file", "path": "instructions/coding.instructions.md"}
    ]}
  ]
}
```

### Behavioral Spec

| Case | Expected behavior |
| --- | --- |
| Browser opens `/` | Loads `index.html` from `.adaptive-agents/ui/` |
| Browser opens `/README.md` | Serves the file with `Content-Type: text/markdown` |
| Browser opens `/images/foo.png` | Serves the file with correct image Content-Type |
| Browser opens `/api/tree` | Returns JSON directory tree of markdown files |
| User clicks a `.md` link in rendered content | `click` handler calls `history.pushState` and renders the new file |
| User clicks browser Back | `popstate` event loads and renders the previous file |
| User clicks an external link (`https://...`) | Opens in new tab (normal link behavior) |
| A file is saved on disk | watchdog fires an event → SSE pushes `file_changed` → browser re-renders if that file is currently displayed |
| A file is created or deleted | watchdog fires → SSE pushes `file_added`/`file_removed` + `tree_changed` → browser refreshes sidebar tree |
| Multiple SSE clients connected | All clients receive the same events |
| Server receives SIGINT (Ctrl+C) | Clean shutdown: stop observer, close SSE connections, exit |

## Applicable Guidance

- `instructions/coding.instructions.md` — small, reversible changes; testable dependencies; preserve existing style.
- `instructions/project.instructions.md` — read `ARCHITECTURE.md` before changing structure or templates.

## Scope

### Included

1. Create `.adaptive-agents/scripts/ui.py` with `generate` and `serve` subcommands + dependency checks.
2. Create `.adaptive-agents/ui/index.html` (app shell) and `.adaptive-agents/ui/app.js` (frontend logic).
3. Implement the HTTP server with file serving, `/api/tree`, `/api/file?path=...`, and `/events` (SSE).
4. Integrate `watchdog.Observer` for OS-native file-change notifications with debounced SSE dispatch.
5. Implement the frontend: sidebar tree, markdown rendering via CDN `marked.js`, History API navigation, SSE reactivity.
6. Verify the server starts, serves files, and SSE events flow correctly.

### Not Included

- Fancy dashboard, charts, or widgets. This is a markdown browser.
- Bundling `marked.js` for offline use — that's a future iteration.
- WebSocket or bidirectional communication — SSE is sufficient for file-change push.
- File editing, creation, or deletion through the UI. Read-only browser for MVP.
- Dark mode / theme switching — MVP uses system preference via `prefers-color-scheme` CSS media query.
- Full-text search — out of scope for now.
- This work unit is scoped to the Project Layer only. Future iterations may graduate to the canonical `ui/` path for use by multiple Project Layers.

## Acceptance Criteria

| # | Criterion | Verification |
| --- | --- | --- |
| AC1 | `py -3 .adaptive-agents/scripts/ui.py generate` produces `.adaptive-agents/ui/index.html` and `app.js`. | File existence check |
| AC2 | `py -3 .adaptive-agents/scripts/ui.py serve` starts the server and responds on the configured port. | `curl http://localhost:8099/` returns indexhtml |
| AC3 | `GET /api/tree` returns JSON with directory structure including all accessible `.md` files. | Valid JSON, contains entry for `instructions/` |
| AC4 | `GET /api/file?path=README.md` returns file content with correct Content-Type. | Response body matches file, header is `text/markdown` |
| AC5 | `GET /api/file?path=images/foo.png` returns image content with correct Content-Type for supported image types. | Content-Type is `image/png` |
| AC6 | `GET /events` returns `Content-Type: text/event-stream` and stays connected. | Response headers + connection stays open |
| AC7 | Frontend loads in browser, sidebar shows file tree, clicking a file renders markdown. | Manual browser check |
| AC8 | Clicking a `.md` link in rendered content navigates without page reload and updates the URL. | History API check: `pushState` called |
| AC9 | Browser Back button loads the previously viewed file. | `popstate` event restores previous content |
| AC10 | Creating a new `.md` file triggers a `file_added` SSE event within 1 second. | Watchdog + SSE delivery |
| AC11 | Editing a `.md` file triggers a `file_changed` SSE event; browser re-renders if that file is displayed. | Watchdog + SSE + DOM update |
| AC12 | `ui.py serve` handles missing `watchdog` with a clear error message. | Test without watchdog installed |
| AC13 | Server exits cleanly on Ctrl+C (no zombie threads). | Process exit code 0 after SIGINT |

## Progress

- [x] Scaffold the Project Layer UI directory and serve-ready files
- [x] Implement the server (`ui.py`): file serving, API endpoints, SSE, watchdog
- [x] Implement the frontend (`index.html` + `app.js`): sidebar tree, rendering, navigation, reactivity
- [x] Test end-to-end: serve files, navigate, edit files, verify SSE updates
- [x] Record verification evidence

## Implementation Plan

1. Create `.adaptive-agents/ui/` directory and `.gitkeep`.
2. Implement `ui.py` with `generate` subcommand that writes `index.html` and `app.js` shells.
3. Implement HTTP server: file serving + `/api/tree` + `/api/file` + `/events`.
4. Implement watchdog integration on a background thread with shared event queue.
5. Implement frontend: sidebar tree, markdown rendering, History API, SSE consumer.
6. Test manually: start server, open browser, navigate, edit files, verify reactivity.
7. Add basic error handling (watchdog not installed, port in use, etc.).

## Decisions

| Date | Decision | Rationale |
| --- | --- | --- |
| 2026-07-17 | Python stdlib `http.server` | Zero framework dependencies. Can upgrade to Flask later if needed. |
| 2026-07-17 | `watchdog` for file watching | OS-native notifications via inotify/FSEvents/ReadDirectoryChangesW. No polling. |
| 2026-07-17 | SSE for reactivity | Simpler than WebSocket for one-directional event push. Works over HTTP/1.1. |
| 2026-07-17 | `marked.js` from CDN | Well-tested, fast, widely used. Bundle later for offline use. |
| 2026-07-17 | History API for navigation | Back/forward work natively. No hash-router hackery. |
| 2026-07-17 | `.adaptive-agents/ui/` for output | Lives inside the Project Layer, always available alongside guidance. |
| 2026-07-17 | Server runs from repo root | Relative Markdown links and images resolve correctly without rewriting. |

## Verification

- `py -3 .adaptive-agents/scripts/ui.py generate` produces `index.html` and `app.js` — AC1 ✓
- `py -3 .adaptive-agents/scripts/ui.py serve` starts and responds:
  - `GET /api/tree` returns JSON with directory entries — AC3 ✓
  - `GET /` returns `index.html` with `Content-Type: text/html` — AC2 (port 8099) ✓
  - `GET /api/file?path=README.md` returns file with `Content-Type: text/markdown` — AC4 ✓
  - `GET /events` returns `Content-Type: text/event-stream` — AC6 ✓
- Markdown links with `.md` extension are intercepted and navigated via History API — AC8 ✓
- Dark mode support via `prefers-color-scheme` CSS media query
- Server exits cleanly on Ctrl+C (tested in isolation)
- SSE keepalive sent every 30s when no events
- Path traversal protection via `full.relative_to(REPO_ROOT.resolve())` check
- Playwright tests: 10/10 passing (navigate, render, API, SSE, back/forward)
- All tests pass from in-process server test harness

## Supporting Documents

- [PL-20260717-markdown-browser memory](PL-20260717-markdown-browser.memory.md)
