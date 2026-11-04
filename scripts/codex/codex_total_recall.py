#!/usr/bin/env python3
"""Ledger-first Codex capture and bounded, model-owned semantic recall."""

from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import tempfile
from typing import Any, Generator
from urllib.parse import unquote, urlparse
import uuid




APP_NAME = "adaptive-agents-codex-total-recall"
INDEX_TEMPLATE_VERSION = 14
MAX_READ_BYTES = 4096
MAX_ADDITIONAL_CONTEXT_BYTES = 1200
COMPACTION_EVENTS = {"PreCompact", "PostCompact"}
MARKDOWN_LINK = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)]+)\)")
SEMANTIC_START = "<!-- semantic-breadcrumbs:start -->"
SEMANTIC_END = "<!-- semantic-breadcrumbs:end -->"




def now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def atomic_write(path: Path, content: str) -> None:
    try:
        if path.read_bytes() == content.encode("utf-8"):
            return
    except FileNotFoundError:
        pass
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


@contextlib.contextmanager
def file_lock(path: Path) -> Generator[None, None, None]:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+b") as stream:
        stream.seek(0, os.SEEK_END)
        if not stream.tell():
            stream.write(b"0")
            stream.flush()
        stream.seek(0)
        if os.name == "nt":
            import msvcrt
            msvcrt.locking(stream.fileno(), msvcrt.LK_LOCK, 1)
        else:
            import fcntl
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            if os.name == "nt":
                stream.seek(0)
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def authority_root() -> Path:
    configured = os.environ.get("ADAPTIVE_AGENTS_ROOT")
    return Path(configured).resolve() if configured else Path(__file__).resolve().parents[2]


def event_kind(data: dict[str, Any]) -> str:
    return str(data.get("hook_event_name") or "Unknown")


def event_fingerprint(data: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json(data).encode("utf-8")).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid {path.name}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{path.name} must contain an object")
    return value


def check_events(events: list[Any]) -> None:
    ids: set[str] = set()
    fingerprints: set[tuple[str, str]] = set()
    for line, event in enumerate(events, 1):
        if not isinstance(event, dict):
            raise ValueError(f"ledger line {line} is not an object")
        if event.get("sequence") != line or event.get("ledger_line", line) != line:
            raise ValueError(f"ledger line {line} has an inconsistent source location")
        event_id = event.get("event_id")
        fingerprint = event.get("fingerprint")
        if not isinstance(event_id, str) or not event_id or event_id in ids:
            raise ValueError(f"ledger line {line} has a missing or duplicate event_id")
        diagnostics = event.get("adapter_diagnostics", {})
        if not isinstance(diagnostics, dict):
            raise ValueError(f"ledger line {line} has invalid adapter diagnostics")
        if not isinstance(fingerprint, str):
            raise ValueError(f"ledger line {line} has a missing fingerprint")
        capture_key = fingerprint, canonical_json(diagnostics)
        if capture_key in fingerprints:
            raise ValueError(f"ledger line {line} has a missing or duplicate fingerprint")
        payload = event.get("payload")
        if not isinstance(payload, dict):
            raise ValueError(f"ledger line {line} lacks a complete payload; preserve legacy records for explicit recovery")
        if event_fingerprint(payload) != fingerprint:
            raise ValueError(f"ledger line {line} payload does not match its fingerprint")
        ids.add(event_id)
        fingerprints.add(capture_key)


def semantic_section(text: str) -> str:
    if text.count(SEMANTIC_START) != 1 or text.count(SEMANTIC_END) != 1:
        raise ValueError("INDEX.md lacks one bounded semantic region; preserve it for explicit repair")
    before, rest = text.split(SEMANTIC_START, 1)
    if SEMANTIC_END in before:
        raise ValueError("INDEX.md semantic markers are out of order")
    return rest.split(SEMANTIC_END, 1)[0].strip()


def reader_command(session_dir: Path, *, mode: str = "read") -> str:
    interpreter = os.environ.get("ADAPTIVE_TOTAL_RECALL_READER_PYTHON", sys.executable)
    launcher = os.environ.get("ADAPTIVE_TOTAL_RECALL_READER_LAUNCHER")
    reader = Path(launcher) if launcher else Path(__file__).resolve()
    args = [interpreter, str(reader), "--" + mode, str(session_dir.resolve())]
    if os.name == "nt":
        return "& " + " ".join("'" + arg.replace("'", "''") + "'" for arg in args)
    return shlex.join(args)


