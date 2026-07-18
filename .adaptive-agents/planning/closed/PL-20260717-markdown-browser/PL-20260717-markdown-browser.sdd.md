# PL-20260717: Adaptive Agents Markdown Browser

- Status: Completed
- Work Unit: PL-20260717-markdown-browser
- Origin: Backlog ([PL-20260717-markdown-browser.backlog.md](PL-20260717-markdown-browser.backlog.md))
- Activated: 2026-07-17
- Memory: [PL-20260717-markdown-browser.memory.md](PL-20260717-markdown-browser.memory.md)

## Objective

Build a standalone, browser-based markdown browser for Adaptive Agents guidance and project documentation. It serves markdown from the current project root with proper link following, image rendering, back/forward navigation, and real-time reactivity to file changes — no more relying on clunky IDE preview.

Architectural pivot, 2026-07-18: the browser should be owned by the system-wide Adaptive Agents install, not copied into each Project Layer. The Project Layer remains project-owned content and configuration that the browser reads; upgrading system-wide Adaptive Agents should upgrade the browser capability for every project that uses that install.

## Specifications

### Problem Spec

The IDE's built-in markdown preview is sufficient for a quick glance but has no meaningful navigation: following a link opens the linked file but there is no back button, no forward button, no history. Browsing a set of related documents requires opening new tabs or clicking around and losing your place. Images, cross-references, and directory browsing are all clunky or absent.

Users spend extensive time in the IDE working with markdown documentation (instructions, plans, retrospectives, playbooks). A dedicated browser that understands the repo's directory structure, renders markdown faithfully, and lets the user navigate freely would dramatically improve the experience.

The MVP must be simple and zero-infrastructure, but the executable browser belongs to the canonical Adaptive Agents repository. It targets a project root and reads that project's `.adaptive-agents` Project Layer instead of being copied into the Project Layer itself.

### Feature Spec

1. **Python HTTP server** at `scripts/ui.py` backed by `scripts/markdown_browser.py` with two subcommands:

- `generate` — writes `index.html` and `app.js` to `ui/markdown-browser/`.
- `serve` — starts the HTTP server, auto-generating output files if missing.
- `--target PATH` — selects the current project root to browse; defaults to the current working directory.

1. **File serving** from the repo root so relative Markdown links (`../instructions/coding.instructions.md`) and image references (`![](images/foo.png)`) resolve correctly.

2. **API endpoints:**
   - `/api/tree` — JSON directory tree of all markdown files and directories under the repo root.

- `/api/index-tree` — JSON tree of `.adaptive-agents` directories that contain `INDEX.md` files, used for quick sidebar navigation.
- `/api/system-index-tree` — JSON tree of the system-wide Adaptive Agents home, using canonical top-level areas with `INDEX.md`/`README.md`/`SKILL.md` fallbacks and virtual folder nodes where needed; it must not dump arbitrary root document links.
- `/api/file?path=...` — returns raw file content with correct Content-Type (text/markdown for .md, image/png for .png, etc.).
- `/events` — SSE stream for file-change notifications.

1. **Frontend** at `ui/markdown-browser/index.html` + `ui/markdown-browser/app.js`:

- Collapsible sidebar tree for `.adaptive-agents` directories with `INDEX.md` files.
- Optional System sidebar tree for the canonical Adaptive Agents install, sourced from `.adaptive-agents/project-layer.json` `adaptiveAgentsHome` when present and kept separate from the current project root. System navigation is an area navigator: root `Adaptive Agents`, canonical top-level areas, and useful document children for instructions, prompts, skills, playbooks, templates, schemas, scripts, and retrospectives.
- Full-width markdown viewer using `marked.js` (CDN).
- `.adaptive-agents/INDEX.md` as the default document.
- History API navigation: back/forward work natively, URL reflects current file.
- `.md` links: navigate within the app using `history.pushState`.
- External links: open in new tab.
- Images: render inline in markdown output.
- SSE connection to `/events`: re-render current file on `file_changed`, refresh tree on `tree_changed`. Show a brief indicator on update.

1. **File watching:**

- `watchdog.Observer` monitors the selected target project root recursively on a background thread.
- Events debounced 300ms before dispatch.

- A broadcast broker gives each connected SSE client its own queue and publishes every change to every subscriber.

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
| Browser opens `/` | Loads `index.html` from `ui/markdown-browser/` |
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

1. Create `scripts/ui.py` with `generate` and `serve` subcommands + dependency checks.
2. Create `scripts/markdown_browser.py` as the system-owned implementation module.
3. Create `ui/markdown-browser/index.html` (app shell) and `ui/markdown-browser/app.js` (frontend logic).
4. Implement the HTTP server with file serving, `/api/tree`, `/api/file?path=...`, and `/events` (SSE).
5. Integrate `watchdog.Observer` for OS-native file-change notifications with debounced SSE dispatch.
6. Implement the frontend: sidebar tree, markdown rendering via CDN `marked.js`, History API navigation, SSE reactivity.
7. Verify the server starts, serves files, and SSE events flow correctly.

### Not Included

