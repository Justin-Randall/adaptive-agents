#!/usr/bin/env python3

import argparse
import json
import re
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description="Validate Adaptive Agents VS Code integration.")
    parser.add_argument("--settings", type=Path, required=True)
    parser.add_argument("--hook", type=Path, required=True)
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--version-output", required=True)
    return parser.parse_args()


def strip_jsonc(text):
    result = []
    index = 0
    in_string = False
    escaped = False
    line_comment = False
    block_comment = False
    while index < len(text):
        character = text[index]
        following = text[index + 1] if index + 1 < len(text) else ""
        if line_comment:
            if character in "\r\n":
                line_comment = False
                result.append(character)
            index += 1
            continue
        if block_comment:
            if character == "*" and following == "/":
                block_comment = False
                index += 2
            else:
                if character in "\r\n":
                    result.append(character)
                index += 1
            continue
        if in_string:
            result.append(character)
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == '"':
                in_string = False
            index += 1
            continue
        if character == '"':
            in_string = True
            result.append(character)
            index += 1
            continue
        if character == "/" and following == "/":
            line_comment = True
            index += 2
            continue
        if character == "/" and following == "*":
            block_comment = True
            index += 2
            continue
        result.append(character)
        index += 1
    return "".join(result)


def load_json(path, label, *, jsonc=False):
    try:
        text = path.read_text(encoding="utf-8")
        if jsonc:
            text = re.sub(r",\s*([}\]])", r"\1", strip_jsonc(text))
        return json.loads(text)
    except FileNotFoundError:
        return None
    except (json.JSONDecodeError, OSError) as error:
        raise ValueError(f"could not parse {label}: {error}") from error


def validate_version(version_output, problems):
    match = re.search(r"(\d+)\.(\d+)\.(\d+)", version_output)
    if match is None:
        problems.append("could not parse VS Code version")
        return
    major, minor, _ = (int(part) for part in match.groups())
    if major < 1 or (major == 1 and minor < 129):
        problems.append(f"detected VS Code {match.group(0)}; Adaptive Agents requires VS Code 1.129.0 or newer")


def validate_settings(settings, repo_root, problems):
    if settings is None:
        problems.append("VS Code settings file is missing")
        return
    if not isinstance(settings, dict):
        problems.append("VS Code settings root is not an object")
        return
    if settings.get("chat.useHooks") is False:
        problems.append("chat.useHooks is false")

    additional_paths = settings.get("github.copilot.chat.additionalReadAccessPaths", [])
    if not isinstance(additional_paths, list):
        problems.append("github.copilot.chat.additionalReadAccessPaths is not an array")
    elif repo_root not in additional_paths:
        problems.append("github.copilot.chat.additionalReadAccessPaths does not include the repo root")
    if "github.copilot.chat.additionalReadAccessFolders" in settings:
        problems.append("obsolete github.copilot.chat.additionalReadAccessFolders remains")

    locations = settings.get("chat.instructionsFilesLocations")
    if isinstance(locations, dict) and f"{repo_root}/vscode" in locations:
        problems.append("legacy instructions registration remains")

    approval_value = {"approve": True, "matchCommandLine": True}
    approvals = settings.get("chat.tools.terminal.autoApprove")
    if isinstance(approvals, dict):
        for pattern, value in approvals.items():
            if (
                value == approval_value
                and pattern.startswith('/^bash\\ "')
                and pattern.endswith('/scripts/session\\-start\\.sh"$/')
            ):
                problems.append("legacy session-start terminal approval remains")
                break


def validate_hook(hook, repo_root, problems):
    if hook is None:
        problems.append("Adaptive Agents hook file is missing")
        return
    expected_commands = {
        f'py -3 "{repo_root}/scripts/vscode-session-start.py"',
        f'python3 "{repo_root}/scripts/vscode-session-start.py"',
        f'python "{repo_root}/scripts/vscode-session-start.py"',
    }
    try:
        hooks = hook["hooks"]
        session_start = hooks["SessionStart"]
    except (KeyError, TypeError):
        problems.append("hook does not define SessionStart")
        return
    if not isinstance(hooks, dict) or list(hooks) != ["SessionStart"]:
        problems.append("hook contains unexpected events")
    if not isinstance(session_start, list) or len(session_start) != 1:
        problems.append("hook must define exactly one SessionStart command")
        return
    entry = session_start[0]
    if not isinstance(entry, dict) or entry.get("type") != "command":
        problems.append("SessionStart hook is not a command")
        return
    if entry.get("command") not in expected_commands:
        problems.append("SessionStart hook does not invoke the canonical Python adapter")
    if entry.get("timeout") != 30:
        problems.append("SessionStart hook timeout is not 30 seconds")


def main():
    args = parse_args()
    problems = []
    validate_version(args.version_output, problems)
    try:
        settings = load_json(args.settings, "VS Code settings", jsonc=True)
    except ValueError as error:
        problems.append(str(error))
        settings = None
    try:
        hook = load_json(args.hook, "hook")
    except ValueError as error:
        problems.append(str(error))
        hook = None
    validate_settings(settings, args.repo_root, problems)
    validate_hook(hook, args.repo_root, problems)
    print("\n".join(problems))
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())