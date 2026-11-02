#!/usr/bin/env python3
"""Safely provision the Adaptive Agents Total Recall Codex hook configuration."""

from __future__ import annotations

import argparse
import json
import os
import shlex
import tempfile
from pathlib import Path
from typing import Any, NoReturn
import tomllib


DESCRIPTION = "Adaptive Agents Total Recall session graph hooks"
INLINE_HOOKS_START = "# BEGIN ADAPTIVE_AGENTS_TOTAL_RECALL_HOOKS"
INLINE_HOOKS_END = "# END ADAPTIVE_AGENTS_TOTAL_RECALL_HOOKS"
MANAGED_EVENTS = {
    "SessionStart",
    "UserPromptSubmit",
    "PreToolUse",
    "PostToolUse",
    "PreCompact",
    "PostCompact",
    "SubagentStart",
    "SubagentStop",
    "Stop",
    "SessionEnd",
}


def fail(message: str) -> NoReturn:
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
            "SessionStart": [{"matcher": "startup|resume|clear|compact|fork", "hooks": [handler(additional_context=True, timeout=60)]}],
            "UserPromptSubmit": [{"hooks": [handler(additional_context=True)]}],
            "PreToolUse": [{"matcher": ".*", "hooks": [handler()]}],
            "PostToolUse": [{"matcher": ".*", "hooks": [handler(additional_context=True)]}],
            "PreCompact": [{"matcher": "manual|auto", "hooks": [handler()]}],
            "PostCompact": [{"matcher": "manual|auto", "hooks": [handler()]}],
            "SubagentStart": [{"matcher": ".*", "hooks": [handler()]}],
            "SubagentStop": [{"matcher": ".*", "hooks": [handler()]}],
            "Stop": [{"hooks": [handler(timeout=60)]}],
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
    if not isinstance(hooks, dict) or not hooks or not set(hooks).issubset(MANAGED_EVENTS):
        return False
    expected = desired_config(Path("codex_total_recall.py"), "python")["hooks"]
    if set(hooks) != set(expected):
        return False

    supported_handler_fields = {
        "type",
        "command",
        "commandWindows",
        "command_windows",
        "timeout",
        "additionalContextLimit",
        "statusMessage",
        "async",
    }
    for event_name, actual_entries in hooks.items():
        expected_entries = expected.get(event_name, [])
        if not isinstance(actual_entries, list) or len(actual_entries) != len(expected_entries):
            return False
        for index, actual_entry in enumerate(actual_entries):
            expected_entry = expected_entries[index] if index < len(expected_entries) else {}
            if (
                not isinstance(actual_entry, dict)
                or "hooks" not in actual_entry
                or not set(actual_entry).issubset({"matcher", "hooks"})
            ):
                return False
            matcher = actual_entry.get("matcher")
            if matcher is not None and not isinstance(matcher, str):
                return False
            actual_handlers = actual_entry.get("hooks")
            expected_handlers = expected_entry.get("hooks", [])
            if (
                not isinstance(actual_handlers, list)
                or len(actual_handlers) != len(expected_handlers)
            ):
                return False
            for actual_handler in actual_handlers:
                if (
                    not isinstance(actual_handler, dict)
                    or not {"type", "command"}.issubset(actual_handler)
                    or not set(actual_handler).issubset(supported_handler_fields)
                    or actual_handler.get("type") != "command"
                ):
                    return False
                command = actual_handler.get("command")
                if not isinstance(command, str) or not command_targets_managed_script(command):
                    return False
                windows_command = actual_handler.get("commandWindows", actual_handler.get("command_windows"))
                if windows_command is not None and (
                    not isinstance(windows_command, str)
                    or not command_targets_managed_script(windows_command, windows=True)
                ):
                    return False
                timeout = actual_handler.get("timeout")
                if timeout is not None and (
                    not isinstance(timeout, int) or isinstance(timeout, bool) or timeout < 1
                ):
                    return False
                context_limit = actual_handler.get("additionalContextLimit")
                if context_limit is not None and (
                    not isinstance(context_limit, int)
                    or isinstance(context_limit, bool)
                    or context_limit < 0
                ):
                    return False
                if "statusMessage" in actual_handler and not isinstance(
                    actual_handler["statusMessage"], str
                ):
                    return False
                if "async" in actual_handler and not isinstance(actual_handler["async"], bool):
                    return False
    return True


def validate_hook_layer(config_path: Path | None, hooks_path: Path) -> bool:
    if config_path is None or not config_path.exists():
        return False
    try:
        config = tomllib.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        fail(f"could not validate Codex hook configuration layers: {exc}")
    features = config.get("features", {})
    if isinstance(features, dict) and features.get("hooks") is False:
        fail("Codex hooks are disabled in config.toml; enable them before installing Total Recall")
    inline_hooks = config.get("hooks")
    if inline_hooks is not None and not isinstance(inline_hooks, dict):
        fail("Codex config.toml has an invalid inline hooks table; preserve it and resolve it manually")
    return bool(inline_hooks)


def _toml_value(value: Any) -> str:
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    fail(f"unsupported value in managed Codex hook configuration: {type(value).__name__}")


