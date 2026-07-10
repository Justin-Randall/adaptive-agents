# PL-20260710T100000Z: Project Layer Web UI

- Status: Backlog
- Readiness: Ready
- Created: 2026-07-10

## Objective

Build a browsable, editable web interface that surfaces all Project Layer artifacts — planning, backlog, active work, retrospectives, instructions, skills, memory, and playbooks — without requiring directory-tree navigation.

## Scope

- Start as a purely client-side single-page application that loads `.adaptive-agents/` as a local directory or mounted path.
- Design the architecture so the same SPA can be served from any HTTP server, with a future API layer as a separate concern.
- Surface all artifact types: active plan (with task checklists), backlog (reorderable), closed work, retrospectives (with status/scope badges), instructions, skills, memory, and playbooks.
- Provide Markdown editing for all editable documents.
- Support drag-and-drop backlog reordering with persistent save-back to the index file.
- Run the Project Layer validator and display results inline.
- Visualize the linked document graph as a simple navigable tree or force-directed graph.
- Respect the layer's source-control policy: edits write through to the underlying Markdown files.

## Out of Scope (v0)

- Authentication, user accounts, or multi-user collaboration.
- Real-time sync or WebSocket-based updates.
- Server-side persistence beyond the file system.
- Integration with GitHub, GitLab, or other remote repositories.
- The AI/agent layer — this surface is for human browsing and editing.

## Acceptance Criteria

- [ ] The SPA renders a navigable index of all Project Layer artifacts by reading `.adaptive-agents/INDEX.md`.
- [ ] Each artifact type has a dedicated view that surfaces its key fields and links.
- [ ] Active plan checkboxes can be toggled and persisted.
- [ ] Backlog items can be reordered via drag-and-drop and the index is updated.
- [ ] Markdown files can be edited in-browser and saved back to disk.
- [ ] The validator can be invoked with results displayed in the UI.
- [ ] The linked document graph is shown in at least a basic navigable form.
- [ ] The app works from `file://` protocol and when served via `python -m http.server` or equivalent.
- [ ] The Project Layer validator passes after any structural changes made through the UI.
- [ ] GitHub repository name and local paths are never hard-coded; the UI discovers its layer at runtime.

## Decisions

- Start as a vanilla or framework-light SPA (no React/Vue requirement in this spec; implementer chooses).
- Edits write directly to the Markdown files on the local file system via the File System Access API or a minimal local proxy.
- Architecture keeps a clean seam between front-end rendering and data access so a server-backed mode can be added later.

## Verification

- Not yet run.
