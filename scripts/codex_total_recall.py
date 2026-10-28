#!/usr/bin/env python3
"""Codex hook adapter for the Adaptive Agents Total Recall foundation.

The adapter deliberately keeps the provider session transcript out of its
persistence contract. Codex hook payloads are captured as inspectable Markdown
records, while the append-only JSONL ledger is authoritative and the JSON
compatibility mirror plus validator provide deterministic graph accounting and
reachability checks.
"""

from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import hashlib
import json
import os
import re
import sys
import tempfile
import uuid
from urllib.parse import unquote, urlparse
from pathlib import Path
from typing import Any, Iterator


APP_NAME = "adaptive-agents-codex-total-recall"
INDEX_TEMPLATE_VERSION = 2
GRAPH_SIZE_GUIDANCE = {
    "root_bytes": 12000,
    "index_bytes": 16000,
    "entries": 64,
}
MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")
ANCHOR_MARKER = re.compile(r"<!--\s*anchor:\s*([^\s]+)\s*-->")
EVENT_MARKER = re.compile(r"<!--\s*event-id:\s*([^\s]+)\s*-->")

SEMANTIC_BREADCRUMB_CONTRACT = """When maintaining this session graph, use descriptive Markdown link text that tells the model what the target contains and why it matters. Do not use opaque event IDs or generic labels such as `event`, `details`, or `record` as the only navigation text. For important instructions, decisions, requirements, unresolved questions, preferences, milestones, evidence, and artifacts, create a concise semantic breadcrumb.

Each breadcrumb may either link directly to `ledger.jsonl` and state the exact inclusive line range to read, or delegate to a narrower semantic index whose link text explains the topic boundary and why to follow it. Example direct locator: `Decision: preserve JSONL history — read ledger.jsonl lines 121–155 for the decision, surrounding discussion, and resulting evidence.` A sub-index may mix these direct locators with further purposeful delegation. Preserve exact source-event links when useful; `event-type` and chronological indexes are fallback accounting/navigation, not semantic navigation.

Semantic organization is model-supplied, but every breadcrumb must resolve to retained source detail. Deterministic validation is authoritative for link resolution, JSONL line-range validity, source identifiers, reachability, and non-orphaning; it cannot certify that a label is semantically meaningful.
"""


def now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def atomic_write(path: Path, content: str) -> None:
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


def adaptive_agents_authority_path() -> Path | None:
    """Return the canonical Adaptive Agents AGENTS.md when installed locally."""

    configured_root = os.environ.get("ADAPTIVE_AGENTS_ROOT")
    candidates = (
        ((Path(configured_root) / "AGENTS.md",) if configured_root else ())
        + (
        Path(__file__).resolve().parent.parent / "AGENTS.md",
        Path.home() / ".adaptive-agents" / "AGENTS.md",
        )
    )
    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()
    return None


def markdown_file_uri(path: Path) -> str:
    return path.resolve().as_uri()


def session_index_template_path() -> Path:
    """Locate the maintained seed template without embedding it in the adapter."""

    configured_root = os.environ.get("ADAPTIVE_AGENTS_ROOT")
    candidates = (
        ((Path(configured_root) / "templates" / "total-recall" / "session-index.md",) if configured_root else ())
        + (Path(__file__).resolve().parent.parent / "templates" / "total-recall" / "session-index.md",)
    )
    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()
    raise FileNotFoundError("missing maintained Total Recall session-index template")