def render_inline_hooks(config: dict[str, Any], newline: str) -> str:
    lines = [INLINE_HOOKS_START]
    for event_name, entries in config["hooks"].items():
        for entry in entries:
            lines.append(f"[[hooks.{event_name}]]")
            for key, value in entry.items():
                if key == "hooks":
                    continue
                lines.append(f"{key} = {_toml_value(value)}")
            for handler in entry["hooks"]:
                lines.append(f"[[hooks.{event_name}.hooks]]")
                for key, value in handler.items():
                    toml_key = "command_windows" if key == "commandWindows" else key
                    lines.append(f"{toml_key} = {_toml_value(value)}")
    lines.append(INLINE_HOOKS_END)
    return newline.join(lines) + newline


def managed_inline_block(raw: str) -> tuple[int, int, str] | None:
    lines = raw.splitlines(keepends=True)
    start_indexes = [
        index for index, line in enumerate(lines) if line.rstrip("\r\n") == INLINE_HOOKS_START
    ]
    end_indexes = [
        index for index, line in enumerate(lines) if line.rstrip("\r\n") == INLINE_HOOKS_END
    ]
    if not start_indexes and not end_indexes:
        return None
    if len(start_indexes) != 1 or len(end_indexes) != 1 or start_indexes[0] >= end_indexes[0]:
        fail("managed inline hook markers are malformed; preserve config.toml and resolve them manually")

    start_line = start_indexes[0]
    end_line = end_indexes[0]
    block_content = "".join(lines[start_line + 1 : end_line])
    try:
        parsed = tomllib.loads(block_content)
    except tomllib.TOMLDecodeError as exc:
        fail(f"managed inline hook block is invalid TOML; preserve it and resolve it manually: {exc}")

    hooks = parsed.get("hooks")
    normalized_hooks: dict[str, Any] = {}
    if isinstance(hooks, dict):
        for event_name, entries in hooks.items():
            if not isinstance(entries, list):
                return _invalid_managed_inline_block()
            normalized_entries: list[Any] = []
            for entry in entries:
                if not isinstance(entry, dict):
                    return _invalid_managed_inline_block()
                normalized_entry = dict(entry)
                handlers = normalized_entry.get("hooks")
                if not isinstance(handlers, list):
                    return _invalid_managed_inline_block()
                normalized_handlers: list[Any] = []
                for handler in handlers:
                    if not isinstance(handler, dict):
                        return _invalid_managed_inline_block()
                    normalized_handler = dict(handler)
                    if "command_windows" in normalized_handler:
                        normalized_handler["commandWindows"] = normalized_handler.pop("command_windows")
                    normalized_handlers.append(normalized_handler)
                normalized_entry["hooks"] = normalized_handlers
                normalized_entries.append(normalized_entry)
            normalized_hooks[event_name] = normalized_entries
    if not can_manage({"description": DESCRIPTION, "hooks": normalized_hooks}):
        fail(
            "managed inline hook block contains unrecognized hooks; preserve config.toml "
            "and resolve the conflict manually"
        )

    offsets = [0]
    for line in lines:
        offsets.append(offsets[-1] + len(line))
    start_offset = offsets[start_line]
    end_offset = offsets[end_line + 1]
    return start_offset, end_offset, raw[start_offset:end_offset]


def _invalid_managed_inline_block() -> None:
    fail("managed inline hook block has an invalid structure; preserve config.toml and resolve it manually")


def replace_inline_hooks(raw: str, desired_block: str) -> str:
    existing_block = managed_inline_block(raw)
    if existing_block is not None:
        start, end, _ = existing_block
        return raw[:start] + desired_block + raw[end:]
    if not raw:
        return desired_block
    separator = "" if raw.endswith(("\n", "\r")) else "\n"
    blank_line = "" if raw.endswith(("\n\n", "\r\n\r\n")) else "\n"
    return raw + separator + blank_line + desired_block


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

    has_inline_hooks = validate_hook_layer(args.toml_config, args.config)
    raw, existing = read_existing(args.config)
    if not can_manage(existing):
        fail(
            "existing hooks.json contains unrecognized hooks; preserve it and "
            "resolve the conflict manually"
        )
    expected = desired_config(args.script, args.python)
    rendered = json.dumps(expected, indent=2, ensure_ascii=False) + "\n"

    if has_inline_hooks:
        if args.toml_config is None:
            fail("inline Codex hooks were detected without a config.toml path")
        toml_raw = args.toml_config.read_text(encoding="utf-8")
        newline = "\r\n" if "\r\n" in toml_raw else "\n"
        desired_block = render_inline_hooks(expected, newline)
        current_block = managed_inline_block(toml_raw)
        if (
            current_block is not None
            and current_block[2] == desired_block
            and existing is None
        ):
            print("Codex Total Recall inline hooks are already installed.")
            return 0
        if args.check:
            fail("Codex Total Recall inline hooks are missing, stale, or still duplicated in hooks.json")
        if not args.apply:
            print("Codex Total Recall inline-hook preflight passed.")
            return 0
        updated_toml = replace_inline_hooks(toml_raw, desired_block)
        try:
            tomllib.loads(updated_toml)
        except tomllib.TOMLDecodeError as exc:
            fail(f"managed inline-hook update would produce invalid TOML: {exc}")
        write_atomic(args.toml_config, updated_toml)
        if existing is not None:
            args.config.unlink()
        print(f"Updated Codex Total Recall inline hooks: {args.toml_config}")
        return 0

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
