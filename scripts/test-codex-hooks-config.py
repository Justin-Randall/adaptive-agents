#!/usr/bin/env python3
"""Focused tests for safe Codex Total Recall hook provisioning."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("codex_hooks_config.py")
SPEC = importlib.util.spec_from_file_location("codex_hooks_config", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class HookConfigTests(unittest.TestCase):
    def test_new_config_is_deterministic_and_idempotent(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:
            config = Path(directory) / "hooks.json"
            script = Path(directory) / "codex_total_recall.py"
            self.assertEqual(MODULE.main(["--config", str(config), "--script", str(script), "--python", "python", "--apply"]), 0)
            first = config.read_text(encoding="utf-8")
            generated = json.loads(first)
            windows_commands = {
                hook["commandWindows"]
                for entries in generated["hooks"].values()
                for entry in entries
                for hook in entry["hooks"]
                if "commandWindows" in hook
            }
            self.assertTrue(windows_commands)
            self.assertTrue(all(not command.startswith('"') for command in windows_commands))
            self.assertEqual(MODULE.main(["--config", str(config), "--script", str(script), "--python", "python", "--apply"]), 0)
            self.assertEqual(first, config.read_text(encoding="utf-8"))

    def test_unrelated_existing_hooks_are_not_overwritten(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:
            config = Path(directory) / "hooks.json"
            original = '{"description":"user hooks","hooks":{}}\n'
            config.write_text(original, encoding="utf-8")
            with self.assertRaises(SystemExit):
                MODULE.main(["--config", str(config), "--script", str(Path(directory) / "script.py"), "--python", "python", "--apply"])
            self.assertEqual(original, config.read_text(encoding="utf-8"))

    def test_extra_hooks_in_managed_file_fail_without_mutation(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:
            config = Path(directory) / "hooks.json"
            original_config = MODULE.desired_config(
                Path(directory) / "codex_total_recall.py",
                "python",
            )
            original_config["hooks"]["Stop"].append(
                {
                    "hooks": [
                        {
                            "type": "command",
                            "command": "user-hook",
                            "timeout": 5,
                        }
                    ]
                }
            )
            original = json.dumps(original_config, indent=2) + "\n"
            config.write_text(original, encoding="utf-8")

            with self.assertRaises(SystemExit):
                MODULE.main(
                    [
                        "--config",
                        str(config),
                        "--script",
                        str(Path(directory) / "new_adapter.py"),
                        "--python",
                        "python",
                        "--apply",
                    ]
                )

            self.assertEqual(original, config.read_text(encoding="utf-8"))

    def test_foundation_hook_config_migrates_to_managed_launcher(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:
            config = Path(directory) / "hooks.json"
            legacy_script = Path(directory) / "scripts" / "codex_total_recall.py"
            managed_launcher = Path(directory) / ".adaptive-agents" / "codex" / "launcher.py"
            original = json.dumps(
                MODULE.desired_config(legacy_script, "python"),
                indent=2,
            ) + "\n"
            config.write_text(original, encoding="utf-8")

            self.assertEqual(
                MODULE.main(
                    [
                        "--config",
                        str(config),
                        "--script",
                        str(managed_launcher),
                        "--python",
                        "python",
                        "--apply",
                    ]
                ),
                0,
            )

            migrated = json.loads(config.read_text(encoding="utf-8"))
            command = migrated["hooks"]["SessionStart"][0]["hooks"][0]["command"]
            self.assertIn(str(managed_launcher.resolve()), command)
            self.assertNotIn(str(legacy_script.resolve()), command)

    def test_inline_user_hooks_block_hooks_json_installation(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:
            config = Path(directory) / "config.toml"
            config.write_text(
                '[[hooks.SessionStart]]\nmatcher = "startup"\n',
                encoding="utf-8",
            )

            with self.assertRaises(SystemExit):
                MODULE.validate_hook_layer(config, Path(directory) / "hooks.json")

    def test_disabled_hooks_block_installation(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:
            config = Path(directory) / "config.toml"
            config.write_text("[features]\nhooks = false\n", encoding="utf-8")

            with self.assertRaises(SystemExit):
                MODULE.validate_hook_layer(config, Path(directory) / "hooks.json")


if __name__ == "__main__":
    unittest.main()