@contextlib.contextmanager
def file_lock(path: Path) -> Iterator[None]:
    """Serialize updates on both native Windows and POSIX hosts."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+b") as stream:
        stream.seek(0, os.SEEK_END)
        if stream.tell() == 0:
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
                import msvcrt

                stream.seek(0)
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl

                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def safe_slug(value: str, fallback: str = "event") -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug[:48] or fallback


def event_kind(data: dict[str, Any]) -> str:
    return str(data.get("hook_event_name") or "Unknown").strip() or "Unknown"


def event_fingerprint(data: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json(data).encode("utf-8")).hexdigest()


class SessionStore:
    """User-scoped Codex session storage and deterministic graph writer."""

    def __init__(self, root: Path | None = None) -> None:
        self.root = (root or (Path.home() / ".adaptive-agents" / "sessions" / "codex")).resolve()
        self.map_path = self.root / "session-map.json"
        self.map_lock = self.root / ".session-map.lock"

    def session_for(self, provider_session_id: str, data: dict[str, Any]) -> Path:
        if not provider_session_id:
            raise ValueError("Codex hook payload is missing session_id")
        self.root.mkdir(parents=True, exist_ok=True)
        with file_lock(self.map_lock):
            mapping = self._read_json(self.map_path, {"version": 1, "sessions": {}}, strict=True)
            sessions = mapping.setdefault("sessions", {})
            if not isinstance(sessions, dict):
                raise ValueError("session-map.json sessions must be an object")
            record = sessions.get(provider_session_id)
            if not isinstance(record, dict) or not record.get("adaptive_session_id"):
                adaptive_id = str(uuid.uuid4())
                record = {
                    "adaptive_session_id": adaptive_id,
                    "provider": "codex",
                    "provider_session_id": provider_session_id,
                    "created_at": now_utc(),
                }
                sessions[provider_session_id] = record
                atomic_write(self.map_path, json.dumps(mapping, indent=2, ensure_ascii=False) + "\n")
            session_dir = self.root / record["adaptive_session_id"]
        self._ensure_session(session_dir, record, data)
        return session_dir

    def capture(self, data: dict[str, Any]) -> tuple[Path, str, bool]:
        session_dir = self.session_for(str(data.get("session_id") or ""), data)
        lock_path = session_dir / ".graph.lock"
        with file_lock(lock_path):
            ledger = self._read_authoritative_ledger(session_dir)
            ledger_path = session_dir / "ledger.json"
            fingerprint = event_fingerprint(data)
            for existing in ledger.get("events", []):
                if existing.get("fingerprint") == fingerprint:
                    atomic_write(ledger_path, json.dumps(ledger, indent=2, ensure_ascii=False) + "\n")
                    self._write_indexes(session_dir, ledger)
                    return session_dir, str(existing["event_id"]), False

            sequence = len(ledger.get("events", [])) + 1
            event_id = f"evt-{sequence:06d}-{fingerprint[:12]}"
            kind = event_kind(data)
            filename = f"{sequence:06d}-{safe_slug(kind)}-{fingerprint[:10]}.md"
            relative_record = Path("events") / filename
            record_path = session_dir / relative_record
            markdown = self._event_markdown(event_id, sequence, data)
            atomic_write(record_path, markdown)
            ledger.setdefault("events", []).append(
                {
                    "event_id": event_id,
                    "sequence": sequence,
                    "kind": kind,
                    "fingerprint": fingerprint,
                    "path": relative_record.as_posix(),
                    "anchor": event_id,
                    "captured_at": now_utc(),
                    "ledger_line": sequence,
                    # JSONL is the authoritative complete record. Keep the
                    # original hook payload on the same line as its stable
                    # graph metadata so derived views never become the only
                    # place where captured detail survives.
                    "payload": data,
                }
            )
            atomic_write(ledger_path, json.dumps(ledger, indent=2, ensure_ascii=False) + "\n")
            self._sync_jsonl_ledger(session_dir / "ledger.jsonl", ledger.get("events", []))
            self._write_indexes(session_dir, ledger)
            return session_dir, event_id, True

    def validate(self, session_dir: Path) -> list[str]:
        return validate_session(session_dir)

    def _ensure_session(self, session_dir: Path, record: dict[str, Any], data: dict[str, Any]) -> None:
        session_dir.mkdir(parents=True, exist_ok=True)
        manifest_path = session_dir / "manifest.json"
        manifest = self._read_json(manifest_path, {}, strict=True)
        manifest.update(
            {
                "version": 2,
                "provider": "codex",
                "provider_session_id": record["provider_session_id"],
                "adaptive_session_id": record["adaptive_session_id"],
                "cwd": data.get("cwd"),
                "last_seen_at": now_utc(),
                "provider_compaction_state": "not-exposed-by-command-hook",
                "index_template_version": INDEX_TEMPLATE_VERSION,
                "ledger_path": "ledger.jsonl",
            }
        )
        manifest.setdefault("created_at", record.get("created_at", now_utc()))
        atomic_write(manifest_path, json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")

    @staticmethod
    def _read_json(path: Path, default: dict[str, Any], *, strict: bool = False) -> dict[str, Any]:
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(value, dict):
                return value
            if strict:
                raise ValueError(f"{path.name} must contain a JSON object")
            return default
        except FileNotFoundError:
            return default
        except json.JSONDecodeError as exc:
            if strict:
                raise ValueError(f"{path.name} is malformed JSON: {exc}") from exc
            return default

    @classmethod
    def _read_authoritative_ledger(cls, session_dir: Path) -> dict[str, Any]:
        """Read JSONL first, migrating legacy JSON ledgers when necessary."""

        jsonl_path = session_dir / "ledger.jsonl"
        if jsonl_path.is_file():
            try:
                events = [json.loads(line) for line in jsonl_path.read_text(encoding="utf-8").splitlines() if line.strip()]
            except (OSError, json.JSONDecodeError) as exc:
                raise ValueError(f"ledger.jsonl is malformed JSONL: {exc}") from exc
            if not all(isinstance(event, dict) for event in events):
                raise ValueError("ledger.jsonl contains a non-object record")
            return {"version": 2, "events": events}

        legacy = cls._read_json(session_dir / "ledger.json", {"version": 1, "events": []}, strict=True)
        if not isinstance(legacy.get("events"), list):
            raise ValueError("ledger.json events must be an array")
        cls._sync_jsonl_ledger(jsonl_path, legacy["events"])
        return {"version": 2, "events": legacy["events"]}

    @staticmethod
    def _sync_jsonl_ledger(path: Path, events: list[dict[str, Any]]) -> None:
        """Append missing ledger records while preserving the existing prefix."""

        existing: list[dict[str, Any]] = []
        if path.is_file():
            try:
                for line in path.read_text(encoding="utf-8").splitlines():
                    if line.strip():
                        value = json.loads(line)
                        if not isinstance(value, dict):
                            raise ValueError(f"{path.name} contains a non-object record")
                        existing.append(value)
            except (OSError, json.JSONDecodeError, ValueError) as exc:
                raise ValueError(f"{path.name} is malformed JSONL: {exc}") from exc
        if len(existing) > len(events) or any(
            existing[index].get("event_id") != events[index].get("event_id")
            for index in range(len(existing))
        ):
            raise ValueError(f"{path.name} does not preserve the ledger prefix")
        missing = events[len(existing) :]
        if not missing:
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8", newline="\n") as stream:
            for event in missing:
                stream.write(json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n")
            stream.flush()
            os.fsync(stream.fileno())

    @staticmethod
    def _event_markdown(event_id: str, sequence: int, data: dict[str, Any]) -> str:
        payload = json.dumps(data, indent=2, ensure_ascii=False)
        kind = event_kind(data)
        return (
            f"# Event {event_id}\n\n"
            f"<!-- event-id: {event_id} -->\n"
            f"<!-- anchor: {event_id} -->\n\n"
            f"- Sequence: `{sequence}`\n"
            f"- Type: `{kind}`\n"
            f"- Captured: `{now_utc()}`\n\n"
            "## Raw Hook Payload\n\n"
            f"~~~~json\n{payload}\n~~~~\n"
        )

    @staticmethod
    def _write_indexes(session_dir: Path, ledger: dict[str, Any]) -> None:
        events = list(ledger.get("events", []))
        type_groups: dict[str, list[dict[str, Any]]] = {}
        for event in events:
            type_groups.setdefault(safe_slug(str(event.get("kind", "unknown"))), []).append(event)

        existing_root = session_dir / "INDEX.md"
        semantic_section = _preserved_semantic_section(existing_root)
        if semantic_section is None:
            semantic_section = (
                "## Semantic Breadcrumbs\n\n"
                f"{SEMANTIC_BREADCRUMB_CONTRACT}\n\n"
                "No model-authored semantic breadcrumbs have been accepted by the deterministic adapter yet. "
                "Add meaningful breadcrumbs directly to this section during the pre-compaction maintenance pass."
            )

        template = session_index_template_path().read_text(encoding="utf-8")
        authority = markdown_file_uri(adaptive_agents_authority_path()) if adaptive_agents_authority_path() else "AGENTS.md"
        fallback_navigation = "\n".join(
            (
                "- [Complete event ledger](indexes/events.md)",
                "- [Context packets](indexes/context-packets.md)",
                "- [Recent events](indexes/recent.md)",
                "- [Events by type](indexes/by-type/index.md)",
                "- [Session manifest](manifest.json)",
            )
        )
        rendered = (
            template.replace("{{ADAPTIVE_AGENTS_AUTHORITY}}", authority)
            .replace("{{SEMANTIC_SECTION}}", semantic_section)
            .replace("{{FALLBACK_NAVIGATION}}", fallback_navigation)
        )
        if "{{" in rendered or "}}" in rendered:
            raise ValueError("session-index template contains unresolved placeholders")
        atomic_write(session_dir / "INDEX.md", rendered.rstrip() + "\n")

        event_lines = ["# Complete Event Ledger", "", "Every captured event is listed below.", ""]
        for event in events:
            event_lines.append(
                f"- [{event['event_id']} — read ledger.jsonl line {event.get('ledger_line', event.get('sequence'))}]({Path('..', event['path']).as_posix()}#{event['anchor']}) — `{event['kind']}`"
            )
        atomic_write(session_dir / "indexes" / "events.md", "\n".join(event_lines) + "\n")

        recent_lines = ["# Recent Events", "", "The latest captured events are listed below.", ""]
        for event in events[-20:]:
            recent_lines.append(
                f"- [{event['event_id']} — read ledger.jsonl line {event.get('ledger_line', event.get('sequence'))}]({Path('..', event['path']).as_posix()}#{event['anchor']}) — `{event['kind']}`"
            )
        atomic_write(session_dir / "indexes" / "recent.md", "\n".join(recent_lines) + "\n")

        type_index = ["# Events by Type", "", "Each type index links to detailed event records.", ""]
        for kind in sorted(type_groups):
            type_index.append(f"- [{kind}]({kind}.md)")
            type_lines = [f"# Events: {kind}", "", ""]
            for event in type_groups[kind]:
                type_lines.append(
                    f"- [{event['event_id']} — read ledger.jsonl line {event.get('ledger_line', event.get('sequence'))}]({Path('..', '..', event['path']).as_posix()}#{event['anchor']})"
                )
            atomic_write(session_dir / "indexes" / "by-type" / f"{kind}.md", "\n".join(type_lines) + "\n")
        atomic_write(session_dir / "indexes" / "by-type" / "index.md", "\n".join(type_index) + "\n")
        SessionStore._write_context_packets(session_dir, events)
        SessionStore._update_graph_metrics(session_dir)

    @staticmethod
    def _write_context_packets(session_dir: Path, events: list[dict[str, Any]]) -> None:
        packet_index = [
            "# Context Packets",
            "",
            "Each packet provides a bounded first-hop view with links to authoritative source events.",
            "",
        ]
        for index, event in enumerate(events):
            packet_name = f"packet-{int(event.get('sequence', index + 1)):06d}.md"
            neighbors = events[max(0, index - 1) : min(len(events), index + 2)]
            source_ids = " ".join(str(item.get("event_id")) for item in neighbors)
            packet_lines = [
                f"# Context Packet {event.get('event_id')}",
                "",
                f"<!-- source-events: {source_ids} -->",
                "",
                "This bounded context view is derived from the authoritative event ledger. Use the source links for exact payloads.",
                "",
                "## Primary Event",
                "",
                SessionStore._packet_summary(event),
                "",
                "## Source Events",
                "",
            ]
            for neighbor in neighbors:
                relation = "primary" if neighbor is event else "neighbor"
                packet_lines.append(
                    f"- [{relation}: {neighbor['event_id']}](../{neighbor['path']}#{neighbor['anchor']}) — `{neighbor['kind']}`"
                )
            atomic_write(session_dir / "context-packets" / packet_name, "\n".join(packet_lines) + "\n")
            packet_index.append(f"- [Context packet for {event['event_id']}](../context-packets/{packet_name})")
        atomic_write(session_dir / "indexes" / "context-packets.md", "\n".join(packet_index) + "\n")

    @staticmethod
    def _packet_summary(event: dict[str, Any]) -> str:
        details: list[str] = []
        payload = event.get("payload") if isinstance(event.get("payload"), dict) else event
        for key in ("prompt", "last_assistant_message", "tool_name", "tool_input", "tool_output", "trigger", "source"):
            value = payload.get(key)
            if value is None:
                continue
            rendered = json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list)) else str(value)
            details.append(f"- `{key}`: {rendered[:400]}")
        body = "\n".join(details) or f"- Event type: `{event.get('kind', 'unknown')}`"
        # Payload strings are untrusted Markdown. Fence them so arbitrary
        # link-looking text cannot become a graph edge in the derived view.
        return f"~~~~text\n{body}\n~~~~"

    @staticmethod
    def _update_graph_metrics(session_dir: Path) -> None:
        manifest_path = session_dir / "manifest.json"
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return
        indexes = list((session_dir / "indexes").rglob("*.md"))
        root_bytes = (session_dir / "INDEX.md").stat().st_size
        max_index_bytes = max((path.stat().st_size for path in indexes), default=0)
        entry_count = sum(path.read_text(encoding="utf-8").count("\n- ") for path in indexes)
        manifest["graph_budget"] = {
            "mode": "heuristic",
            "root_bytes": root_bytes,
            "max_index_bytes": max_index_bytes,
            "entry_count": entry_count,
            "oversized": (
                root_bytes > GRAPH_SIZE_GUIDANCE["root_bytes"]
                or max_index_bytes > GRAPH_SIZE_GUIDANCE["index_bytes"]
                or entry_count > GRAPH_SIZE_GUIDANCE["entries"]
            ),
            "guidance": GRAPH_SIZE_GUIDANCE,
        }
        atomic_write(manifest_path, json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")


def validate_session(session_dir: Path) -> list[str]:
    errors: list[str] = []
    session_dir = session_dir.resolve()
    root = session_dir / "INDEX.md"
    ledger_path = session_dir / "ledger.json"
    if not root.is_file():
        errors.append("missing session root INDEX.md")
    if not ledger_path.is_file():
        errors.append("missing session ledger.json")
        return errors
    try:
        ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"invalid ledger.json: {exc}"]
    compatibility_events = ledger.get("events") if isinstance(ledger, dict) else None
    if not isinstance(compatibility_events, list):
        return ["ledger.json events must be an array"]

    manifest_path = session_dir / "manifest.json"
    if manifest_path.is_file():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            if manifest.get("version", 1) >= 2 and manifest.get("index_template_version") != INDEX_TEMPLATE_VERSION:
                errors.append("manifest index_template_version is missing or unsupported")
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"invalid manifest.json: {exc}")
    jsonl_path = session_dir / "ledger.jsonl"
    if jsonl_path.is_file():
        try:
            events = [json.loads(line) for line in jsonl_path.read_text(encoding="utf-8").splitlines() if line.strip()]
            if not all(isinstance(event, dict) for event in events):
                errors.append("ledger.jsonl contains a non-object event")
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"invalid ledger.jsonl: {exc}")
            events = compatibility_events
    else:
        events = compatibility_events

    event_ids: set[str] = set()
    fingerprints: set[str] = set()
    for event in events:
        if not isinstance(event, dict):
            errors.append("ledger contains a non-object event")
            continue
        event_id = event.get("event_id")
        if not isinstance(event_id, str) or not event_id:
            errors.append("ledger event is missing event_id")
        elif event_id in event_ids:
            errors.append(f"duplicate event_id: {event_id}")
        else:
            event_ids.add(event_id)
        fingerprint = event.get("fingerprint")
        if isinstance(fingerprint, str) and fingerprint in fingerprints:
            errors.append(f"duplicate event fingerprint: {fingerprint}")
        elif isinstance(fingerprint, str):
            fingerprints.add(fingerprint)
        relative = event.get("path")
        if not isinstance(relative, str):
            errors.append(f"event {event_id!r} is missing path")
            continue
        record = (session_dir / relative).resolve()
        if session_dir not in record.parents or not record.is_file():
            errors.append(f"event {event_id!r} record is missing: {relative}")
        elif not _has_anchor(record, str(event.get("anchor", event_id))):
            errors.append(f"event {event_id!r} anchor is missing: {event.get('anchor', event_id)}")
        ledger_line = event.get("ledger_line")
        if ledger_line is not None and ledger_line != event.get("sequence"):
            errors.append(f"event {event_id!r} ledger_line does not match sequence")

    reachable, link_errors = _reachable_markdown(session_dir, root)
    errors.extend(link_errors)
    for event in events:
        if isinstance(event, dict) and isinstance(event.get("path"), str):
            if (session_dir / event["path"]).resolve() not in reachable:
                errors.append(f"event {event.get('event_id')!r} is not reachable from INDEX.md")
    ledger_paths = {
        (session_dir / event["path"]).resolve()
        for event in events
        if isinstance(event, dict) and isinstance(event.get("path"), str)
    }
    for record in sorted((session_dir / "events").glob("*.md")):
        if record.resolve() not in ledger_paths:
            errors.append(f"event record is not accounted for in ledger.json: {record.name}")
    for packet in sorted((session_dir / "context-packets").glob("*.md")):
        if packet.resolve() not in reachable:
            errors.append(f"context packet is not reachable from INDEX.md: {packet.name}")
        try:
            text = packet.read_text(encoding="utf-8")
        except OSError:
            continue
        match = re.search(r"<!--\s*source-events:\s*(.*?)\s*-->", text)
        if not match:
            errors.append(f"context packet is missing source-events metadata: {packet.name}")
            continue
        for source_id in match.group(1).split():
            if source_id not in event_ids:
                errors.append(f"context packet {packet.name} references unknown source event: {source_id}")
    return sorted(set(errors))


def _preserved_semantic_section(root: Path) -> str | None:
    """Return model-authored root breadcrumbs without trusting them as valid."""

    try:
        text = root.read_text(encoding="utf-8")
    except OSError:
        return None
    match = re.search(
        r"<!-- semantic-breadcrumbs:start -->\s*\n(.*?)\n<!-- semantic-breadcrumbs:end -->",
        text,
        flags=re.DOTALL,
    )
    return match.group(1).strip() if match else None


def _has_anchor(path: Path, anchor: str) -> bool:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return False
    return anchor in set(ANCHOR_MARKER.findall(text)) or anchor in set(EVENT_MARKER.findall(text))


def _has_jsonl_line_range(path: Path, fragment: str) -> bool:
    """Validate an optional #Lstart-Lend locator on an append-only JSONL file."""

    if path.suffix.lower() != ".jsonl":
        return False
    match = re.fullmatch(r"L(\d+)(?:-L?(\d+))?", fragment)
    if not match:
        return False
    start = int(match.group(1))
    end = int(match.group(2) or match.group(1))
    if start < 1 or end < start:
        return False
    try:
        line_count = sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())
    except OSError:
        return False
    return end <= line_count


