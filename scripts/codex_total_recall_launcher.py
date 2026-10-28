#!/usr/bin/env python3
"""Stable entrypoint that dispatches Codex hooks to the active managed runtime."""

from __future__ import annotations

import hashlib
import json
import os
import runpy
import sys
from pathlib import Path
from typing import Any


MANIFEST_SCHEMA_VERSION = 1


def read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"{label} is missing or invalid: {path}") from exc
    if not isinstance(value, dict):
        raise RuntimeError(f"{label} must contain a JSON object: {path}")
    return value


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def dispatch() -> None:
    root = Path(__file__).resolve().parent
    active = read_json(root / "active.json", "active runtime pointer")
    if active.get("manifest_schema_version") != MANIFEST_SCHEMA_VERSION:
        raise RuntimeError("unsupported active runtime pointer schema")
    version_directory = active.get("version_directory")
    if not isinstance(version_directory, str):
        raise RuntimeError("active runtime pointer has no version directory")
    versions_root = (root / "versions").resolve()
    payload = (root / version_directory).resolve()
    if payload.parent != versions_root:
        raise RuntimeError("active runtime pointer escapes the managed versions directory")
    manifest_path = payload / "manifest.json"
    manifest_bytes = manifest_path.read_bytes()
    if sha256_bytes(manifest_bytes) != active.get("manifest_sha256"):
        raise RuntimeError("managed runtime manifest hash does not match active pointer")
    manifest = read_json(manifest_path, "runtime manifest")
    minimum_python = manifest.get("minimum_python")
    if not isinstance(minimum_python, list) or tuple(sys.version_info[:2]) < tuple(minimum_python[:2]):
        raise RuntimeError("the managed Total Recall runtime requires a newer Python interpreter")
    expected_interpreter = manifest.get("python_executable")
    if (
        not isinstance(expected_interpreter, str)
        or os.path.normcase(str(Path(sys.executable).resolve()))
        != os.path.normcase(str(Path(expected_interpreter).resolve()))
    ):
        raise RuntimeError("Codex launched the managed runtime with an unexpected Python interpreter")

    files = manifest.get("files")
    if not isinstance(files, dict):
        raise RuntimeError("managed runtime manifest has no file hashes")
    for relative, expected_hash in files.items():
        if not isinstance(relative, str) or Path(relative).name != relative:
            raise RuntimeError("managed runtime manifest contains an unsafe file path")
        path = payload / relative
        if not path.is_file() or sha256_bytes(path.read_bytes()) != expected_hash:
            raise RuntimeError(f"managed runtime file hash mismatch: {path}")
    adapter = payload / "codex_total_recall.py"
    if not adapter.is_file():
        raise RuntimeError("managed Total Recall adapter is missing")

    agents_root = manifest.get("adaptive_agents_root")
    if isinstance(agents_root, str):
        os.environ["ADAPTIVE_AGENTS_ROOT"] = agents_root
    runpy.run_path(str(adapter), run_name="__main__")


if __name__ == "__main__":
    try:
        dispatch()
    except (OSError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