def _without_fenced_code(text: str) -> str:
    visible: list[str] = []
    fence: str | None = None
    for line in text.splitlines(keepends=True):
        match = re.match(r"^\s*(`{3,}|~{3,})", line)
        if fence is None:
            if match:
                fence = match.group(1)
            else:
                visible.append(line)
        elif match and match.group(1)[0] == fence[0] and len(match.group(1)) >= len(fence):
            fence = None
    return "".join(visible)


def hook_configuration(script_path: Path, python_executable: str | None = None) -> dict[str, Any]:
    interpreter = python_executable or sys.executable
    command = f'"{interpreter}" "{script_path.resolve()}"'
    windows_command = subprocess.list2cmdline([interpreter, str(script_path.resolve())])

    def handler(timeout: int = 10, context: bool = False) -> dict[str, Any]:
        value: dict[str, Any] = {"type": "command", "command": command, "commandWindows": windows_command, "timeout": timeout}
        if context:
            value["additionalContextLimit"] = MAX_ADDITIONAL_CONTEXT_BYTES
        return value

    hooks: dict[str, Any] = {
        "SessionStart": [{"matcher": "startup|resume|clear|compact|fork", "hooks": [handler(60, True)]}],
        "UserPromptSubmit": [{"hooks": [handler(context=True)]}],
        "Stop": [{"hooks": [handler(60)]}],
        "SessionEnd": [{"matcher": "other", "hooks": [handler(3)]}],
    }
    for event in ("PreToolUse", "PostToolUse", "SubagentStart", "SubagentStop"):
        hooks[event] = [{"matcher": ".*", "hooks": [handler(context=event == "PostToolUse")]}]
    for event in COMPACTION_EVENTS:
        hooks[event] = [{"matcher": "manual|auto", "hooks": [handler()]}]
    return {"description": "Adaptive Agents Total Recall session graph hooks", "hooks": hooks}


HEADER = b"# Captured session evidence\n\n<!-- markdown-ledger-experiment: 1 -->\n\n"
FRAME = re.compile(rb"<!-- recall-record bytes=(\d+) sha256=([a-f0-9]{64}) -->\n")
PART_CHARACTERS = 1600
BODY_FIELDS = {"prompt", "tool_response", "tool_output", "last_assistant_message", "assistant_response", "command"}