def _reachable_markdown(session_dir: Path, root: Path) -> tuple[set[Path], list[str]]:
    if not root.is_file():
        return set(), []
    reachable: set[Path] = set()
    errors: list[str] = []
    pending = [root.resolve()]
    while pending:
        current = pending.pop()
        if current in reachable:
            continue
        reachable.add(current)
        try:
            text = current.read_text(encoding="utf-8")
        except OSError as exc:
            errors.append(f"cannot read linked Markdown file {current.name}: {exc}")
            continue
        for raw_target in MARKDOWN_LINK.findall(_without_fenced_code(text)):
            target = raw_target.strip().split("#", 1)[0]
            fragment = raw_target.strip().split("#", 1)[1] if "#" in raw_target else ""
            if not target:
                continue
            external_path = _local_markdown_path(target)
            if external_path is not None:
                if not external_path.is_file():
                    errors.append(f"broken Markdown link: {current.relative_to(session_dir)} -> {raw_target}")
                elif fragment and not (_has_anchor(external_path, fragment) or _has_jsonl_line_range(external_path, fragment)):
                    errors.append(f"broken Markdown anchor: {current.relative_to(session_dir)} -> {raw_target}")
                continue
            if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target):
                continue
            resolved = (current.parent / target).resolve()
            if session_dir not in resolved.parents and resolved != session_dir:
                errors.append(f"link escapes session graph: {current.name} -> {raw_target}")
                continue
            if not resolved.is_file():
                errors.append(f"broken Markdown link: {current.relative_to(session_dir)} -> {raw_target}")
                continue
            if fragment and not (_has_anchor(resolved, fragment) or _has_jsonl_line_range(resolved, fragment)):
                errors.append(f"broken Markdown anchor: {current.relative_to(session_dir)} -> {raw_target}")
            if resolved.suffix.lower() == ".md":
                pending.append(resolved)
    return reachable, errors


