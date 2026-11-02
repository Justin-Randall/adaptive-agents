#!/usr/bin/env python3
"""Retired JSONL repair must fail explicitly without touching evidence."""

import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location("recovery", Path(__file__).with_name("recover-codex-total-recall.py"))
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class RecoveryDeprecationTests(unittest.TestCase):
    def test_retired_recovery_rejects_preview_and_apply_without_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            ledger, transcript = root / "ledger.jsonl", root / "native.jsonl"
            for path in (ledger, transcript):
                path.write_bytes(b'{"historical":"evidence"}\n')
            before = {p: p.read_bytes() for p in root.iterdir()}
            for apply in (False, True):
                with self.assertRaisesRegex(ValueError, "deprecated"):
                    MODULE.recover(root, transcript, apply=apply)
            result = subprocess.run(
                [sys.executable, MODULE.__file__, "--session", str(root), "--transcript", str(transcript), "--apply"],
                capture_output=True, timeout=30)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(b"deprecated", result.stderr)
            self.assertEqual(before, {p: p.read_bytes() for p in root.iterdir()})


if __name__ == "__main__":
    unittest.main()
