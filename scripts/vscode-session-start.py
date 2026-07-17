#!/usr/bin/env python3

import argparse
from datetime import datetime, timezone
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


PROFILE_NAME = "non_trivial_coding"


def parse_args():
    parser = argparse.ArgumentParser(description="Emit Adaptive Agents SessionStart hook context.")
    default_root = Path(__file__).resolve().parent.parent
    parser.add_argument("--repo-root", type=Path, default=default_root)
    parser.add_argument("--runner", type=Path)
    parser.add_argument(
        "--status-file",
        type=Path,
        default=Path.home() / ".cache" / "adaptive-agents" / "vscode-session-start-status.json",
    )
    return parser.parse_args()


def load_budget_checker():
    checker_path = Path(__file__).resolve().parent / "check-instruction-load-budget.py"
    spec = importlib.util.spec_from_file_location("adaptive_agents_instruction_budget", checker_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load instruction budget checker: {checker_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_hook_input():
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    payload = json.loads(raw)
    if not isinstance(payload, dict):
        raise ValueError("hook input must be a JSON object")
    event_name = payload.get("hookEventName")
    if event_name not in (None, "SessionStart"):
        raise ValueError(f"unexpected hook event: {event_name}")
    return payload


def load_profile(repo_root, checker):
    manifest_path = repo_root / "instruction-load-routes.json"
    manifest = checker._load_json(manifest_path, "route manifest")
    baseline = checker.build_baseline(repo_root, manifest, enforce_limits=True)
    profiles = [profile for profile in baseline["profiles"] if profile["name"] == PROFILE_NAME]
    if len(profiles) != 1:
        raise checker.ValidationError(f"route manifest must define exactly one {PROFILE_NAME} profile")
    return profiles[0]


def build_static_context(repo_root, profile, checker):
    sections = [
        "Adaptive Agents session startup has already run. The canonical startup files below "
        "are authoritative for this conversation; do not run startup again.\n"
        f"Canonical Adaptive Agents repository: {repo_root.as_posix()}"
    ]
    for entry in profile["files"]:
        relative_path = entry["path"]
        content = checker.normalize_text((repo_root / relative_path).read_text(encoding="utf-8"))
        sections.append(f"--- FILE: {relative_path} ---\n{content.rstrip()}")
    return "\n\n".join(sections)


def to_bash_path(path):
    cygpath = shutil.which("cygpath")
    if cygpath is None:
        return str(path)
    result = subprocess.run(
        [cygpath, "-u", str(path)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"could not translate runner path for Bash: {result.stderr.strip()}")
    return result.stdout.strip()


def find_bash():
    if sys.platform == "win32":
        git = shutil.which("git")
        if git is None:
            raise RuntimeError("Git for Windows is required to run Adaptive Agents session startup")
        git_path = Path(git).resolve()
        for ancestor in git_path.parents:
            for relative_path in (Path("bin/bash.exe"), Path("usr/bin/bash.exe")):
                candidate = ancestor / relative_path
                if candidate.is_file():
                    return str(candidate)
        raise RuntimeError(f"could not locate Git for Windows Bash from: {git_path}")
    bash = shutil.which("bash")
    if bash is None:
        raise RuntimeError("Bash is required to run Adaptive Agents session startup")
    return bash


def run_session_start(runner):
    result = subprocess.run(
        [find_bash(), to_bash_path(runner)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        suffix = f": {detail}" if detail else ""
        raise RuntimeError(f"session-start runner failed with exit code {result.returncode}{suffix}")
    return result.stdout.rstrip("\r\n")


def write_status(path, repo_root, profile, dynamic_output):
    status = {
        "schemaVersion": 1,
        "hookEventName": "SessionStart",
        "completedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "repoRoot": repo_root.as_posix(),
        "filesLoaded": len(profile["files"]),
        "dynamicOutput": bool(dynamic_output),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            prefix=f".{path.name}.",
            suffix=".tmp",
            dir=path.parent,
            delete=False,
        ) as temporary:
            temporary_path = Path(temporary.name)
            json.dump(status, temporary, indent=2)
            temporary.write("\n")
            temporary.flush()
            os.fsync(temporary.fileno())
        os.replace(temporary_path, path)
        temporary_path = None
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def main():
    args = parse_args()
    repo_root = args.repo_root.resolve()
    runner = (args.runner or repo_root / "scripts" / "session-start.sh").resolve()
    args.status_file.unlink(missing_ok=True)
    try:
        read_hook_input()
        checker = load_budget_checker()
        profile = load_profile(repo_root, checker)
        context = build_static_context(repo_root, profile, checker)
        dynamic_output = run_session_start(runner)
        if dynamic_output:
            context += f"\n\n--- DYNAMIC STARTUP OUTPUT ---\n{dynamic_output}"
        write_status(args.status_file, repo_root, profile, dynamic_output)
        json.dump(
            {
                "hookSpecificOutput": {
                    "hookEventName": "SessionStart",
                    "additionalContext": context,
                }
            },
            sys.stdout,
            ensure_ascii=False,
        )
        sys.stdout.write("\n")
        return 0
    except (json.JSONDecodeError, OSError, RuntimeError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    except Exception as error:
        validation_error = getattr(locals().get("checker"), "ValidationError", None)
        if validation_error is not None and isinstance(error, validation_error):
            print(f"ERROR: {error}", file=sys.stderr)
            return 1
        raise


if __name__ == "__main__":
    raise SystemExit(main())