def _without_fenced_code(text: str) -> str:
    """Exclude code fences so serialized payloads cannot become graph edges."""

    visible: list[str] = []
    fence: str | None = None
    for line in text.splitlines(keepends=True):
        stripped = line.lstrip()
        if fence is None:
            if stripped.startswith("```"):
                fence = "```"
                continue
            if stripped.startswith("~~~"):
                fence = "~~~"
                continue
            visible.append(line)
            continue
        if stripped.startswith(fence):
            fence = None
    return "".join(visible)


def _local_markdown_path(target: str) -> Path | None:
    """Resolve a local file URI without treating web links as session files."""

    parsed = urlparse(target)
    if parsed.scheme.lower() != "file" or parsed.netloc not in ("", "localhost"):
        return None
    path = unquote(parsed.path)
    if os.name == "nt" and re.match(r"^/[A-Za-z]:/", path):
        path = path[1:]
    return Path(path).resolve()


def recovery_context(session_dir: Path, validation_errors: list[str]) -> str:
    root = (session_dir / "INDEX.md").as_posix()
    status = "The graph passed deterministic reachability validation."
    if validation_errors:
        status = "The graph needs repair before relying on semantic indexes: " + "; ".join(validation_errors[:3])
    return (
        "Adaptive Agents remains active. Total Recall session graph root: "
        f"{root}. When historical detail is needed, read that INDEX.md and follow its linked indexes and event records; "
        "do not assume the compacted context is complete. Semantic breadcrumbs should use descriptive link text and explain why important details matter; event-type indexes are only fallback navigation. "
        f"{adaptive_agents_guidance()} "
        "The pre-compaction checkpoint is the graph-construction boundary; this recovery hook restores the pointer and retrieval contract rather than rebuilding the graph from compacted context. {status}"
    ).format(status=status)


