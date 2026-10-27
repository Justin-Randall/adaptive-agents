#!/usr/bin/env python3
"""Safely add the Adaptive Agents repository to Codex workspace-write roots."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
import tomllib
from pathlib import Path


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def transform(raw: str, repo_root: Path) -> str:
    try:
        config = tomllib.loads(raw)
    except tomllib.TOMLDecodeError as exc:
        fail(f"config.toml is invalid TOML: {exc}")

    if "default_permissions" in config:
        fail("config.toml uses default_permissions; merge this permission profile manually before installing")
    sandbox_mode = config.get("sandbox_mode")
    if sandbox_mode is not None and sandbox_mode != "workspace-write":
        fail(f"sandbox_mode is {sandbox_mode!r}; installer preserves it and requires workspace-write")

    root = repo_root.resolve().as_posix()
    section = config.get("sandbox_workspace_write")
    if section is not None and not isinstance(section, dict):
        fail("sandbox_workspace_write must be a TOML table")
    roots = (section or {}).get("writable_roots", [])
    if not isinstance(roots, list) or any(not isinstance(item, str) for item in roots):
        fail("sandbox_workspace_write.writable_roots must be an array of strings")
    normalized_root = os.path.normcase(root)
    if any(os.path.normcase(item.replace("\\", "/")) == normalized_root for item in roots):
        return raw

    newline = "\r\n" if "\r\n" in raw else "\n"
    quoted = json.dumps(root)
    if section is None:
        suffix = "" if not raw or raw.endswith(("\n", "\r")) else newline
        return raw + suffix + f"[sandbox_workspace_write]{newline}writable_roots = [{quoted}]{newline}"

    lines = raw.splitlines(keepends=True)
    in_section = False
    start = None
    end = None
    for index, line in enumerate(lines):
        header = re.match(r"\s*\[([^]]+)\]", line)
        if header:
            if in_section:
                break
            in_section = header.group(1).strip() == "sandbox_workspace_write"
            continue
        if in_section and re.match(r"\s*writable_roots\s*=", line):
            start = index
            break

    if start is None:
        for index, line in enumerate(lines):
            if re.match(r"\s*\[sandbox_workspace_write\]\s*(?:#.*)?(?:\r?\n)?$", line):
                start = end = index + 1
                break
        if start is None:
            fail("could not locate the sandbox_workspace_write table for a safe merge")
        lines.insert(start, f"writable_roots = [{quoted}]{newline}")
        return "".join(lines)

    # Find the closing bracket of this array while ignoring quoted text/comments.
    assignment = "".join(lines[start:])
    opening = assignment.find("[")
    if opening < 0:
        fail("could not parse writable_roots array for a safe merge")
    depth = 0
    in_string = False
    escaped = False
    closing = None
    offset = opening
    while offset < len(assignment):
        char = assignment[offset]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            offset += 1
            continue
        if char == "#":
            newline_at = assignment.find("\n", offset)
            if newline_at < 0:
                break
            offset = newline_at + 1
            continue
        if char == '"':
            in_string = True
        elif char == "[":
            depth += 1
        elif char == "]":
            depth -= 1
            if depth == 0:
                closing = offset
                break
        offset += 1
    if closing is None:
        fail("could not find the end of writable_roots array")
    array_body = assignment[opening + 1 : closing]
    meaningful = []
    quoted_string = False
    escaped_char = False
    comment = False
    for char in array_body:
        if comment:
            if char in "\r\n":
                comment = False
            continue
        if quoted_string:
            meaningful.append(char)
            if escaped_char:
                escaped_char = False
            elif char == "\\":
                escaped_char = True
            elif char == '"':
                quoted_string = False
            continue
        if char == "#":
            comment = True
        elif char == '"':
            quoted_string = True
            meaningful.append(char)
        elif not char.isspace():
            meaningful.append(char)
    separator = "" if not roots or meaningful[-1:] == [","] else ", "
    insertion = separator + quoted
    absolute = sum(len(part) for part in lines[:start]) + closing
    full = "".join(lines)
    updated = full[:absolute] + insertion + full[absolute:]
    try:
        tomllib.loads(updated)
    except tomllib.TOMLDecodeError as exc:
        fail(f"safe config merge produced invalid TOML: {exc}")
    return updated


def redirect(repo_root: Path) -> str:
    target = (repo_root.resolve() / "AGENTS.md").as_posix()
    return (
        "<!-- adaptive-agents:codex-redirect -->\n"
        "# Adaptive Agents\n\n"
        f"Before responding, read and follow the canonical Adaptive Agents instructions at `{target}`.\n"
        "Follow their discovery protocol to load relevant guidance.\n"
    )


def valid_entrypoint(path: Path, repo_root: Path) -> bool:
    if path.is_symlink():
        return path.resolve() == (repo_root / "AGENTS.md").resolve()
    return path.is_file() and path.read_text(encoding="utf-8") == redirect(repo_root)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--global-instructions", type=Path)
    parser.add_argument("--install-instructions", action="store_true")
    args = parser.parse_args()
    if args.global_instructions is not None:
        entry = args.global_instructions
        if (entry.exists() or entry.is_symlink()) and not valid_entrypoint(entry, args.repo_root):
            fail("existing global instructions are not the canonical redirect or symlink; preserving them")
    if args.install_instructions:
        if args.global_instructions is None:
            fail("--global-instructions is required with --install-instructions")
        if not entry.exists() and not entry.is_symlink():
            entry.parent.mkdir(parents=True, exist_ok=True)
            with entry.open("x", encoding="utf-8", newline="\n") as stream:
                stream.write(redirect(args.repo_root))
        return 0
    if args.check:
        if args.global_instructions is None:
            fail("--global-instructions is required with --check")
        try:
            if not valid_entrypoint(args.global_instructions, args.repo_root):
                fail("Codex global AGENTS.md is missing or does not resolve to the canonical repository file")
            config = tomllib.loads(args.config.read_text(encoding="utf-8"))
        except (OSError, tomllib.TOMLDecodeError) as exc:
            fail(f"could not validate Codex config: {exc}")
        if "default_permissions" in config:
            fail("config.toml uses default_permissions")
        if config.get("sandbox_mode", "workspace-write") != "workspace-write":
            fail("config.toml sandbox_mode is not workspace-write")
        sandbox = config.get("sandbox_workspace_write", {})
        if not isinstance(sandbox, dict):
            fail("sandbox_workspace_write is not a TOML table")
        roots = sandbox.get("writable_roots", [])
        if not isinstance(roots, list) or any(not isinstance(item, str) for item in roots):
            fail("sandbox_workspace_write.writable_roots is not an array of strings")
        expected = args.repo_root.resolve().as_posix()
        normalized_expected = os.path.normcase(expected)
        if not any(os.path.normcase(item.replace("\\", "/")) == normalized_expected for item in roots):
            fail("sandbox_workspace_write.writable_roots is missing the Adaptive Agents repository")
        print("Codex entrypoint and repository-scoped workspace-write grant are valid.")
        return 0
    raw = args.config.read_text(encoding="utf-8") if args.config.exists() else ""
    updated = transform(raw, args.repo_root)
    if updated == raw:
        print("Codex permission grant is already present.")
        return 0
    if not args.apply:
        print("Codex permission config preflight passed.")
        return 0
    args.config.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".adaptive-agents-codex-", dir=args.config.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as stream:
            stream.write(updated)
        os.replace(temporary, args.config)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    print(f"Updated Codex permission config: {args.config}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
