#!/usr/bin/env python3
"""Copilot-harness adapter for the shared Markdown Total Recall ledger."""

from __future__ import annotations

import json
import hashlib
import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from codex import codex_total_recall as recall
from vscode import session_start


EVENTS = {
    "sessionStart": "SessionStart",
    "userPromptSubmitted": "UserPromptSubmit",
    "preToolUse": "PreToolUse",
    "postToolUse": "PostToolUse",
    "postToolUseFailure": "PostToolUseFailure",
    "preCompact": "PreCompact",
    "subagentStart": "SubagentStart",
    "subagentStop": "SubagentStop",
    "agentStop": "Stop",
    "sessionEnd": "SessionEnd",
}

EVENT_ALIASES = {**EVENTS, **{value: value for value in EVENTS.values()}}
TRANSCRIPT_MAX_BYTES = 16 * 1024 * 1024


def latest_assistant_response(transcript_path: str | None) -> str | None:
    """Return the latest visible assistant message from a Copilot transcript."""
    if not transcript_path:
        return None
    path = Path(transcript_path)
    if not path.is_file():
        return None
    latest: str | None = None
    try:
        with path.open("rb") as stream:
            stream.seek(0, os.SEEK_END)
            end = stream.tell()
            stream.seek(max(0, end - TRANSCRIPT_MAX_BYTES))
            if stream.tell() > 0:
                stream.readline()
            for raw in stream:
                try:
                    record = json.loads(raw.decode("utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError):
                    continue
                if record.get("type") != "assistant.message":
                    continue
                content = record.get("data", {}).get("content")
                if isinstance(content, str) and content:
                    latest = content
    except OSError:
        return None
    return latest


def capture_assistant_response(data: dict, store: recall.SessionStore) -> None:
    if data.get("hook_event_name") != "Stop":
        return
    response = latest_assistant_response(data.get("transcriptPath"))
    if not response:
        return
    store.capture({
        "cwd": data.get("cwd", os.getcwd()),
        "hook_event_name": "AssistantResponse",
        "sessionId": data["session_id"],
        "session_id": data["session_id"],
        "transcriptPath": data.get("transcriptPath"),
        "assistant_response": response,
        "assistant_response_sha256": hashlib.sha256(response.encode("utf-8")).hexdigest(),
    })


def normalize(payload: dict) -> dict:
    event_name = payload.get("hookEventName") or payload.get("hook_event_name")
    if not isinstance(event_name, str):
        event_name = os.environ.get("ADAPTIVE_COPILOT_EVENT", "")
    if event_name not in EVENT_ALIASES:
        raise ValueError(f"unsupported Copilot hook event: {event_name or '<missing>'}")
    normalized = dict(payload)
    normalized["hook_event_name"] = EVENT_ALIASES[event_name]
    session_id = payload.get("sessionId") or payload.get("session_id")
    if not isinstance(session_id, str) or not session_id:
        raise ValueError("Copilot hook payload is missing sessionId")
    normalized["session_id"] = session_id
    normalized.setdefault("cwd", os.getcwd())
    return normalized


def main() -> int:
    try:
        payload = json.loads(sys.stdin.buffer.read().decode("utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("Copilot hook payload must be an object")
        normalized = normalize(payload)
        configured_root = os.environ.get("ADAPTIVE_TOTAL_RECALL_STORE")
        store = recall.SessionStore(Path(configured_root) if configured_root else None, provider="copilot")
        output = recall.handle_hook(normalized, store=store)
        capture_assistant_response(normalized, store)
        if normalized["hook_event_name"] == "SessionStart":
            repo_root = Path(__file__).resolve().parents[2]
            checker = session_start.load_budget_checker()
            profile = session_start.load_profile(repo_root, checker)
            context = session_start.build_static_context(repo_root, profile, checker)
            dynamic = session_start.run_session_start(repo_root / "scripts" / "session-start.sh")
            status_file = Path.home() / ".cache" / "adaptive-agents" / "vscode-session-start-status.json"
            session_start.write_status(status_file, repo_root, profile, dynamic)
            if dynamic:
                context += f"\n\n--- DYNAMIC STARTUP OUTPUT ---\n{dynamic}"
            recall_context = (output or {}).get("hookSpecificOutput", {}).get("additionalContext", "")
            output = {"hookSpecificOutput": {"additionalContext": context + "\n\n" + recall_context}}
        if output is None:
            print("{}")
        else:
            specific = output.get("hookSpecificOutput", {})
            context = specific.get("additionalContext")
            print(json.dumps({"additionalContext": context} if context else {}, ensure_ascii=True))
        return 0
    except (json.JSONDecodeError, OSError, ValueError, RuntimeError) as exc:
        print(f"Adaptive Agents Copilot Total Recall: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