def semantic_maintenance_prompt(session_dir: Path) -> str:
    """Build the model instruction for a full-context pre-compaction pass.

    Codex does not deliver ``additionalContext`` from ``PreCompact``. A
    supported incremental or separate maintenance caller can use this prompt
    while the complete session graph is still available, then run validation
    before accepting the model-authored changes.
    """

    root = (session_dir / "INDEX.md").as_posix()
    return (
        "Before compaction, maintain the Total Recall semantic graph while full session detail is available. "
        f"Read the session root at {root} and its retained event records. "
        "Create or update semantic breadcrumb indexes for important instructions, decisions, requirements, "
        "unresolved questions, preferences, milestones, evidence, and artifacts. Use descriptive Markdown "
        "link text that says what the target contains and why it matters; never rely on opaque IDs or generic "
        "labels alone. Every breadcrumb must link to a stable source record or narrower semantic index, and "
        "the deterministic validator must pass before the changes become authoritative. Preserve the event "
        "ledger and fallback indexes; do not replace them with a semantic summary.\n\n"
        + SEMANTIC_BREADCRUMB_CONTRACT
    )


def adaptive_agents_guidance() -> str:
    """Identify the canonical Adaptive Agents activation files for recovery."""

    candidates = (
        Path(__file__).resolve().parent.parent,
        Path.home() / ".adaptive-agents",
    )
    for root in candidates:
        agents = root / "AGENTS.md"
        if agents.is_file():
            return (
                "Restore Adaptive Agents prompting by reading the canonical "
                f"{agents.as_posix()} before continuing."
            )
    return "Restore Adaptive Agents prompting by reading the canonical AGENTS.md before continuing."


