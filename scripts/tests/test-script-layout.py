#!/usr/bin/env python3
"""Compatibility checks for the indexed scripts tree."""

import importlib.util
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"


class ScriptLayoutTests(unittest.TestCase):
    def test_application_implementations_and_tests_are_grouped(self) -> None:
        for path in (
            "codex/codex_total_recall.py",
            "codex/codex_total_recall_installer.py",
            "codex/tests/test-codex-total-recall.py",
            "codex/tests/test-install-codex.sh",
            "vscode/session_start.py",
            "vscode/integration.py",
            "vscode/tests/test-vscode-session-start.py",
            "browser/markdown_browser.py",
            "tests/test-project-layer.sh",
        ):
            with self.subTest(path=path):
                self.assertTrue(SCRIPTS.joinpath(*path.split("/")).is_file())
        self.assertEqual({path.name for path in SCRIPTS.glob("test-*")},
                         {"test-opencode.sh", "test-install-antigravity.sh", "test-project-layer.sh"})
        self.assertEqual(list(SCRIPTS.glob("codex_*.py")), [])

    def test_public_python_entrypoints_work_outside_the_checkout(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            for name in ("ui.py", "vscode-session-start.py", "check-vscode-integration.py"):
                with self.subTest(name=name):
                    result = subprocess.run(
                        [sys.executable, str(SCRIPTS / name), "--help"],
                        cwd=directory, capture_output=True, timeout=30)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertIn(b"usage:", result.stdout)

    def test_application_sources_are_not_ignored(self) -> None:
        result = subprocess.run(
            ["git", "check-ignore", "--no-index",
             "scripts/codex/codex_total_recall.py", "scripts/vscode/session_start.py",
             "scripts/browser/markdown_browser.py", "scripts/tests/test-script-layout.py"],
            cwd=ROOT, capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)

    def test_browser_and_legacy_bridge_keep_the_canonical_root(self) -> None:
        for name in ("ui.py", "markdown_browser.py"):
            with self.subTest(name=name):
                module = runpy.run_path(str(SCRIPTS / name))
                self.assertEqual(module["SYSTEM_ROOT"], ROOT)
                self.assertEqual(module["BrowserConfig"].create().system_root, ROOT)

    def test_vscode_hook_keeps_its_default_root_and_budget_checker(self) -> None:
        spec = importlib.util.spec_from_file_location(
            "layout_vscode_hook", SCRIPTS / "vscode" / "session_start.py")
        self.assertIsNotNone(spec)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with patch.object(sys, "argv", ["vscode-session-start.py"]):
            self.assertEqual(module.parse_args().repo_root, ROOT)
        self.assertTrue(callable(module.load_budget_checker().build_baseline))


if __name__ == "__main__":
    unittest.main()
