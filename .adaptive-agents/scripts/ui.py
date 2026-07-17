#!/usr/bin/env python3
"""Adaptive Agents Markdown Browser — server and generator.

Usage:
  py -3 .adaptive-agents/scripts/ui.py generate   # write index.html + app.js
  py -3 .adaptive-agents/scripts/ui.py serve      # start HTTP server
"""

import argparse
import json
import mimetypes
import os
import queue
import sys
import threading
import time
import urllib.parse
import webbrowser
from http.server import HTTPServer, ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path

UI_DIR = Path(__file__).resolve().parent.parent / "ui"
REPO_ROOT = Path(__file__).resolve().parent.parent.parent  # adaptive-agents root
PORT = 8099
DEBOUNCE_MS = 0.3  # seconds

event_queue = queue.Queue()


# ---------------------------------------------------------------------------
# Embedded frontend source (canonical copies written by `generate`)
# ---------------------------------------------------------------------------

INDEX_HTML = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Adaptive Agents</title>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<style>
*,::before,::after{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Roboto,Oxygen,Ubuntu,Cantarell,'Helvetica Neue',Arial,sans-serif;background:#fff;color:#1c1c1e;display:flex;height:100vh;overflow:hidden}
@media(prefers-color-scheme:dark){body{background:#1c1c1e;color:#e0e0e0}}
#sidebar{width:280px;min-width:280px;height:100vh;overflow-y:auto;border-right:1px solid #e0dcd8;padding:8px}
@media(prefers-color-scheme:dark){#sidebar{border-right:1px solid #272727}}
#sidebar h3{font-size:11px;text-transform:uppercase;letter-spacing:.05em;color:#666;margin-bottom:8px}
#sidebar ul{list-style:none}
#sidebar li{cursor:pointer;padding:2px 8px;border-radius:4px;font-size:14px}
#sidebar li.dir{font-weight:600}
#sidebar li.file{font-weight:400}
#sidebar li:hover{background:#f0f0f0}
@media(prefers-color-scheme:dark){#sidebar li:hover{background:#333}}
#sidebar li.active{background:#e3e2ff;color:#442abb}
@media(prefers-color-scheme:dark){#sidebar li.active{background:#2a2544;color:#9988ff}}
#sidebar li .icon{display:inline-block;width:16px;text-align:center;margin-right:4px;color:#999}
#sidebar li.dir .icon{color:#db8a00}
#sidebar li.file .icon{color:#442708}
#sidebar .children{display:none}
#sidebar .children.open{display:block}
#sidebar .toggle{cursor:pointer;user-select:none}
#preview{flex:1;height:100vh;overflow-y:auto;padding:24px 32px}
#preview h1{font-size:2.5em;border-bottom:2px solid #e0dcd8;padding-bottom:8px;margin-bottom:16px}
#preview h2{font-size:1.5em;margin-top:24px;margin-bottom:8px}
#preview p{line-height:1.6;margin-bottom:16px}
#preview code{font-family:Consolas,'Courier New',monospace;font-size:13px;background:#f6f8fa;padding:2px 6px;border-radius:3px}
#preview pre{background:#f6f8fa;padding:16px;border-radius:6px;overflow-x:auto;margin-bottom:16px}
#preview pre code{padding:0;background:transparent}
#preview img{max-width:100%;border-radius:4px}
#preview a{color:#442abb;text-decoration:none}
#preview a:hover{text-decoration:underline}
@media(prefers-color-scheme:dark){#preview .description{color:#b4b4b4}#preview pre{background:#2d2d29}#preview code{background:#2d2d29}#preview h1{border-bottom:2px solid #333}#preview a{color:#9988ff}}
blockquote{border-left:4px solid #e0dcd8;padding-left:16px;margin-left:0;color:#666}
@media(prefers-color-scheme:dark){blockquote{border-left:4px solid #333;color:#999}}
#status{position:fixed;bottom:8px;right:8px;padding:4px 10px;border-radius:4px;font-size:12px;background:#000;color:#fff;opacity:.8;pointer-events:none;transition:opacity .3s}
#status.hidden{opacity:0}
</style>
</head>
<body>
<div id="sidebar"><h3>Files</h3><div id="tree"></div></div>
<div id="preview">
  <div id="welcome"><h1>Adaptive Agents</h1><p class="description">Select a file from the sidebar or open a markdown link to get started.</p></div>
  <div id="content" style="display:none"></div>
</div>
<div id="status" class="hidden"></div>
<script src="app.js"></script>
</body>
</html>
"""

APP_JS = """\
const PREVIEW=document.getElementById('preview'),CONTENT=document.getElementById('content'),WELCOME=document.getElementById('welcome'),TREE=document.getElementById('tree'),STATUS=document.getElementById('status');let currentPath=null;
marked.use({breaks:true,gfm:true});
function showStatus(msg,duration){STATUS.textContent=msg;STATUS.classList.remove('hidden');clearTimeout(STATUS._timer);if(duration)STATUS._timer=setTimeout(()=>STATUS.classList.add('hidden'),duration)}
function escapeHtml(t){const e=document.createElement('div');e.textContent=t;return e.innerHTML}
async function loadTree(){const r=await fetch('/api/tree'),t=await r.json();TREE.innerHTML=renderTree(t);if(currentPath){const e=TREE.querySelector(`[data-path="${CSS.escape(currentPath)}"]`);if(e)e.classList.add('active')}}
function renderTree(n){if(n.type==='file')return `<li class="file" data-path="${escapeHtml(n.path)}" onclick="navigateTo('${escapeHtml(n.path)}')"><span class="icon">\\ud83d\\udcc4<\\/span>${escapeHtml(n.name.replace(/\\.md$/,''))}<\\/li>`;const c=(n.children||[]).map(renderTree).join('');if(!n.path)return `<ul>${c}<\\/ul>`;return `<li class="dir"><div class="toggle" onclick="toggleDir(this)"><span class="icon">\\ud83d\\udcc1<\\/span>${escapeHtml(n.name)}<\\/div><ul class="children">${c}<\\/ul><\\/li>`}
function toggleDir(e){e.parentElement.querySelector('.children').classList.toggle('open')}
function navigateTo(pushState){const path=arguments[0];if(path===currentPath)return;currentPath=path;loadFile(path);TREE.querySelectorAll('.active').forEach(e=>e.classList.remove('active'));const e=TREE.querySelector(`[data-path="${CSS.escape(path)}"]`);if(e)e.classList.add('active');if(pushState!==false){const url='/view?path='+encodeURIComponent(path);history.pushState({path},'',url)}}
async function loadFile(path){try{const r=await fetch('/api/file?path='+encodeURIComponent(path));if(!r.ok)throw new Error('HTTP '+r.status);const t=await r.text(),h=marked.parse(t);CONTENT.innerHTML=h;CONTENT.style.display='block';WELCOME.style.display='none';CONTENT.querySelectorAll('a[href]').forEach(anchorHandler);showStatus('Loaded: '+path,2000)}catch(e){CONTENT.innerHTML='<p style=\"color:red\">Error loading <code>'+escapeHtml(path)+'<\\/code>: '+escapeHtml(e.message)+'<\\/p>';CONTENT.style.display='block';WELCOME.style.display='none'}}
function anchorHandler(a){const h=a.getAttribute('href');if(!h)return;if(h.startsWith('http://')||h.startsWith('https://')||h.startsWith('mailto:')||h.startsWith('#'))return;if(h.endsWith('.md')){a.addEventListener('click',e=>{e.preventDefault();const r=resolvePath(currentPath||'',h);navigateTo(r)})}}
function resolvePath(base,target){if(target.startsWith('/'))return target.replace(/^\\//,'');const parts=base.split('/').slice(0,-1).concat(target.split('/')),result=[];for(const p of parts){if(p==='.'||p==='')continue;if(p==='..'){result.pop();continue}result.push(p)}return result.join('/')}
window.addEventListener('popstate',e=>{const p=new URLSearchParams(location.search).get('path')||(e.state&&e.state.path)||null;if(p)navigateTo(p,false);else{currentPath=null;CONTENT.style.display='none';WELCOME.style.display='block'}})
function connectSSE(){const s=new EventSource('/events');s.addEventListener('file_changed',e=>{const d=JSON.parse(e.data);if(d.path===currentPath)loadFile(currentPath)});s.addEventListener('tree_changed',()=>{const p=currentPath;loadTree();showStatus('Files changed - tree updated',2000)});s.onerror=()=>showStatus('SSE reconnecting...',3000)}
loadTree();connectSSE();const ip=new URLSearchParams(location.search).get('path');if(ip)navigateTo(ip);
"""


# ---------------------------------------------------------------------------
# Generate subcommand
# ---------------------------------------------------------------------------

def cmd_generate():
    UI_DIR.mkdir(parents=True, exist_ok=True)
    (UI_DIR / "index.html").write_text(INDEX_HTML, encoding="utf-8")
    (UI_DIR / "app.js").write_text(APP_JS, encoding="utf-8")
    print(f"Generated {UI_DIR / 'index.html'}")
    print(f"Generated {UI_DIR / 'app.js'}")


# ---------------------------------------------------------------------------
# File tree builder
# ---------------------------------------------------------------------------

def build_tree(base: Path) -> dict:
    """Build a JSON-serializable directory tree of markdown files."""
    children = []
    try:
        entries = sorted(base.iterdir(), key=lambda e: (not e.is_dir(), e.name.lower()))
    except PermissionError:
        return {"name": base.name, "type": "directory", "children": []}

    for entry in entries:
        if entry.name.startswith(".") or entry.name.startswith("node_modules"):
            continue
        if entry.is_dir():
            sub = build_tree(entry)
            if sub.get("children"):
                children.append(sub)
        elif entry.suffix == ".md" and entry.name != "INDEX.md":
            children.append({
                "name": entry.name,
                "type": "file",
                "path": str(entry.relative_to(REPO_ROOT).as_posix()),
            })
    return {"name": base.name, "type": "directory", "children": children}


def tree_json():
    tree = build_tree(REPO_ROOT)
    tree["name"] = REPO_ROOT.name
    return tree


# ---------------------------------------------------------------------------
# Watchdog integration
# ---------------------------------------------------------------------------

class WatchdogWatcher:
    """Monitors the repo root for file changes and puts events on the queue."""

    def __init__(self):
        self._observer = None
        self._running = False
        self._debounce_timer = None
        self._lock = threading.Lock()
        self._pending = set()

    def start(self):
        try:
            from watchdog.observers import Observer
            from watchdog.events import FileSystemEventHandler
        except ImportError:
            return  # watchdog not available — SSE events won't fire

        class Handler(FileSystemEventHandler):
            def on_any_event(_, event):
                if event.is_directory:
                    return
                src = event.src_path
                try:
                    rel = str(Path(src).relative_to(REPO_ROOT).as_posix())
                except ValueError:
                    return
                if not rel.endswith(".md"):
                    return
                with self._lock:
                    self._pending.add(rel)
                if self._debounce_timer and self._debounce_timer.is_alive():
                    return
                self._debounce_timer = threading.Timer(DEBOUNCE_MS, self._flush)
                self._debounce_timer.start()

        self._observer = Observer()
        self._observer.schedule(Handler(), str(REPO_ROOT), recursive=True)
        self._observer.start()
        self._running = True

    def _flush(self):
        with self._lock:
            batch = list(self._pending)
            self._pending.clear()
        tree_changed = False
        for path in batch:
            full = REPO_ROOT / path
            if full.exists():
                event_queue.put(("file_changed", {"path": path}))
            else:
                event_queue.put(("file_removed", {"path": path}))
                tree_changed = True
        if tree_changed:
            # also check for new files (watchdog doesn't always fire "created")
            event_queue.put(("tree_changed", {}))
        # periodic tree refresh in case of new files
        event_queue.put(("tree_changed", {}))

    def stop(self):
        self._running = False
        if self._debounce_timer:
            self._debounce_timer.cancel()
        if self._observer:
            self._observer.stop()
            self._observer.join()


# ---------------------------------------------------------------------------
# HTTP Request Handler
# ---------------------------------------------------------------------------

class Handler(BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        pass  # quieter output

    def _send_json(self, data, status=200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)
        self.wfile.flush()

    def _send_text(self, text, content_type="text/plain", status=200):
        body = text.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)
        self.wfile.flush()

    def _serve_static(self, path, content_type=None):
        full = UI_DIR / path
        if not full.exists() or not full.is_file():
            self._send_text("Not Found", status=404)
            return
        body = full.read_bytes()
        if content_type is None:
            content_type, _ = mimetypes.guess_type(str(full))
            content_type = content_type or "application/octet-stream"
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)
        self.wfile.flush()

    def do_GET(self):
        parsed = self.path.split("?", 1)
        path = parsed[0]
        query = parsed[1] if len(parsed) > 1 else ""

        # API routes
        if path == "/api/tree":
            return self._send_json(tree_json())

        if path == "/api/file":
            params = urllib.parse.parse_qs(query)
            file_path = params.get("path", [""])[0]
            full = (REPO_ROOT / file_path).resolve()
            try:
                full.relative_to(REPO_ROOT.resolve())
            except ValueError:
                return self._send_text("Forbidden", status=403)
            if not full.exists() or not full.is_file():
                return self._send_text("Not Found", status=404)
            content_type, _ = mimetypes.guess_type(str(full))
            content_type = content_type or "application/octet-stream"
            body = full.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(body)
            self.wfile.flush()
            return

        if path == "/events":
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            sid = id(self)
            try:
                while True:
                    try:
                        event_type, data = event_queue.get(timeout=30)
                        line = f"event: {event_type}\ndata: {json.dumps(data)}\n\n"
                        self.wfile.write(line.encode("utf-8"))
                        self.wfile.flush()
                    except queue.Empty:
                        # Send keepalive comment
                        self.wfile.write(": keepalive\n\n".encode("utf-8"))
                        self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError):
                pass
            return

        # Serve UI app files
        if path == "/" or path == "":
            return self._serve_static("index.html", "text/html")
        if path == "/app.js":
            return self._serve_static("app.js", "application/javascript")

        # Serve repo files at their actual paths (for images, etc.)
        full = (REPO_ROOT / path.lstrip("/")).resolve()
        try:
            full.relative_to(REPO_ROOT.resolve())
        except ValueError:
            return self._send_text("Forbidden", status=403)
        if full.exists() and full.is_file():
            content_type, _ = mimetypes.guess_type(str(full))
            content_type = content_type or "application/octet-stream"
            body = full.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(body)
            self.wfile.flush()
            return

        # View route
        if path.startswith("/view"):
            params = urllib.parse.parse_qs(query)
            file_path = params.get("path", [""])[0]
            if file_path:
                return self._serve_static("index.html", "text/html")
            return self._send_text("Missing path parameter", status=400)

        self._send_text("Not Found", status=404)

    def do_HEAD(self):
        self.do_GET()


# ---------------------------------------------------------------------------
# Serve subcommand
# ---------------------------------------------------------------------------

def cmd_serve():
    # Auto-generate if output files are missing
    if not (UI_DIR / "index.html").exists() or not (UI_DIR / "app.js").exists():
        print("UI files missing — generating…")
        cmd_generate()

    # Start watchdog watcher
    watcher = WatchdogWatcher()
    watcher.start()

    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    url = f"http://localhost:{PORT}"

    print(f"Adaptive Agents Markdown Browser")
    print(f"Serving from: {REPO_ROOT}")
    print(f"Open:         {url}")
    print("Press Ctrl+C to stop.")

    webbrowser.open(url)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down…")
    finally:
        server.shutdown()
        watcher.stop()


# ---------------------------------------------------------------------------
# CLI Entrypoint
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    subcommand = sys.argv[1]

    # Check Python version
    if sys.version_info < (3, 9):
        print("Error: Python 3.9+ is required (watchdog requirement).", file=sys.stderr)
        sys.exit(1)

    if subcommand == "generate":
        cmd_generate()
    elif subcommand == "serve":
        cmd_serve()
    else:
        print(f"Unknown subcommand: {subcommand}", file=sys.stderr)
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
