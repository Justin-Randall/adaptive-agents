#!/usr/bin/env python3
"""Safely provision the Adaptive Agents Total Recall Codex hook configuration."""

from __future__ import annotations

import argparse
import json
import os
import shlex
import tempfile
from pathlib import Path
from typing import Any
import tomllib


DESCRIPTION = "Adaptive Agents Total Recall session graph hooks"


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def desired_config(script: Path, python_executable: str) -> dict[str, Any]:
    command = f'"{python_executable}" "{script.resolve()}"'
    windows_command = " ".join(
        value if not any(character.isspace() for character in value) else f'"{value}"'
        for value in (python_executable, str(script.resolve()))
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
        "description": DESCRIPTION,
        "hooks": {
            "SessionStart": [{"matcher": "startup|resume|clear|compact|fork", "hooks": [handler(additional_context=True)]}],
            "UserPromptSubmit": [{"hooks": [handler(additional_context=True)]}],
            "PreToolUse": [{"matcher": ".*", "hooks": [handler()]}],
            "PostToolUse": [{"matcher": ".*", "hooks": [handler()]}],
            "PreCompact": [{"matcher": "manual|auto", "hooks": [handler()]}],
            "PostCompact": [{"matcher": "manual|auto", "hooks": [handler()]}],
            "SubagentStart": [{"matcher": ".*", "hooks": [handler()]}],
            "SubagentStop": [{"matcher": ".*", "hooks": [handler()]}],
            "Stop": [{"hooks": [handler()]}],
            "SessionEnd": [{"matcher": "other", "hooks": [handler(timeout=3)]}],
        },
    }


def read_existing(path: Path) -> tuple[str, dict[str, Any] | None]:
    if not path.exists():
        return "", None
    raw = path.read_text(encoding="utf-8")
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        fail(f"existing hooks.json is not strict JSON; preserve it and merge manually: {exc}")
    if not isinstance(value, dict):
        fail("existing hooks.json must contain an object; preserve it and merge manually")
    return raw, value


def command_targets_managed_script(command: str, *, windows: bool = False) -> bool:
    try:
        parts = shlex.split(command, posix=not windows)
    except ValueError:
        return False
    parts = [part.strip('"') for part in parts]
    if len(parts) != 2:
        return False
    target_name = Path(parts[1].replace("\\", "/")).name.lower()
    return target_name in {"codex_total_recall.py", "launcher.py"}


def can_manage(existing: dict[str, Any] | None) -> bool:
    if existing is None:
        return True
    if set(existing) != {"description", "hooks"} or existing.get("description") != DESCRIPTION:
        return False
    hooks = existing.get("hooks")
    if not isinstance(hooks, dict):
        return False
    expected = desired_config(Path("codex_total_recall.py"), "python")["hooks"]
    if set(hooks) != set(expected):
        return False

    for event_name, expected_entries in expected.items():
        actual_entries = hooks.get(event_name)
        if not isinstance(actual_entries, list) or len(actual_entries) != len(expected_entries):
            return False
        for actual_entry, expected_entry in zip(actual_entries, expected_entries):
            if not isinstance(actual_entry, dict) or set(actual_entry) != set(expected_entry):
                return False
            for key, expected_value in expected_entry.items():
                if key != "hooks" and actual_entry.get(key) != expected_value:
                    return False
            actual_handlers = actual_entry.get("hooks")
            expected_handlers = expected_entry.get("hooks")
            if not isinstance(actual_handlers, list) or not isinstance(expected_handlers, list):
                return False
            if len(actual_handlers) != len(expected_handlers):
                return False
            for actual_handler, expected_handler in zip(actual_handlers, expected_handlers):
                if not isinstance(actual_handler, dict):
                    return False
                if set(actual_handler) != set(expected_handler):
                    return False
                if any(
                    actual_handler.get(key) != value
                    for key, value in expected_handler.items()
                    if key not in {"command", "commandWindows"}
                ):
                    return False
                command = actual_handler.get("command")
                windows_command = actual_handler.get("commandWindows")
                if not isinstance(command, str) or not command_targets_managed_script(command):
                    return False
                if not isinstance(windows_command, str) or not command_targets_managed_script(
                    windows_command,
                    windows=True,
                ):
                    return False
    return True


def validate_hook_layer(config_path: Path | None, hooks_path: Path) -> None:
    if config_path is None or not config_path.exists():
        return
    try:
        config = tomllib.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        fail(f"could not validate Codex hook configuration layers: {exc}")
    features = config.get("features", {})
    if isinstance(features, dict) and features.get("hooks") is False:
        fail("Codex hooks are disabled in config.toml; enable them before installing Total Recall")
    inline_hooks = config.get("hooks")
    if inline_hooks:
        fail(
            "Codex config.toml defines inline hooks; preserve them and resolve the "
            "user-level hook representation conflict before installing hooks.json"
        )


def write_atomic(path: Path, content: str) -> None:
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--script", required=True, type=Path)
    parser.add_argument("--python", required=True)
    parser.add_argument("--toml-config", type=Path)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    validate_hook_layer(args.toml_config, args.config)
    raw, existing = read_existing(args.config)
    if not can_manage(existing):
        fail(
            "existing hooks.json contains unrecognized or modified hooks; "
            "preserve it and resolve the conflict manually"
        )
    expected = desired_config(args.script, args.python)
    rendered = json.dumps(expected, indent=2, ensure_ascii=False) + "\n"
    if raw == rendered:
        print("Codex Total Recall hooks are already installed.")
        return 0
    if args.check:
        fail("Codex Total Recall hooks are missing or stale")
    if not args.apply:
        print("Codex Total Recall hook preflight passed.")
        return 0
    write_atomic(args.config, rendered)
    print(f"Updated Codex Total Recall hooks: {args.config}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