- Fancy dashboard, charts, or widgets. This is a markdown browser.
- Bundling `marked.js` for offline use — that's a future iteration.
- WebSocket or bidirectional communication — SSE is sufficient for file-change push.
- File editing, creation, or deletion through the UI. Read-only browser for MVP.
- Dark mode / theme switching — MVP uses system preference via `prefers-color-scheme` CSS media query.
- Full-text search — out of scope for now.
- The Project Layer should not carry the full browser implementation. It may carry metadata such as `adaptiveAgentsHome`, but the executable browser app should live in the canonical Adaptive Agents repository and target a selected current project root.

## Acceptance Criteria

| # | Criterion | Verification |
| --- | --- | --- |
| AC1 | `py -3 scripts/ui.py generate --target .` produces `ui/markdown-browser/index.html` and `app.js`. | File existence check |
| AC2 | `py -3 scripts/ui.py serve --target .` starts the server and responds on the configured port. | `curl http://localhost:8099/` returns indexhtml |
| AC3 | `GET /api/tree` returns JSON with directory structure including all accessible `.md` files. | Valid JSON, contains entry for `instructions/` |
| AC3a | `GET /api/index-tree` returns `.adaptive-agents` index navigation. | Valid JSON, contains top-level Project Layer index folders and nested planning indexes |
| AC3b | `GET /api/system-index-tree` returns system-wide Adaptive Agents area navigation. | Valid JSON, uses `system:` paths, exposes canonical top-level areas, includes fallback document children, excludes hidden Project Layer folders and root link dumps |
| AC4 | `GET /api/file?path=README.md` returns file content with correct Content-Type. | Response body matches file, header is `text/markdown` |
| AC4a | `GET /api/file?path=system:INDEX.md` returns system-wide Adaptive Agents content without treating it as project-local. | Response body matches canonical Adaptive Agents file |
| AC5 | `GET /api/file?path=images/foo.png` returns image content with correct Content-Type for supported image types. | Content-Type is `image/png` |
| AC6 | `GET /events` returns `Content-Type: text/event-stream` and stays connected. | Response headers + connection stays open |
| AC7 | Frontend loads `.adaptive-agents/INDEX.md` in a full-width markdown viewer. | Playwright browser check |
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
- [x] Reach the user-verified MVP checkpoint
- [x] Restore sidebar quick navigation for Project Layer index pages
- [x] Make sidebar navigation branches collapsible
- [x] Add a separate System tree for the canonical Adaptive Agents install
- [x] Move browser ownership from dogfood Project Layer into system-wide Adaptive Agents
- [x] Validate the system-owned browser against a non-Adaptive-Agents project root
- [x] Add an agent-facing startup skill so users can ask to start the browser without remembering commands
- [x] Add visible and API context verification to prevent wrong Project Layer dogfooding
- [x] Add Project Repo root section to the sidebar so the target repository is visible
- [x] Refine and polish the deliverable

## Implementation Plan

1. Keep the canonical entrypoint at `scripts/ui.py` and the implementation in `scripts/markdown_browser.py`.
2. Generate static browser assets under `ui/markdown-browser/`.
3. Keep `.adaptive-agents/scripts/ui.py` as a compatibility wrapper only.
4. Validate with Playwright against `py -3 scripts/ui.py serve --target . --no-open`.
5. Validate against a non-Adaptive-Agents target project root before closing the work unit.

## Decisions

| Date | Decision | Rationale |
| --- | --- | --- |
| 2026-07-17 | Python stdlib `http.server` | Zero framework dependencies. Can upgrade to Flask later if needed. |
| 2026-07-17 | `watchdog` for file watching | OS-native notifications via inotify/FSEvents/ReadDirectoryChangesW. No polling. |
| 2026-07-17 | SSE for reactivity | Simpler than WebSocket for one-directional event push. Works over HTTP/1.1. |
| 2026-07-17 | `marked.js` from CDN | Well-tested, fast, widely used. Bundle later for offline use. |
| 2026-07-17 | History API for navigation | Back/forward work natively. No hash-router hackery. |
| 2026-07-18 | `ui/markdown-browser/` for output | Browser assets belong to the canonical Adaptive Agents install, not to each Project Layer. |
| 2026-07-17 | Server runs from repo root | Relative Markdown links and images resolve correctly without rewriting. |
| 2026-07-17 | Per-client SSE queues | Filesystem events are broadcasts; a shared work queue lets one client consume another client's update. |
| 2026-07-18 | System navigation uses `adaptiveAgentsHome` and `system:` paths | The current project root, Project Layer root, and canonical Adaptive Agents home are separate concepts even when they overlap in this dogfood repo. |
| 2026-07-18 | System navigation is an area navigator | Requiring `INDEX.md` in every system directory would make useful areas disappear until curated; dumping root links makes the sidebar unreadable. Virtual area nodes plus fallback documents keep it navigable without context-loading bloat. |
| 2026-07-18 | Canonical system areas get concise `INDEX.md` files | Top-level area indexes make placeholder and content areas human-browseable, give agents guidance for adding future content, and do not add context unless explicitly loaded. |
| 2026-07-18 | Superseded: external-project testing through Project Layer template promotion | This was the initial interpretation, but the browser is now treated as a system-wide Adaptive Agents feature. The full web app should not be copied into every Project Layer template. |
| 2026-07-18 | Project Layer template versions use SemVer-style pre-1.0 numbering | `0.<minor>.<patch>` gives room for many additive updates such as `0.5.12`; `1.0.0` is reserved for a stable Project Layer contract, not the tenth update. |
| 2026-07-18 | Markdown Browser is a system-wide Adaptive Agents feature | The browser should be upgraded by updating the canonical Adaptive Agents install, then point at any current project root and its `.adaptive-agents/` Project Layer. Project Layer template upgrades should not copy the full web app into every project. |
| 2026-07-18 | Browser startup is an agent-facing skill | Users should be able to ask the model to start the browser. Agents should infer the current target project, locate the Adaptive Agents home, start `scripts/ui.py`, choose a free port if needed, and return the URL. |
| 2026-07-18 | Browser context must be visible and machine-checkable | Dogfooding exposed a wrong-root failure where the browser showed Adaptive Agents planning while targeting DeltaScaleDemo. The app now exposes `/api/context`, shows Target/System roots in the sidebar, and the startup skill requires verifying context before reporting success. |
| 2026-07-18 | Sidebar shows Project Repo, Project Layer, and System as separate roots | The target repository root must be visible independently from the target Project Layer and the Adaptive Agents system home. This makes wrong-root startup failures obvious in the UI. |

