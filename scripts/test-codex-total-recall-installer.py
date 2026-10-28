#!/usr/bin/env python3
"""Focused tests for the managed Codex Total Recall runtime installer."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


MODULE_PATH = Path(__file__).with_name("codex_total_recall_installer.py")
SPEC = importlib.util.spec_from_file_location("codex_total_recall_installer", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ManagedRuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(dir=Path.cwd())
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "managed runtime"
        self.source = Path(self.temporary.name) / "codex_total_recall.py"
        self.launcher_source = Path(self.temporary.name) / "codex_total_recall_launcher.py"
        self.source.write_text("print('adapter')\n", encoding="utf-8")
        self.launcher_source.write_text("# stable launcher\n", encoding="utf-8")
        self.runtime = MODULE.ManagedRuntime(
            self.root,
            self.source,
            self.launcher_source,
            sys.executable,
        )

    def test_install_writes_versioned_payload_manifest_and_active_pointer(self) -> None:
        self.runtime.install()

        active = json.loads((self.root / "active.json").read_text(encoding="utf-8"))
        version_dir = self.root / active["version_directory"]
        manifest_path = version_dir / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        adapter = version_dir / "codex_total_recall.py"

        self.assertEqual(manifest["manifest_schema_version"], MODULE.MANIFEST_SCHEMA_VERSION)
        self.assertEqual(manifest["runtime_version"], MODULE.RUNTIME_VERSION)
        self.assertEqual(manifest["minimum_python"], list(MODULE.MINIMUM_PYTHON))
        self.assertEqual(manifest["python_executable"], str(Path(sys.executable).resolve()))
        self.assertEqual(
            manifest["files"]["codex_total_recall.py"],
            hashlib.sha256(adapter.read_bytes()).hexdigest(),
        )
        self.assertEqual(adapter.read_text(encoding="utf-8"), "print('adapter')\n")
        self.assertTrue((self.root / "launcher.py").is_file())
        self.runtime.check_installed()

    def test_same_version_install_is_content_idempotent(self) -> None:
        self.runtime.install()
        before = {
            path.relative_to(self.root): path.read_bytes()
            for path in self.root.rglob("*")
            if path.is_file()
        }

        self.runtime.install()

        after = {
            path.relative_to(self.root): path.read_bytes()
            for path in self.root.rglob("*")
            if path.is_file()
        }
        self.assertEqual(before, after)

    def test_dry_run_does_not_create_runtime_files(self) -> None:
        self.runtime.preview()

        self.assertFalse(self.root.exists())

    def test_health_check_rejects_modified_managed_payload(self) -> None:
        self.runtime.install()
        active = json.loads((self.root / "active.json").read_text(encoding="utf-8"))
        adapter = self.root / active["version_directory"] / "codex_total_recall.py"
        adapter.write_text("print('tampered')\n", encoding="utf-8")

        with self.assertRaisesRegex(MODULE.InstallationError, "hash"):
            self.runtime.check()

    def test_failed_staging_keeps_previous_active_runtime(self) -> None:
        self.runtime.install()
        active_before = (self.root / "active.json").read_bytes()
        self.source.write_text("print('new adapter')\n", encoding="utf-8")

        with patch.object(MODULE.shutil, "copy2", side_effect=OSError("simulated copy failure")):
            with self.assertRaisesRegex(OSError, "simulated copy failure"):
                self.runtime.install()

        self.assertEqual(active_before, (self.root / "active.json").read_bytes())
        self.runtime.check_installed()
        self.assertEqual(
            {path.name for path in (self.root / "staging").iterdir()} if (self.root / "staging").exists() else set(),
            set(),
        )

    def test_modified_stable_launcher_is_not_overwritten(self) -> None:
        self.runtime.install()
        launcher = self.root / "launcher.py"
        launcher.write_text("user change\n", encoding="utf-8")

        with self.assertRaisesRegex(MODULE.InstallationError, "launcher"):
            self.runtime.install()

        self.assertEqual(launcher.read_text(encoding="utf-8"), "user change\n")

    def test_launcher_dispatches_with_canonical_guidance_root(self) -> None:
        marker = Path(self.temporary.name) / "dispatch.json"
        canonical_root = Path(self.temporary.name) / "canonical guidance"
        self.source.write_text(
            "import json, os, sys\n"
            "from pathlib import Path\n"
            "Path(os.environ['ADAPTIVE_TEST_MARKER']).write_text(json.dumps({"
            "'root': os.environ.get('ADAPTIVE_AGENTS_ROOT'), "
            "'arguments': sys.argv[1:]}), encoding='utf-8')\n",
            encoding="utf-8",
        )
        self.runtime = MODULE.ManagedRuntime(
            self.root,
            self.source,
            Path(__file__).with_name("codex_total_recall_launcher.py"),
            sys.executable,
            canonical_root,
        )
        self.runtime.install()
        environment = os.environ.copy()
        environment["ADAPTIVE_TEST_MARKER"] = str(marker)

        result = subprocess.run(
            [sys.executable, str(self.root / "launcher.py"), "session-start", "event.json"],
            check=False,
            capture_output=True,
            text=True,
            env=environment,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        dispatch = json.loads(marker.read_text(encoding="utf-8"))
        self.assertEqual(dispatch["root"], str(canonical_root.resolve()))
        self.assertEqual(dispatch["arguments"], ["session-start", "event.json"])


if __name__ == "__main__":
    unittest.main()
