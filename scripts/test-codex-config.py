#!/usr/bin/env python3
"""Focused tests for merging the Codex permission contract."""

from __future__ import annotations

import importlib.util
import tempfile
import tomllib
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("codex_config.py")
SPEC = importlib.util.spec_from_file_location("codex_config", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class CodexPermissionConfigTests(unittest.TestCase):
    def test_transform_adds_repository_and_session_roots_without_losing_comments(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:
            repo = Path(directory) / "repo"
            sessions = Path(directory) / "user data" / "sessions"
            raw = (
                'approval_policy = "on-request"\n\n'
                "[sandbox_workspace_write]\n"
                "# Preserve the existing user root.\n"
                'writable_roots = ["C:/user/root"]\n'
            )

            updated = MODULE.transform(raw, repo, extra_roots=(sessions,))
            parsed = tomllib.loads(updated)

            self.assertEqual(
                parsed["sandbox_workspace_write"]["writable_roots"],
                [
                    "C:/user/root",
                    repo.resolve().as_posix(),
                    sessions.resolve().as_posix(),
                ],
            )
            self.assertIn("# Preserve the existing user root.", updated)
            self.assertEqual(
                MODULE.transform(updated, repo, extra_roots=(sessions,)),
                updated,
            )

    def test_transform_adds_both_managed_roots_to_a_new_config(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:
            repo = Path(directory) / "repo"
            sessions = Path(directory) / "sessions"

            updated = MODULE.transform("", repo, extra_roots=(sessions,))

            self.assertEqual(
                tomllib.loads(updated)["sandbox_workspace_write"]["writable_roots"],
                [repo.resolve().as_posix(), sessions.resolve().as_posix()],
            )


if __name__ == "__main__":
    unittest.main()