def user_prompt_context(session_dir: Path) -> str:
    """Give the active model the supported incremental maintenance contract."""

    root = (session_dir / "INDEX.md").as_posix()
    return (
        "Total Recall maintenance: while full session detail is available, treat the session root "
        f"{root} as the semantic navigation surface. If this turn establishes an important instruction, "
        "decision, requirement, unresolved question, durable fact, evidence item, or artifact, update the "
        "root semantic breadcrumb section with descriptive link text, why the target matters, and a stable "
        "source link. A breadcrumb may point directly to ledger.jsonl with an inclusive #Lstart-Lend range, or delegate a named topic to a narrower index; these forms may be mixed at every level. Preserve the event ledger; deterministic validation will reject broken, invalid-range, or orphaned links. "
        "This is the supported pre-compaction maintenance path; the PreCompact hook itself cannot inject model context."
    )


def hook_configuration(script_path: Path, python_executable: str | None = None) -> dict[str, Any]:
    """Return the Codex hooks.json contract used by the installer child."""

    interpreter = python_executable or sys.executable
    command = f'"{interpreter}" "{script_path.resolve()}"'
    windows_command = " ".join(
        value if not any(character.isspace() for character in value) else f'"{value}"'
        for value in (interpreter, str(script_path.resolve()))
    )

    def handler(*, additional_context: bool = False, timeout: int = 10) -> dict[str, Any]:
        value: dict[str, Any] = {
            "type": "command",
            "command": command,
            "commandWindows": windows_command,
            "timeout": timeout,
        }
        if additional_context:
            value["additionalContextLimit"] = 1200
        return value

    return {
        "description": "Adaptive Agents Total Recall session graph hooks",
        "hooks": {
            "SessionStart": [{"matcher": "startup|resume|clear|compact|fork", "hooks": [handler(additional_context=True)]}],
            "UserPromptSubmit": [{"matcher": ".*", "hooks": [handler(additional_context=True)]}],
            "PreToolUse": [{"matcher": ".*", "hooks": [handler()]}],
            "PostToolUse": [{"matcher": ".*", "hooks": [handler()]}],
            "PreCompact": [{"matcher": "manual|auto", "hooks": [handler()]}],
            "PostCompact": [{"matcher": "manual|auto", "hooks": [handler()]}],
            "SubagentStart": [{"matcher": ".*", "hooks": [handler()]}],
            "SubagentStop": [{"matcher": ".*", "hooks": [handler()]}],
            "Stop": [{"matcher": ".*", "hooks": [handler()]}],
            "SessionEnd": [{"matcher": "other", "hooks": [handler(timeout=3)]}],
        },
    }


