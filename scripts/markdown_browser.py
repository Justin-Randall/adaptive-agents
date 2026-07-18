#!/usr/bin/env python3
"""Adaptive Agents Markdown Browser server and generator.

Usage:
  py -3 scripts/ui.py generate [--target PATH]
  py -3 scripts/ui.py serve [--target PATH] [--port 8099]

The browser is owned by the canonical Adaptive Agents repository and targets a
selected project root. The target project's `.adaptive-agents` directory is
shown as the Project Layer tree; the canonical repository is shown as System.
"""

import argparse
from dataclasses import dataclass
import json
import mimetypes
import queue
import re
import sys
import threading
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


SYSTEM_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_UI_DIR = SYSTEM_ROOT / "ui" / "markdown-browser"
DEFAULT_PORT = 8099
DEBOUNCE_SECONDS = 0.3
IGNORED_WATCH_PARTS = {".git", "__pycache__", "node_modules", "playwright-report"}
SYSTEM_AREA_NAMES = (
    "instructions",
    "skills",
    "agents",
    "prompts",
    "memory",
    "playbooks",
    "retrospectives",
    "schemas",
    "templates",
    "scripts",
)
_LINK_PATTERN = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


@dataclass(frozen=True)
class BrowserConfig:
    target_root: Path
    system_root: Path = SYSTEM_ROOT
    ui_dir: Path = DEFAULT_UI_DIR
    port: int = DEFAULT_PORT

    @property
    def project_layer_root(self):
        return self.target_root / ".adaptive-agents"

    @property
    def system_home(self):
        manifest = self.project_layer_root / "project-layer.json"
        if manifest.exists():
            try:
                data = json.loads(manifest.read_text(encoding="utf-8"))
                configured_home = data.get("adaptiveAgentsHome") or data.get("agentsHome")
                if configured_home:
                    return Path(configured_home).resolve()
            except (json.JSONDecodeError, OSError):
                pass
        return self.system_root.resolve()

    @classmethod
    def create(cls, target_root=None, system_root=SYSTEM_ROOT, ui_dir=None, port=DEFAULT_PORT):
        resolved_system_root = Path(system_root).resolve()
        return cls(
            target_root=Path(target_root or Path.cwd()).resolve(),
            system_root=resolved_system_root,
            ui_dir=Path(ui_dir or resolved_system_root / "ui" / "markdown-browser").resolve(),
            port=port,
        )


def _default_config():
    return BrowserConfig.create(SYSTEM_ROOT)


CONFIG = _default_config()


class EventBroker:
    def __init__(self):
        self._lock = threading.Lock()
        self._subscribers = set()

    def subscribe(self):
        subscriber = queue.Queue()
        with self._lock:
            self._subscribers.add(subscriber)
        return subscriber

    def unsubscribe(self, subscriber):
        with self._lock:
            self._subscribers.discard(subscriber)

    def publish(self, event_type, data):
        with self._lock:
            subscribers = tuple(self._subscribers)
        for subscriber in subscribers:
            subscriber.put((event_type, data))


