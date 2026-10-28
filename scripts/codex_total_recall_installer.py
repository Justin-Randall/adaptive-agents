#!/usr/bin/env python3
"""Install and validate the managed Codex Total Recall runtime."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


RUNTIME_VERSION = "1.0.0"
MANIFEST_SCHEMA_VERSION = 1
MINIMUM_PYTHON = (3, 11)


class InstallationError(RuntimeError):
    """Raised when a managed runtime is missing, conflicting, or invalid."""


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def json_bytes(value: dict[str, Any]) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


class ManagedRuntime:
    def __init__(
        self,
        root: Path,
        adapter_source: Path,
        launcher_source: Path,
        python_executable: str,
        adaptive_agents_root: Path | None = None,
    ) -> None:
        self.root = root.expanduser().resolve()
        self.adapter_source = adapter_source.expanduser().resolve()
        self.launcher_source = launcher_source.expanduser().resolve()
        self.python_executable = str(Path(python_executable).expanduser().resolve())
        self.adaptive_agents_root = (
            adaptive_agents_root.expanduser().resolve()
            if adaptive_agents_root is not None
            else None
        )

    @property
    def active_path(self) -> Path:
        return self.root / "active.json"

    @property
    def launcher_path(self) -> Path:
        return self.root / "launcher.py"

    def _python_info(self, executable: str | None = None) -> dict[str, Any]:
        target = executable or self.python_executable
        try:
            result = subprocess.run(
                [
                    target,
                    "-c",
                    "import json,sys; print(json.dumps({'executable':sys.executable,"
                    "'version':list(sys.version_info[:3])}))",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
        except (OSError, subprocess.CalledProcessError) as exc:
            raise InstallationError(
                f"Python interpreter is unavailable: {target}"
            ) from exc
        try:
            info = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            raise InstallationError("Python interpreter returned invalid version data") from exc
        version = info.get("version")
        if not isinstance(version, list) or len(version) < 2:
            raise InstallationError("Python interpreter returned an invalid version")
        if tuple(version[:2]) < MINIMUM_PYTHON:
            required = ".".join(str(part) for part in MINIMUM_PYTHON)
            actual = ".".join(str(part) for part in version[:3])
            raise InstallationError(f"Python {required}+ is required; found {actual}")
        return info

    def _desired_manifest(self, adapter_digest: str) -> dict[str, Any]:
        manifest: dict[str, Any] = {
            "manifest_schema_version": MANIFEST_SCHEMA_VERSION,
            "runtime_version": RUNTIME_VERSION,
            "minimum_python": list(MINIMUM_PYTHON),
            "python_executable": self.python_executable,
            "files": {"codex_total_recall.py": adapter_digest},
        }
        if self.adaptive_agents_root is not None:
            manifest["adaptive_agents_root"] = str(self.adaptive_agents_root)
        return manifest

    def _version_directory(self, manifest: dict[str, Any]) -> Path:
        manifest_digest = sha256_bytes(json_bytes(manifest))
        return self.root / "versions" / f"{RUNTIME_VERSION}-{manifest_digest[:16]}"

    def _read_json(self, path: Path, label: str) -> dict[str, Any]:
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise InstallationError(f"{label} is missing or invalid: {path}") from exc
        if not isinstance(value, dict):
            raise InstallationError(f"{label} must contain a JSON object: {path}")
        return value

    def _read_active(self) -> tuple[dict[str, Any], dict[str, Any], Path]:
        active = self._read_json(self.active_path, "active runtime pointer")
        if active.get("manifest_schema_version") != MANIFEST_SCHEMA_VERSION:
            raise InstallationError("unsupported active runtime pointer schema")
        version_directory = active.get("version_directory")
        if not isinstance(version_directory, str):
            raise InstallationError("active runtime pointer has no version directory")
        versions_root = (self.root / "versions").resolve()
        payload = (self.root / version_directory).resolve()
        if payload.parent != versions_root or not payload.is_dir():
            raise InstallationError("active runtime pointer escapes the managed versions directory")
        manifest_path = payload / "manifest.json"
        manifest_bytes = manifest_path.read_bytes()
        if sha256_bytes(manifest_bytes) != active.get("manifest_sha256"):
            raise InstallationError("managed runtime manifest hash does not match active pointer")
        manifest = self._read_json(manifest_path, "runtime manifest")
        return active, manifest, payload

    def _validate_owned_state(self) -> tuple[dict[str, Any], dict[str, Any], Path] | None:
        active_exists = self.active_path.exists()
        launcher_exists = self.launcher_path.exists()
        if not active_exists:
            if launcher_exists:
                raise InstallationError(
                    f"unmanaged launcher already exists; preserve it and resolve manually: {self.launcher_path}"
                )
            return None

        active, manifest, payload = self._read_active()
        if manifest.get("manifest_schema_version") != MANIFEST_SCHEMA_VERSION:
            raise InstallationError("unsupported managed runtime manifest schema")
        files = manifest.get("files")
        if not isinstance(files, dict) or not files:
            raise InstallationError("managed runtime manifest has no file hashes")
        for relative, expected_hash in files.items():
            if not isinstance(relative, str) or Path(relative).name != relative:
                raise InstallationError("managed runtime manifest contains an unsafe file path")
            managed_file = payload / relative
            if not managed_file.is_file() or sha256_file(managed_file) != expected_hash:
                raise InstallationError(f"managed runtime file hash mismatch: {managed_file}")
        if not launcher_exists or sha256_file(self.launcher_path) != active.get("launcher_sha256"):
            raise InstallationError("managed runtime launcher is missing or modified")
        return active, manifest, payload

    def preflight(self) -> dict[str, Any]:
        self._python_info()
        for source, label in (
            (self.adapter_source, "Total Recall adapter"),
            (self.launcher_source, "Total Recall launcher source"),
        ):
            if not source.is_file():
                raise InstallationError(f"{label} is missing: {source}")
        adapter_digest = sha256_file(self.adapter_source)
        launcher_digest = sha256_file(self.launcher_source)
        current = self._validate_owned_state()
        manifest = self._desired_manifest(adapter_digest)
        final_directory = self._version_directory(manifest)
        if final_directory.exists() and not (final_directory / "manifest.json").is_file():
            raise InstallationError(
                f"unmanaged runtime directory conflicts with this install: {final_directory}"
            )
        if current is None and self.launcher_path.exists():
            raise InstallationError("managed launcher exists without an active runtime pointer")
        return {
            "adapter_hash": adapter_digest,
            "launcher_hash": launcher_digest,
            "manifest": manifest,
            "version_directory": final_directory,
            "current": current,
        }

    def preview(self) -> str:
        plan = self.preflight()
        current = plan["current"]
        if current is not None and current[0].get("version_directory") == str(
            plan["version_directory"].relative_to(self.root)
        ) and current[0].get("launcher_sha256") == plan["launcher_hash"]:
            return f"Managed Total Recall runtime is current at {self.root}"
        action = "upgrade" if current is not None else "install"
        return f"Would {action} managed Total Recall runtime at {self.root}"

    def check_installed(self) -> None:
        current = self._validate_owned_state()
        if current is None:
            raise InstallationError(f"managed Total Recall runtime is missing: {self.root}")
        active, manifest, _ = current
        interpreter = manifest.get("python_executable")
        if not isinstance(interpreter, str):
            raise InstallationError("managed runtime manifest has no Python interpreter")
        self._python_info(interpreter)
        if active.get("runtime_version") != manifest.get("runtime_version"):
            raise InstallationError("active runtime version does not match its manifest")

    def check(self) -> None:
        self.check_installed()
        plan = self.preflight()
        current = plan["current"]
        if current is None:
            raise InstallationError(f"managed Total Recall runtime is missing: {self.root}")
        active, manifest, _ = current
        expected_directory = str(plan["version_directory"].relative_to(self.root))
        if active.get("version_directory") != expected_directory:
            raise InstallationError("managed Total Recall runtime is stale; rerun the installer")
        if manifest != plan["manifest"]:
            raise InstallationError("managed Total Recall manifest is stale; rerun the installer")
        if active.get("launcher_sha256") != plan["launcher_hash"]:
            raise InstallationError("managed Total Recall launcher source changed; rerun the installer")

    def install(self) -> None:
        plan = self.preflight()
        adapter_digest = plan["adapter_hash"]
        launcher_digest = plan["launcher_hash"]
        manifest = plan["manifest"]
        version_directory: Path = plan["version_directory"]
        old_active = self.active_path.read_bytes() if self.active_path.exists() else None
        old_launcher = self.launcher_path.read_bytes() if self.launcher_path.exists() else None
        created_version = False
        stage: Path | None = None
        try:
            self.root.mkdir(parents=True, exist_ok=True)
            versions = self.root / "versions"
            versions.mkdir(exist_ok=True)
            if not version_directory.exists():
                stage = Path(tempfile.mkdtemp(prefix=".staging-", dir=versions))
                shutil.copy2(self.adapter_source, stage / "codex_total_recall.py")
                if sha256_file(stage / "codex_total_recall.py") != adapter_digest:
                    raise InstallationError("staged Total Recall adapter failed hash verification")
                atomic_write(stage / "manifest.json", json_bytes(manifest))
                os.replace(stage, version_directory)
                stage = None
                created_version = True
            else:
                existing_manifest = self._read_json(
                    version_directory / "manifest.json",
                    "existing runtime manifest",
                )
                existing_adapter = version_directory / "codex_total_recall.py"
                if (
                    existing_manifest != manifest
                    or not existing_adapter.is_file()
                    or sha256_file(existing_adapter) != adapter_digest
                ):
                    raise InstallationError(
                        f"existing runtime version directory is not safely managed: {version_directory}"
                    )

            if old_launcher is None or sha256_bytes(old_launcher) != launcher_digest:
                atomic_write(self.launcher_path, self.launcher_source.read_bytes())
            active = {
                "manifest_schema_version": MANIFEST_SCHEMA_VERSION,
                "runtime_version": RUNTIME_VERSION,
                "version_directory": str(version_directory.relative_to(self.root)),
                "manifest_sha256": sha256_file(version_directory / "manifest.json"),
                "launcher_sha256": launcher_digest,
            }
            atomic_write(self.active_path, json_bytes(active))
            self.check()
        except Exception:
            if old_active is None:
                self.active_path.unlink(missing_ok=True)
            else:
                atomic_write(self.active_path, old_active)
            if old_launcher is None:
                self.launcher_path.unlink(missing_ok=True)
            else:
                atomic_write(self.launcher_path, old_launcher)
            if created_version:
                shutil.rmtree(version_directory, ignore_errors=True)
            raise
        finally:
            if stage is not None:
                shutil.rmtree(stage, ignore_errors=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime-root", required=True, type=Path)
    parser.add_argument("--adapter-source", required=True, type=Path)
    parser.add_argument("--launcher-source", required=True, type=Path)
    parser.add_argument("--python-executable", required=True)
    parser.add_argument("--adaptive-agents-root", type=Path)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    runtime = ManagedRuntime(
        args.runtime_root,
        args.adapter_source,
        args.launcher_source,
        args.python_executable,
        args.adaptive_agents_root,
    )
    try:
        if args.check:
            runtime.check()
            print(f"Managed Total Recall runtime is healthy: {runtime.root}")
        elif args.apply:
            runtime.install()
            print(f"Installed managed Total Recall runtime: {runtime.root}")
        else:
            print(runtime.preview())
    except InstallationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