def handle_hook(data: dict[str, Any], store: SessionStore | None = None) -> dict[str, Any] | None:
    store = store or SessionStore()
    session_dir, _, _ = store.capture(data)
    if event_kind(data) == "SessionStart":
        errors = store.validate(session_dir)
        return {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": recovery_context(session_dir, errors),
            }
        }
    if event_kind(data) == "UserPromptSubmit":
        return {
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": user_prompt_context(session_dir),
            }
        }
    return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=APP_NAME)
    parser.add_argument("--validate", type=Path, help="validate an existing session directory")
    parser.add_argument("--hooks-json", action="store_true", help="print the Codex hooks.json contract")
    parser.add_argument("--root", type=Path, help="override the session namespace (testing/diagnostics)")
    args = parser.parse_args(argv)
    if args.hooks_json:
        print(json.dumps(hook_configuration(Path(__file__)), indent=2))
        return 0
    if args.validate:
        errors = validate_session(args.validate)
        if errors:
            for error in errors:
                print(f"ERROR: {error}", file=sys.stderr)
            return 1
        print("Total Recall session graph is valid.")
        return 0

    try:
        raw = sys.stdin.read()
        data = json.loads(raw)
        if not isinstance(data, dict):
            raise ValueError("hook input must be a JSON object")
        output = handle_hook(data, SessionStore(args.root) if args.root else None)
        if output is not None:
            print(json.dumps(output, ensure_ascii=False))
        return 0
    except Exception as exc:  # Hooks must not break the Codex operation.
        print(f"{APP_NAME}: {exc}", file=sys.stderr)
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