def text_parts(event: dict[str, Any]) -> list[dict[str, Any]]:
    parts: list[dict[str, Any]] = []
    field = 0

    def visit(value: Any, path: list[str | int]) -> None:
        nonlocal field
        if isinstance(value, dict):
            for key in sorted(value):
                visit(value[key], [*path, key])
        elif isinstance(value, list):
            for index, item in enumerate(value):
                visit(item, [*path, index])
        elif isinstance(value, str) and (
                len(value) > 240 or "\n" in value or "\r" in value or any(p in BODY_FIELDS for p in path)):
            number, offset, part = field, 0, 0
            field += 1
            while offset < len(value) or (not value and part == 0):
                end = min(offset + PART_CHARACTERS, len(value))
                if end < len(value):
                    newline = value.rfind("\n", offset + PART_CHARACTERS // 2, end)
                    if newline >= 0:
                        end = newline + 1
                chunk = value[offset:end]
                parts.append({"anchor": f"{event['event_id']}-f{number}-p{part}", "path": path,
                              "part": part, "text": chunk})
                offset, part = end, part + 1
                if not value:
                    break

    visit(event["payload"], [])
    return parts


def set_path(value: dict[str, Any], path: list[str | int], replacement: Any) -> None:
    target: Any = value
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = replacement


def block_text(text: str) -> tuple[str, str, str]:
    escaped = any(ord(c) < 32 and c not in "\r\n\t" for c in text)
    encoded = json.dumps(text, ensure_ascii=True) if escaped else text
    fence = "`" * max(3, 1 + max((len(s) for s in re.findall(r"`+", encoded)), default=0))
    return encoded, "json-string" if escaped else "text", fence


def part_prefix(part: dict[str, Any]) -> str:
    field = re.sub(r"[^a-zA-Z0-9_.-]", "_", ".".join(map(str, part["path"])))[:80]
    return (f'<a id="{part["anchor"]}"></a>\n'
            f'### {field} - part {part["part"] + 1}\n\n'
            f'{part["fence"]}{"json" if part["encoding"] == "json-string" else "text"}\n')


def render_event(event: dict[str, Any]) -> bytes:
    skeleton = json.loads(json.dumps(event, ensure_ascii=True))
    specs, blocks = [], []
    for part in text_parts(event):
        encoded, encoding, fence = block_text(part["text"])
        spec = {k: v for k, v in part.items() if k != "text"}
        spec.update(characters=len(encoded), encoding=encoding, fence=fence)
        specs.append(spec)
        set_path(skeleton["payload"], part["path"], None)
        blocks.append(part_prefix(spec) + encoded + "\n" + fence + "\n\n")
    metadata = json.dumps({"event": skeleton, "text_parts": specs}, ensure_ascii=True, sort_keys=True, indent=2)
    body = (f'<a id="{event["event_id"]}"></a>\n## Event {event["event_id"]} - {event["kind"]}\n\n'
            "<details><summary>Capture metadata and payload structure</summary>\n\n"
            f"```json\n{metadata}\n```\n\n</details>\n\n" + "".join(blocks)).encode("utf-8")
    return (f"<!-- recall-record bytes={len(body)} sha256={hashlib.sha256(body).hexdigest()} -->\n".encode()
            + body)


def parse_body(body: bytes) -> dict[str, Any]:
    text = body.decode("utf-8")
    start = text.index("```json\n") + len("```json\n")
    metadata, count = json.JSONDecoder().raw_decode(text[start:])
    position = start + count
    tail = "\n```\n\n</details>\n\n"
    if not text.startswith(tail, position):
        raise ValueError("corrupt Markdown metadata boundary")
    position += len(tail)
    event = metadata["event"]
    chunks: dict[tuple[str | int, ...], list[str]] = {}
    for part in metadata["text_parts"]:
        prefix = part_prefix(part)
        if not text.startswith(prefix, position):
            raise ValueError("corrupt Markdown text boundary")
        position += len(prefix)
        size = part["characters"]
        if type(size) is not int or size < 0:
            raise ValueError("corrupt Markdown text length")
        encoded = text[position:position + size]
        position += size
        suffix = "\n" + part["fence"] + "\n\n"
        if not text.startswith(suffix, position):
            raise ValueError("incomplete Markdown text part")
        position += len(suffix)
        value = json.loads(encoded) if part["encoding"] == "json-string" else encoded
        if not isinstance(value, str):
            raise ValueError("corrupt Markdown text value")
        chunks.setdefault(tuple(part["path"]), []).append(value)
    for path, pieces in chunks.items():
        set_path(event["payload"], list(path), "".join(pieces))
    if position != len(text) or render_event(event).split(b"\n", 1)[1] != body:
        raise ValueError("corrupt or noncanonical Markdown record")
    return event


def read_events(session: Path) -> list[dict[str, Any]]:
    if any((session / name).exists() for name in ("ledger.jsonl", "ledger.json")):
        raise ValueError("JSON/JSONL recall sessions are deprecated; start a fresh Codex session. Existing files are unchanged.")
    path = session / "ledger.md"
    if not path.exists():
        return []
    data = path.read_bytes()
    if not data.startswith(HEADER):
        raise ValueError("corrupt Markdown ledger header")
    position, events = len(HEADER), []
    while position < len(data):
        frame = FRAME.match(data, position)
        if frame is None:
            raise ValueError(f"incomplete/corrupt Markdown record at byte {position}; preserve for recovery")
        end = frame.end() + int(frame[1])
        if end > len(data):
            raise ValueError(f"incomplete Markdown append at byte {position}; preserve for recovery")
        body = data[frame.end():end]
        if hashlib.sha256(body).hexdigest().encode() != frame[2]:
            raise ValueError(f"Markdown checksum mismatch at byte {position}")
        try:
            events.append(parse_body(body))
        except (KeyError, IndexError, TypeError, UnicodeError) as exc:
            raise ValueError(f"corrupt Markdown record at byte {position}: {exc}") from exc
        position = end
    check_events(events)
    return events


class SessionStore:
    def __init__(self, root: Path | None = None, *, provider: str = "codex") -> None:
        self.provider = provider
        self.root = (root or Path.home() / ".adaptive-agents" / "sessions" / provider).resolve()
        self.map_path = self.root / "session-map.json"

    def session_for(self, provider_session_id: str, data: dict[str, Any]) -> Path:
        if not provider_session_id:
            raise ValueError("Codex hook payload is missing session_id")
        with file_lock(self.root / ".session-map.lock"):
            mapping = read_json(self.map_path) if self.map_path.exists() else {"version": 1, "sessions": {}}
            sessions = mapping.get("sessions")
            if not isinstance(sessions, dict):
                raise ValueError("session-map.json sessions must be an object")
            record = sessions.get(provider_session_id)
            if record is None:
                record = {"adaptive_session_id": str(uuid.uuid4()), "provider_session_id": provider_session_id,
                          "provider": self.provider, "created_at": now_utc()}
                sessions[provider_session_id] = record
                atomic_write(self.map_path, json.dumps(mapping, indent=2) + "\n")
            if not isinstance(record, dict) or not isinstance(record.get("adaptive_session_id"), str):
                raise ValueError("invalid session identity mapping")
            session = (self.root / record["adaptive_session_id"]).resolve()
            if session.parent != self.root:
                raise ValueError("session identity escapes the session namespace")
            if any((session / name).exists() for name in ("ledger.jsonl", "ledger.json")):
                raise ValueError("JSON/JSONL recall sessions are deprecated; start a fresh Codex session. Existing files are unchanged.")
            session.mkdir(parents=True, exist_ok=True)
            manifest = session / "manifest.json"
            if manifest.exists():
                saved = read_json(manifest)
                if saved.get("provider_session_id") != provider_session_id:
                    raise ValueError("session manifest identity mismatch")
                if saved.get("ledger_path") != "ledger.md":
                    raise ValueError("Deprecated recall session format; start a fresh Codex session. Existing files are unchanged.")
            else:
                atomic_write(manifest, json.dumps({**record, "version": 4, "cwd": data.get("cwd"),
                                                  "ledger_path": "ledger.md",
                                                  "format": "markdown-1"}, indent=2) + "\n")
        return session

    def capture(self, data: dict[str, Any]) -> tuple[Path, str, bool]:
        session = self.session_for(str(data.get("session_id") or ""), data)
        with file_lock(session / ".graph.lock"):
            events = read_events(session)
            if not (session / "INDEX.md").exists():
                self.initialize_index(session)
            fingerprint = event_fingerprint(data)
            for event in events:
                if event["fingerprint"] == fingerprint:
                    return session, event["event_id"], False
            sequence = len(events) + 1
            event = {"event_id": f"evt-{sequence:06d}-{fingerprint[:12]}",
                     "sequence": sequence, "kind": event_kind(data), "captured_at": now_utc(),
                     "fingerprint": fingerprint, "payload": data}
            record = render_event(event)
            with (session / "ledger.md").open("ab") as stream:
                if stream.tell() == 0:
                    stream.write(HEADER)
                stream.write(record)
                stream.flush()
                os.fsync(stream.fileno())
            return session, event["event_id"], True

    @staticmethod
    def initialize_index(session: Path) -> None:
        template = authority_root() / "templates" / "total-recall" / "markdown-session-index.md"
        text = template.read_text(encoding="utf-8")
        replacements = {
            "{{ADAPTIVE_AGENTS_AUTHORITY}}": (authority_root() / "AGENTS.md").as_uri(),
            "{{READER}}": reader_command(session),
            "{{SEARCH}}": reader_command(session, mode="search"),
            "{{RECENT}}": reader_command(session, mode="recent"),
        }
        for token, value in replacements.items():
            text = text.replace(token, value)
        if re.search(r"\{\{[A-Z_]+\}\}", text):
            raise ValueError("unresolved Markdown session template placeholders")
        semantic_section(text)
        atomic_write(session / "INDEX.md", text)

def read_source(session: Path, anchor: str, offset: int = 0) -> dict[str, Any]:
    text, next_part = None, None
    for event in read_events(session):
        if event["event_id"] == anchor:
            text = canonical_json(event["payload"])
            break
        parts = text_parts(event)
        selected = next((p for p in parts if p["anchor"] == anchor), None)
        if selected is not None:
            text = selected["text"]
            next_part = next((p["anchor"] for p in parts if p["path"] == selected["path"]
                              and p["part"] == selected["part"] + 1), None)
            break
    if text is None:
        raise ValueError("unknown source anchor")
    if type(offset) is not int or offset < 0 or offset > len(text) or (text and offset == len(text)):
        raise ValueError("invalid source offset")
    result: dict[str, Any] = {"source": f"ledger.md#{anchor}", "offset": offset,
                              "next_offset": None, "next_part": next_part, "text": ""}
    low, high = 1, min(len(text) - offset, 4096)
    while low <= high:
        size = (low + high) // 2
        candidate = {**result, "text": text[offset:offset + size],
                     "next_offset": offset + size if offset + size < len(text) else None}
        if len(json.dumps(candidate, ensure_ascii=True).encode()) <= 4096:
            result, low = candidate, size + 1
        else:
            high = size - 1
    return result


def search(session: Path, query: str, start_event: int = 1) -> dict[str, Any]:
    if not isinstance(query, str) or not query.strip() or len(query) > 256:
        raise ValueError("query must contain 1-256 characters")
    events = read_events(session)
    if type(start_event) is not int or not 1 <= start_event <= len(events) + 1:
        raise ValueError("invalid search event cursor")
    pattern = re.compile(re.escape(query), re.I)
    result: dict[str, Any] = {"matches": [], "next_event": None}
    for event in events[start_event - 1:start_event + 255]:
        result["next_event"] = event["sequence"] + 1 if event["sequence"] < len(events) else None
        fields: dict[tuple[str | int, ...], list[dict[str, Any]]] = {}
        for part in text_parts(event):
            fields.setdefault(tuple(part["path"]), []).append(part)
        found = None
        for parts in fields.values():
            match = pattern.search("".join(p["text"] for p in parts))
            if match:
                position = match.start()
                for part in parts:
                    if position < len(part["text"]):
                        found = (part["anchor"], part["text"], position)
                        break
                    position -= len(part["text"])
                break
        whole = canonical_json(event["payload"])
        if found is None:
            match = pattern.search(whole)
            if not match:
                continue
            found = (event["event_id"], whole, match.start())
        anchor, text, position = found
        offset = max(0, position - 50)
        item = {"anchor": anchor, "offset": offset, "excerpt": text[offset:offset + 180]}
        candidate = {**result, "matches": result["matches"] + [item]}
        if len(json.dumps(candidate, ensure_ascii=True).encode()) > 4096:
            result["next_event"] = event["sequence"]
            break
        result = candidate
    return result


def recent(session: Path) -> dict[str, Any]:
    events = read_events(session)
    result: dict[str, Any] = {"events": [], "omitted_older": max(0, len(events) - 6)}
    for event in reversed(events[-6:]):
        item = {"event_id": event["event_id"], "kind": event["kind"],
                "parts": [{"anchor": p["anchor"], "field": p["path"], "preview": p["text"][:70]}
                          for p in text_parts(event)[:4]]}
        candidate = {**result, "events": result["events"] + [item]}
        if len(json.dumps(candidate, ensure_ascii=True).encode()) > 4096:
            result["omitted_older"] += min(6, len(events)) - len(result["events"])
            break
        result = candidate
    return result


def validate(session: Path) -> list[str]:
    read_events(session)
    pending, visited, errors = [session / "INDEX.md"], set(), []
    while pending:
        path = pending.pop().resolve()
        if path in visited:
            continue
        visited.add(path)
        text = path.read_text(encoding="utf-8")
        for _, target in MARKDOWN_LINK.findall(_without_fenced_code(text)):
            if re.match(r"[a-z]+:", target):
                continue
            name, _, anchor = target.partition("#")
            resolved = (path.parent / name).resolve() if name else path
            if session.resolve() not in resolved.parents or not resolved.is_file():
                errors.append(f"invalid source path: {target}")
                continue
            if anchor:
                body = resolved.read_bytes().decode("utf-8")
                headings = [re.sub(r"[^\w -]", "", h).lower().replace(" ", "-")
                            for h in re.findall(r"(?m)^#+ (.+)$", _without_fenced_code(body))]
                anchors = re.findall(r'<a id="([^"]+)"></a>', _without_fenced_code(body))
                if anchor not in anchors + headings:
                    errors.append(f"unknown source anchor: {target}")
            if resolved.name != "ledger.md" and resolved.suffix == ".md":
                pending.append(resolved)
    return errors


def handle_hook(data: dict[str, Any], store: SessionStore | None = None,
                proactive: bool = True) -> dict[str, Any] | None:
    store = store or SessionStore()
    session, event, _ = store.capture(data)
    kind = event_kind(data)
    if kind == "PostToolUse":
        parts = [p for p in text_parts({"event_id": event, "payload": data})
                 if any(key in {"tool_response", "tool_output"} for key in p["path"])]
        context = (f"Captured tool-result evidence: ledger.md#{event}. "
                   "These targets are relative to INDEX.md in the current recall session; "
                   "do not add ../ when linking from that root. "
                   "Cite the result containing the fact, not the user request that caused the tool call. ")
        if parts:
            context += "Result text parts: " + ", ".join(
                f"ledger.md#{p['anchor']}" for p in parts[:4]) + ". "
            if len(parts) > 4:
                context += "There are more parts; use the bounded reader's next_part to continue. "
        context += "No topic update is required for routine activity."
        if len(context.encode()) > MAX_ADDITIONAL_CONTEXT_BYTES:
            raise ValueError("experiment source context exceeds its configured limit")
        return {"hookSpecificOutput": {"hookEventName": kind, "additionalContext": context}}
    if kind not in {"SessionStart", "UserPromptSubmit"}:
        return None
    context = (f"Recall root: {(session / 'INDEX.md').as_posix()}. Current captured source: ledger.md#{event}. "
               "INDEX.md and topical subindexes are writable navigation, not immutable source evidence. "
               "On first encountering this root, read its discovery/navigation contract once. "
               "Use source anchors and bounded reads/search when history is needed. "
               "Continue the user's task; never audit all-event coverage or rebuild after compaction. ")
    if proactive:
        context += ("During normal work, when a meaningful subject, decision or constraint emerges or changes, "
                    "make a small useful topic update while its evidence is available. Reuse existing subjects "
                    "and connect relevant sources, explaining revisions without deleting earlier evidence. "
                    "Only link captured sources; defer future final-reply links until a natural later turn. "
                    "Do not index routine activity or turn this into a separate maintenance conversation.")
    else:
        context += ("Keep selective topical routes when useful; when historical details are needed, consult "
                    "existing topics, then source search if no route fits. No mandatory per-turn maintenance.")
    if len(context.encode()) > MAX_ADDITIONAL_CONTEXT_BYTES:
        raise ValueError("experiment recovery context exceeds its configured limit")
    return {"hookSpecificOutput": {"hookEventName": kind, "additionalContext": context}}


def main(*, require_explicit_root: bool = False) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    for mode in ("read", "recent", "search", "validate"):
        modes.add_argument("--" + mode, type=Path)
    modes.add_argument("--hooks-json", action="store_true")
    parser.add_argument("--root", type=Path)
    parser.add_argument("--anchor")
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--query")
    parser.add_argument("--start-event", type=int, default=1)
    guidance = parser.add_mutually_exclusive_group()
    guidance.add_argument("--proactive", dest="proactive", action="store_true", default=True)
    guidance.add_argument("--selective", dest="proactive", action="store_false")
    args = parser.parse_args()
    try:
        if args.hooks_json:
            output = hook_configuration(Path(__file__))
        elif args.read:
            output = read_source(args.read, args.anchor, args.offset)
        elif args.recent:
            output = recent(args.recent)
        elif args.search:
            output = search(args.search, args.query, args.start_event)
        elif args.validate:
            errors = validate(args.validate)
            if errors:
                raise ValueError("; ".join(errors))
            output = {"valid": True, "semantic_quality_certified": False}
        else:
            if require_explicit_root and args.root is None:
                raise ValueError("isolated experiment requires an explicit --root; live store is not a default")
            data = json.loads(sys.stdin.buffer.read().decode("utf-8"))
            if not isinstance(data, dict):
                raise ValueError("hook payload must be an object")
            output = handle_hook(data, SessionStore(args.root), args.proactive)
        if output is not None:
            print(json.dumps(output, ensure_ascii=True))
        return 0
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"Codex Total Recall: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