event_broker = EventBroker()


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
:root{color-scheme:light}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Roboto,Oxygen,Ubuntu,Cantarell,'Helvetica Neue',Arial,sans-serif;background:#fff;color:#1c1c1e}
@media(prefers-color-scheme:dark){:root{color-scheme:dark}body{background:#1c1c1e;color:#e0e0e0}}
.app{display:grid;grid-template-columns:280px minmax(0,1fr);min-height:100vh}
#sidebar{position:sticky;top:0;height:100vh;overflow:auto;border-right:1px solid #e0dcd8;background:#fbfaf8;padding:22px 16px;scrollbar-width:thin;scrollbar-color:#b8afa6 transparent}
#sidebar::-webkit-scrollbar{width:10px}
#sidebar::-webkit-scrollbar-track{background:transparent}
#sidebar::-webkit-scrollbar-thumb{background:#b8afa6;border:3px solid #fbfaf8;border-radius:999px}
#sidebar::-webkit-scrollbar-thumb:hover{background:#8f867d}
#sidebar h2{font-size:13px;font-weight:650;text-transform:uppercase;letter-spacing:.08em;color:#6b645d;margin-bottom:14px}
.context-panel{border-bottom:1px solid #e0dcd8;margin:-8px 0 18px;padding:0 0 14px}
.context-row{margin-top:8px}
.context-label{display:block;font-size:11px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:#8f867d;margin-bottom:2px}
.context-value{display:block;color:#3b342e;font-size:12px;line-height:1.35;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.sidebar-section+.sidebar-section{margin-top:18px}
.nav-tree ul{list-style:none;padding-left:14px;margin-top:4px}
.nav-tree>ul{padding-left:0}
.nav-tree li{margin:2px 0}
.nav-tree .tree-row{display:grid;grid-template-columns:24px minmax(0,1fr);align-items:center;border-radius:6px}
.nav-tree button{width:22px;height:22px;border:0;border-radius:4px;background:transparent;color:#6b645d;cursor:pointer;font-size:14px;line-height:1}
.nav-tree button:hover{background:#efebe7;color:#3b342e}
.nav-tree button.empty{visibility:hidden;pointer-events:none}
.nav-tree li.collapsed>ul{display:none}
.nav-tree a,.nav-tree .node-label{display:block;border-radius:6px;color:#3b342e;font-size:14px;line-height:1.35;padding:6px 8px;text-decoration:none;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.nav-tree a:hover{background:#efebe7;text-decoration:none}
.nav-tree a.active{background:#e7e0ff;color:#2e1c96;font-weight:650}
#content{max-width:860px;margin:0 auto;padding:32px 24px;min-height:100vh}
#content h1{font-size:2.5em;border-bottom:2px solid #e0dcd8;padding-bottom:8px;margin-bottom:16px}
#content h2{font-size:1.5em;margin-top:24px;margin-bottom:8px}
#content p{line-height:1.6;margin-bottom:16px}
#content ul,#content ol{margin-bottom:16px;padding-left:24px}
#content li{line-height:1.6;margin-bottom:4px}
#content code{font-family:Consolas,'Courier New',monospace;font-size:13px;background:#f6f8fa;padding:2px 6px;border-radius:3px}
#content pre{background:#f6f8fa;padding:16px;border-radius:6px;overflow-x:auto;margin-bottom:16px}
#content pre code{padding:0;background:transparent}
#content img{max-width:100%;border-radius:4px}
#content a{color:#442abb;text-decoration:none}
#content a:hover{text-decoration:underline}
#content table{border-collapse:collapse;margin-bottom:16px;width:100%}
#content th,#content td{border:1px solid #ddd;padding:8px 12px;text-align:left}
#content th{background:#f6f8fa}
@media(prefers-color-scheme:dark){#sidebar{background:#222220;border-right-color:#333;scrollbar-color:#5f5f58 transparent}#sidebar::-webkit-scrollbar-thumb{background:#5f5f58;border-color:#222220}#sidebar::-webkit-scrollbar-thumb:hover{background:#77776f}#sidebar h2{color:#aaa}.context-panel{border-bottom-color:#333}.context-label{color:#888}.context-value{color:#ddd}.nav-tree button{color:#aaa}.nav-tree button:hover{background:#302f2c;color:#ddd}.nav-tree a,.nav-tree .node-label{color:#ddd}.nav-tree a:hover{background:#302f2c}.nav-tree a.active{background:#332b5f;color:#c8c0ff}#content pre{background:#2d2d29}#content code{background:#2d2d29}#content h1{border-bottom:2px solid #333}#content a{color:#9988ff}#content th,#content td{border-color:#333}#content th{background:#2d2d29}}
blockquote{border-left:4px solid #e0dcd8;padding-left:16px;margin-left:0;color:#666}
@media(prefers-color-scheme:dark){blockquote{border-left:4px solid #333;color:#999}}
#status{position:fixed;bottom:8px;right:8px;padding:4px 10px;border-radius:4px;font-size:12px;background:#000;color:#fff;opacity:.8;pointer-events:none;transition:opacity .3s}
#status.hidden{opacity:0}
@media(max-width:760px){.app{display:block}#sidebar{position:relative;height:auto;max-height:38vh;border-right:0;border-bottom:1px solid #e0dcd8}#content{padding:24px 18px}#content h1{font-size:2em}}
</style>
</head>
<body>
<div class="app">
<nav id="sidebar" aria-label="Page navigation"><section class="context-panel" aria-label="Browser context"><div class="context-row"><span class="context-label">Target</span><span id="target-root" class="context-value">Loading...</span></div><div class="context-row"><span class="context-label">System</span><span id="system-root" class="context-value">Loading...</span></div></section><section class="sidebar-section"><h2>Project Repo</h2><div id="root-tree" class="nav-tree"></div></section><section class="sidebar-section"><h2>Project Layer</h2><div id="index-tree" class="nav-tree"></div></section><section class="sidebar-section" id="system-section" hidden><h2>System</h2><div id="system-tree" class="nav-tree"></div></section></nav>
<main id="content"></main>
</div>
<div id="status" class="hidden"></div>
<script src="app.js"></script>
</body>
</html>
"""

APP_JS = """\
const C=document.getElementById('content'),S=document.getElementById('status'),RT=document.getElementById('root-tree'),T=document.getElementById('index-tree'),SS=document.getElementById('system-section'),ST=document.getElementById('system-tree'),TR=document.getElementById('target-root'),SR=document.getElementById('system-root');let currentPath=null,rootTree=null,indexTree=null,systemTree=null;const rootCollapsedPaths=new Set(),projectCollapsedPaths=new Set(),systemCollapsedPaths=new Set();
function ready(fn){if(typeof marked!=='undefined'&&marked){fn()}else setTimeout(()=>ready(fn),50)}
function showStatus(msg,duration){S.textContent=msg;S.classList.remove('hidden');clearTimeout(S._timer);if(duration)S._timer=setTimeout(()=>S.classList.add('hidden'),duration)}
function escapeHtml(t){const e=document.createElement('div');e.textContent=t;return e.innerHTML}
function navigateTo(path,pushState){
 if(path===currentPath)return;currentPath=path;loadFile(path);updateActiveNav();
 if(pushState!==false){const url='/view?path='+encodeURIComponent(path);history.pushState({path},'',url)}
}
async function loadFile(path){
 try{const r=await fetch('/api/file?path='+encodeURIComponent(path));if(!r.ok)throw new Error('HTTP '+r.status);const t=await r.text(),h=marked.parse(t);C.innerHTML=h;showStatus('Loaded: '+path,2000);C.querySelectorAll('a[href]').forEach(anchorHandler)}
 catch(e){C.innerHTML='<p style="color:red">Error loading <code>'+escapeHtml(path)+'</code>: '+escapeHtml(e.message)+'</p>'}
}
function anchorHandler(a){const h=a.getAttribute('href');if(!h)return;if(h.startsWith('http://')||h.startsWith('https://')||h.startsWith('mailto:')||h.startsWith('#'))return;if(h.endsWith('.md')){a.addEventListener('click',e=>{e.preventDefault();navigateTo(resolvePath(currentPath||'',h))})}}
function resolvePath(base,target){if(base.startsWith('system:')){const innerBase=base.slice(7),innerTarget=target.startsWith('/')?target.slice(1):target;return 'system:'+resolveRelativePath(innerBase,innerTarget)}if(target.startsWith('/'))return target.slice(1);return resolveRelativePath(base,target)}
function resolveRelativePath(base,target){const parts=base.split('/').slice(0,-1).concat(target.split('/')),result=[];for(const p of parts){if(p==='.'||p==='')continue;if(p==='..'){result.pop();continue}result.push(p)}return result.join('/')}
window.addEventListener('popstate',e=>{const p=new URLSearchParams(location.search).get('path')||(e.state&&e.state.path)||null;if(p)navigateTo(p,false);else navigateTo('.adaptive-agents/INDEX.md',false)})
async function loadRootTree(){try{const r=await fetch('/api/tree');if(!r.ok)throw new Error('HTTP '+r.status);rootTree=await r.json();rootCollapsedPaths.clear();renderTree(RT,rootTree,rootCollapsedPaths,renderRootTree)}catch(e){RT.innerHTML='<p style="font-size:13px;color:#a33">Project repo unavailable</p>'}}
async function loadIndexTree(){try{const r=await fetch('/api/index-tree');if(!r.ok)throw new Error('HTTP '+r.status);indexTree=await r.json();projectCollapsedPaths.clear();renderTree(T,indexTree,projectCollapsedPaths,renderIndexTree)}catch(e){T.innerHTML='<p style="font-size:13px;color:#a33">Navigation unavailable</p>'}}
async function loadSystemTree(){try{const r=await fetch('/api/system-index-tree');if(!r.ok)throw new Error('HTTP '+r.status);systemTree=await r.json();systemCollapsedPaths.clear();SS.hidden=false;renderTree(ST,systemTree,systemCollapsedPaths,renderSystemTree)}catch(e){systemTree=null;SS.hidden=true;ST.innerHTML=''}}
async function loadContext(){try{const r=await fetch('/api/context');if(!r.ok)throw new Error('HTTP '+r.status);const c=await r.json();TR.textContent=c.targetName+' — '+c.targetRoot;TR.title=c.targetRoot;SR.textContent=c.systemName+' — '+c.systemHome;SR.title=c.systemHome;document.title='Adaptive Agents — '+c.targetName}catch(e){TR.textContent='Context unavailable';SR.textContent='Context unavailable'}}
function renderRootTree(){if(rootTree)renderTree(RT,rootTree,rootCollapsedPaths,renderRootTree)}
function renderIndexTree(){if(indexTree)renderTree(T,indexTree,projectCollapsedPaths,renderIndexTree)}
function renderSystemTree(){if(systemTree)renderTree(ST,systemTree,systemCollapsedPaths,renderSystemTree)}
function renderTree(container,tree,collapsedSet,rerender){container.innerHTML='';container.appendChild(renderNodeList([tree],0,collapsedSet,rerender));updateActiveNav()}
function renderNodeList(nodes,depth,collapsedSet,rerender){const ul=document.createElement('ul');for(const node of nodes){const subItems=[].concat(node.children||[],node.links||[]),hasSubContent=subItems.length>0,li=document.createElement('li'),row=document.createElement('div'),button=document.createElement('button'),label=node.path?document.createElement('a'):document.createElement('span');row.className='tree-row';button.type='button';button.dataset.path=node.path||node.name;if(hasSubContent){const key=node.path||node.name,defaultCollapsed=depth>0,isCollapsed=collapsedSet.has(key)?!defaultCollapsed:defaultCollapsed;li.classList.toggle('collapsed',isCollapsed);button.textContent=isCollapsed?'▸':'▾';button.setAttribute('aria-label',(isCollapsed?'Expand ':'Collapse ')+node.name);button.setAttribute('aria-expanded',String(!isCollapsed));button.addEventListener('click',()=>{if(collapsedSet.has(key))collapsedSet.delete(key);else collapsedSet.add(key);rerender()})}else{button.className='empty';button.textContent='';button.setAttribute('aria-hidden','true');button.tabIndex=-1}label.textContent=node.name;if(node.path){label.href='/view?path='+encodeURIComponent(node.path);label.dataset.path=node.path;label.addEventListener('click',e=>{e.preventDefault();navigateTo(node.path)})}else{label.className='node-label'}row.appendChild(button);row.appendChild(label);li.appendChild(row);if(hasSubContent)li.appendChild(renderNodeList(subItems,depth+1,collapsedSet,rerender));ul.appendChild(li)}return ul}
function updateActiveNav(){const all=[RT,T,ST];for(const el of all)if(el)el.querySelectorAll('a').forEach(a=>a.classList.toggle('active',a.dataset.path===currentPath))}
function connectSSE(){const s=new EventSource('/events');s.addEventListener('file_changed',e=>{const d=JSON.parse(e.data);if(d.path===currentPath)loadFile(currentPath)});s.addEventListener('file_added',e=>{const d=JSON.parse(e.data);if(d.path===currentPath)loadFile(currentPath);showStatus('File added: '+d.path,3000)});s.addEventListener('file_removed',e=>{const d=JSON.parse(e.data);if(d.path===currentPath)navigateTo('.adaptive-agents/INDEX.md',false);showStatus('File removed: '+d.path,3000)});s.addEventListener('tree_changed',()=>{loadRootTree();loadIndexTree();loadSystemTree()});s.onerror=()=>showStatus('SSE reconnecting...',3000)}
ready(()=>{marked.use({breaks:true,gfm:true});connectSSE();loadContext();loadRootTree();loadIndexTree();loadSystemTree();const ip=new URLSearchParams(location.search).get('path');if(ip)navigateTo(ip,false);else navigateTo('.adaptive-agents/INDEX.md',false)})
"""


def set_config(config):
    global CONFIG
    CONFIG = config


def cmd_generate(config=None):
    active_config = config or CONFIG
    active_config.ui_dir.mkdir(parents=True, exist_ok=True)
    (active_config.ui_dir / "index.html").write_text(INDEX_HTML, encoding="utf-8")
    (active_config.ui_dir / "app.js").write_text(APP_JS, encoding="utf-8")
    print(f"Generated {active_config.ui_dir / 'index.html'}")
    print(f"Generated {active_config.ui_dir / 'app.js'}")


def build_tree(base, target_root=None):
    root = Path(target_root or CONFIG.target_root).resolve()
    children = []
    try:
        entries = sorted(Path(base).iterdir(), key=lambda e: (not e.is_dir(), e.name.lower()))
    except PermissionError:
        return {"name": Path(base).name, "type": "directory", "children": []}

    for entry in entries:
        if entry.name.startswith(".") or entry.name.startswith("node_modules"):
            continue
        if entry.is_dir():
            sub = build_tree(entry, root)
            if sub.get("children"):
                children.append(sub)
        elif entry.suffix == ".md" and entry.name != "INDEX.md":
            children.append({
                "name": entry.name,
                "type": "file",
                "path": str(entry.relative_to(root).as_posix()),
            })
    return {"name": Path(base).name, "type": "directory", "children": children}


def tree_json(config=None):
    active_config = config or CONFIG
    tree = build_tree(active_config.target_root, active_config.target_root)
    tree["name"] = active_config.target_root.name
    return tree


def context_json(config=None):
    active_config = config or CONFIG
    project_manifest = active_config.project_layer_root / "project-layer.json"
    project_name = active_config.target_root.name
    if project_manifest.exists():
        try:
            data = json.loads(project_manifest.read_text(encoding="utf-8"))
            project_name = data.get("projectName") or project_name
        except (json.JSONDecodeError, OSError):
            pass
    return {
        "targetName": project_name,
        "targetRoot": str(active_config.target_root),
        "projectLayerRoot": str(active_config.project_layer_root),
        "projectLayerExists": active_config.project_layer_root.exists(),
        "systemName": "Adaptive Agents",
        "systemHome": str(active_config.system_home),
        "systemRoot": str(active_config.system_root),
    }


def build_index_tree(base, root, visited_paths=None, include_links=True, path_prefix=""):
    base = Path(base)
    root = Path(root)
    index_path = base / "INDEX.md"
    if not index_path.exists():
        return None

    if visited_paths is None:
        visited_paths = set()

    rel_path = str(index_path.relative_to(root).as_posix())
    visited_paths.add(rel_path)

    children = []
    try:
        entries = sorted(base.iterdir(), key=lambda e: e.name.lower())
    except PermissionError:
        entries = []

    for entry in entries:
        if entry.is_dir():
            if entry.name.startswith("."):
                continue
            child = build_index_tree(entry, root, visited_paths, include_links, path_prefix)
            if child:
                children.append(child)

    links = []
    if include_links:
        try:
            text = index_path.read_text(encoding="utf-8")
            for match in _LINK_PATTERN.finditer(text):
                alt_text = match.group(1)
                target = match.group(2).split("#", 1)[0]
                if not target or target.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                if not target.endswith(".md"):
                    continue
                resolved = (root / rel_path).parent / target
                resolved = resolved.resolve()
                try:
                    link_rel = str(resolved.relative_to(root.resolve()).as_posix())
                except ValueError:
                    continue
                if link_rel in visited_paths:
                    continue
                if not resolved.exists() or not resolved.is_file():
                    continue
                visited_paths.add(link_rel)
                links.append({
                    "name": alt_text,
                    "type": "link",
                    "path": f"{path_prefix}{link_rel}",
                })
        except (OSError, UnicodeDecodeError):
            links = []

    return {
        "name": base.name,
        "type": "index",
        "path": f"{path_prefix}{rel_path}",
        "children": children,
        "links": links,
    }


def index_tree_json(config=None):
    active_config = config or CONFIG
    tree = build_index_tree(active_config.project_layer_root, active_config.target_root)
    if tree is None:
        return {"name": ".adaptive-agents", "type": "index", "path": ".adaptive-agents/INDEX.md", "children": []}
    return tree


def system_path(path, config=None):
    active_config = config or CONFIG
    return f"system:{Path(path).relative_to(active_config.system_home).as_posix()}"


def system_display_name(path):
    name = Path(path).name
    for suffix in (".patch.prompt.md", ".prompt.md", ".instructions.md", ".md", ".json", ".sh", ".py"):
        if name.endswith(suffix):
            return name[:-len(suffix)]
    return Path(path).stem


def system_node_for_file(path, config=None):
    return {
        "name": system_display_name(path),
        "type": "file",
        "path": system_path(path, config),
        "children": [],
        "links": [],
    }


def system_entry_document(directory):
    for name in ("INDEX.md", "README.md", "SKILL.md"):
        candidate = Path(directory) / name
        if candidate.exists() and candidate.is_file():
            return candidate
    return None


def system_area_child_node(entry, area_name, config=None):
    if entry.name.startswith("."):
        return None

    if entry.is_file():
        if entry.name in {"INDEX.md", "README.md"}:
            return None
        if area_name == "scripts" and entry.suffix in {".sh", ".py"}:
            return system_node_for_file(entry, config)
        if area_name == "schemas" and entry.suffix == ".json":
            return system_node_for_file(entry, config)
        if entry.suffix == ".md":
            return system_node_for_file(entry, config)
        return None

    if not entry.is_dir():
        return None

    document = system_entry_document(entry)
    children = system_area_children(entry, area_name, config)
    node = {
        "name": entry.name,
        "type": "area" if document is None else "index",
        "children": children,
        "links": [],
    }
    if document is not None:
        node["path"] = system_path(document, config)
    if node.get("path") or children:
        return node
    return None


def system_area_children(directory, area_name, config=None):
    try:
        entries = sorted(Path(directory).iterdir(), key=lambda e: (not e.is_dir(), e.name.lower()))
    except PermissionError:
        return []

    children = []
    for entry in entries:
        child = system_area_child_node(entry, area_name, config)
        if child:
            children.append(child)
    return children


def build_system_area_tree(area, config=None):
    document = system_entry_document(area)
    children = system_area_children(area, Path(area).name, config)
    node = {
        "name": Path(area).name,
        "type": "area" if document is None else "index",
        "children": children,
        "links": [],
    }
    if document is not None:
        node["path"] = system_path(document, config)
    return node


def system_index_tree_json(config=None):
    active_config = config or CONFIG
    system_home = active_config.system_home
    if not system_home or not (system_home / "INDEX.md").exists():
        return None
    children = []
    for area_name in SYSTEM_AREA_NAMES:
        area = system_home / area_name
        if area.exists() and area.is_dir():
            children.append(build_system_area_tree(area, active_config))
    return {
        "name": "Adaptive Agents",
        "type": "index",
        "path": "system:INDEX.md",
        "children": children,
        "links": [],
    }


def resolve_requested_file(file_path, config=None):
    active_config = config or CONFIG
    if file_path.startswith("system:"):
        root = active_config.system_home.resolve()
        relative_path = file_path[len("system:"):]
    else:
        root = active_config.target_root.resolve()
        relative_path = file_path

    full = (root / relative_path).resolve()
    try:
        full.relative_to(root)
    except ValueError:
        return None
    return full


class WatchdogWatcher:
    """Monitors the target project root and publishes file changes to SSE clients."""

    def __init__(self, config=None, broker=event_broker):
        self._config = config or CONFIG
        self._broker = broker
        self._observer = None
        self._debounce_timer = None
        self._lock = threading.Lock()
        self._pending = set()
        self._known_paths = set()

    def start(self):
        try:
            from watchdog.events import FileSystemEventHandler
            from watchdog.observers import Observer
        except ImportError:
            print("watchdog not installed - file reactivity disabled")
            return

        target_root = self._config.target_root.resolve()

        class Handler(FileSystemEventHandler):
            def on_any_event(_, event):
                if event.is_directory:
                    return
                src_path = Path(event.src_path)
                if src_path.suffix != ".md":
                    return
                try:
                    rel_path = src_path.resolve().relative_to(target_root)
                except ValueError:
                    return
                if IGNORED_WATCH_PARTS.intersection(rel_path.parts):
                    return
                rel = str(rel_path.as_posix())
                with self._lock:
                    self._pending.add(rel)
                if self._debounce_timer is not None:
                    self._debounce_timer.cancel()
                self._debounce_timer = threading.Timer(DEBOUNCE_SECONDS, self._flush)
                self._debounce_timer.start()

        self._observer = Observer()
        self._observer.schedule(Handler(), str(target_root), recursive=True)
        self._observer.start()
        print(f"watchdog observer started on {target_root}")

    def _flush(self):
        with self._lock:
            batch = list(self._pending)
            self._pending.clear()
        if not batch:
            return
        tree_changed = False
        for path in batch:
            full = self._config.target_root / path
            exists = full.exists()
            was_known = path in self._known_paths
            if exists:
                self._broker.publish("file_changed", {"path": path})
                if not was_known:
                    tree_changed = True
            elif was_known:
                self._broker.publish("file_removed", {"path": path})
                tree_changed = True
            if exists:
                self._known_paths.add(path)
            else:
                self._known_paths.discard(path)
        if tree_changed:
            self._broker.publish("tree_changed", {})
        with self._lock:
            if self._pending:
                self._debounce_timer = threading.Timer(DEBOUNCE_SECONDS, self._flush)
                self._debounce_timer.start()

    def stop(self):
        if self._debounce_timer:
            self._debounce_timer.cancel()
        if self._observer:
            self._observer.stop()
            self._observer.join()


class Handler(BaseHTTPRequestHandler):
    broker = event_broker
    config = CONFIG

    def log_message(self, fmt, *args):
        pass

    def _write_body(self, body):
        try:
            self.wfile.write(body)
            self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            self.close_connection = True

    def _send_json(self, data, status=200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self._write_body(body)

    def _send_text(self, text, content_type="text/plain", status=200):
        body = text.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self._write_body(body)

    def _serve_static(self, path, content_type=None):
        full = self.config.ui_dir / path
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
        self._write_body(body)

    def do_GET(self):
        parsed = self.path.split("?", 1)
        path = parsed[0]
        query = parsed[1] if len(parsed) > 1 else ""

        if path == "/api/tree":
            return self._send_json(tree_json(self.config))
        if path == "/api/context":
            return self._send_json(context_json(self.config))
        if path == "/api/index-tree":
            return self._send_json(index_tree_json(self.config))
        if path == "/api/system-index-tree":
            system_tree = system_index_tree_json(self.config)
            if system_tree is not None:
                return self._send_json(system_tree)
            return self._send_json({"name": "Adaptive Agents", "type": "index", "path": "INDEX.md", "children": []}, status=404)
        if path == "/api/file":
            params = urllib.parse.parse_qs(query)
            file_path = params.get("path", [""])[0]
            full = resolve_requested_file(file_path, self.config)
            if full is None:
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
            self._write_body(body)
            return
        if path == "/events":
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            subscriber = self.broker.subscribe()
            try:
                while True:
                    try:
                        event_type, data = subscriber.get(timeout=30)
                        line = f"event: {event_type}\ndata: {json.dumps(data)}\n\n"
                        self.wfile.write(line.encode("utf-8"))
                        self.wfile.flush()
                    except queue.Empty:
                        self.wfile.write(": keepalive\n\n".encode("utf-8"))
                        self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
                pass
            finally:
                self.broker.unsubscribe(subscriber)
                self.close_connection = True
            return
        if path == "/" or path == "":
            return self._serve_static("index.html", "text/html")
        if path == "/app.js":
            return self._serve_static("app.js", "application/javascript")

        full = (self.config.target_root / path.lstrip("/")).resolve()
        try:
            full.relative_to(self.config.target_root.resolve())
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
            self._write_body(body)
            return
        if path.startswith("/view"):
            params = urllib.parse.parse_qs(query)
            file_path = params.get("path", [""])[0]
            if file_path:
                return self._serve_static("index.html", "text/html")
            return self._send_text("Missing path parameter", status=400)
        self._send_text("Not Found", status=404)

    def do_HEAD(self):
        self.do_GET()


def make_handler(config, broker=event_broker):
    class ConfiguredHandler(Handler):
        pass

    ConfiguredHandler.config = config
    ConfiguredHandler.broker = broker
    return ConfiguredHandler


def cmd_serve(config=None, open_browser=True):
    active_config = config or CONFIG
    set_config(active_config)
    if not (active_config.ui_dir / "index.html").exists() or not (active_config.ui_dir / "app.js").exists():
        print("UI files missing - generating...")
        cmd_generate(active_config)

    watcher = WatchdogWatcher(active_config)
    watcher.start()
    server = ThreadingHTTPServer(("0.0.0.0", active_config.port), make_handler(active_config))
    url = f"http://localhost:{active_config.port}"

    print("Adaptive Agents Markdown Browser")
    print(f"System home:  {active_config.system_home}")
    print(f"Target root:  {active_config.target_root}")
    print(f"Project layer:{active_config.project_layer_root}")
    print(f"Open:         {url}")
    print("Press Ctrl+C to stop.")

    if open_browser:
        webbrowser.open(url)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        server.shutdown()
        watcher.stop()


def parse_args(argv):
    parser = argparse.ArgumentParser(description="Adaptive Agents Markdown Browser")
    parser.add_argument("command", choices=("generate", "serve"))
    parser.add_argument("--target", default=None, help="Project root to browse; defaults to the current working directory.")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="HTTP port for serve; defaults to 8099.")
    parser.add_argument("--no-open", action="store_true", help="Do not open a browser window when serving.")
    return parser.parse_args(argv)


def main(argv=None):
    if sys.version_info < (3, 9):
        print("Error: Python 3.9+ is required.", file=sys.stderr)
        return 1

    args = parse_args(sys.argv[1:] if argv is None else argv)
    config = BrowserConfig.create(target_root=args.target, port=args.port)
    set_config(config)
    if args.command == "generate":
        cmd_generate(config)
    elif args.command == "serve":
        cmd_serve(config, open_browser=not args.no_open)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())