## Verification

Closure: Completed on 2026-07-18 after the user accepted the shippable MVP. Commit `745134c` was pushed to `origin/pl-20260717-markdown-browser` with upstream tracking.

- `py -3 scripts/ui.py generate --target .` produces `ui/markdown-browser/index.html` and `app.js` — AC1 ✓
- `py -3 scripts/ui.py serve --target . --no-open` starts and responds:
  - `GET /api/tree` returns JSON with directory entries — AC3 ✓
  - `GET /` returns `index.html` with `Content-Type: text/html` — AC2 (port 8099) ✓
  - `GET /api/file?path=README.md` returns file with `Content-Type: text/markdown` — AC4 ✓
  - `GET /events` returns `Content-Type: text/event-stream` — AC6 ✓
- Markdown links with `.md` extension are intercepted and navigated via History API — AC8 ✓
- Dark mode support via `prefers-color-scheme` CSS media query
- Server exits cleanly on Ctrl+C (tested in isolation)
- SSE keepalive sent every 30s when no events
- Path traversal protection via `full.relative_to(target_root.resolve())` and `full.relative_to(system_home.resolve())` checks
- Event broker unit tests prove one publication reaches every subscriber and unsubscribed clients stop receiving events
- Playwright includes a two-client live-update regression: one filesystem save updates both rendered DOMs without navigation or reload
- Playwright verifies `/api/index-tree`, sidebar navigation to `.adaptive-agents/planning/INDEX.md`, and collapse/expand behavior for nested index branches
- Playwright verifies `/api/system-index-tree`, `system:INDEX.md` file serving, top-level System areas, fallback instruction/prompt/skill children, and that System navigation avoids rendering root Markdown links as sidebar items
- `scripts/test-project-layer.sh` verifies bootstrap writes `adaptiveAgentsHome` into new Project Layer manifests so non-dogfood projects can locate the canonical Adaptive Agents home
- URL-encoded paths (%%2F) handled correctly via `urllib.parse.parse_qs`
- Sidebar restored for quick navigation across Project Layer `INDEX.md` pages; app still starts on `.adaptive-agents/INDEX.md` as home page
- `ThreadingHTTPServer` handles SSE + regular requests concurrently
- No Python warnings on startup (escaped regex fixed to `slice(1)`)
- Existing `.adaptive-agents/scripts/ui.py` path is now a compatibility wrapper around the system-owned implementation
- External target validation: `py -3 scripts/ui.py serve --target /tmp/tmp.KizT4Yov2W --port 8101 --no-open` served a disposable non-Adaptive-Agents project root while `system:INDEX.md` resolved from the canonical Adaptive Agents repository
- `skills/start-markdown-browser/SKILL.md` routes natural requests like "start the Adaptive Agents browser" into a no-fuss server startup workflow
- DeltaScaleDemo wrong-root regression check: `http://127.0.0.1:8102/api/context` reported `targetRoot` as `E:\github.com\Justin-Randall\DeltaScaleDemo`; target `.adaptive-agents/planning/INDEX.md` returned "No active plan" while `system:.adaptive-agents/planning/INDEX.md` returned Adaptive Agents' active Markdown Browser work
- Playwright now verifies `/api/context` and visible Target/System sidebar labels; run with `BROWSER_BASE_URL=http://127.0.0.1:<port>` for isolated validation ports
- Project Repo sidebar validation: `http://127.0.0.1:8105/api/tree` reported root name `DeltaScaleDemo` and target planning continued to return "No active plan"

## Supporting Documents

- [PL-20260717-markdown-browser memory](PL-20260717-markdown-browser.memory.md)
