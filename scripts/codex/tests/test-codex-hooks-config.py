#!/usr/bin/env python3
"""Focused tests for safe Codex Total Recall hook provisioning."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

MODULE_PATH = Path(__file__).resolve().parents[1] / "codex_hooks_config.py"
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
            legacy_script = Path(directory) / "scripts" / "codex" / "codex_total_recall.py"
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

    def test_changed_managed_hook_settings_are_refreshed_on_upgrade(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:
            config = Path(directory) / "hooks.json"
            previous = MODULE.desired_config(
                Path(directory) / "codex_total_recall.py",
                "python",
            )
            previous["hooks"]["SessionStart"][0]["matcher"] = "startup|resume"
            previous["hooks"]["PreCompact"][0]["hooks"][0]["timeout"] = 20
            config.write_text(json.dumps(previous, indent=2) + "\n", encoding="utf-8")
            updated_script = Path(directory) / ".adaptive-agents" / "launcher.py"

            self.assertEqual(
                MODULE.main(
                    [
                        "--config",
                        str(config),
                        "--script",
                        str(updated_script),
                        "--python",
                        "python",
                        "--apply",
                    ]
                ),
                0,
            )

            updated = json.loads(config.read_text(encoding="utf-8"))
            self.assertEqual(updated, MODULE.desired_config(updated_script, "python"))

    def test_inline_user_hooks_are_preserved_and_managed_hooks_migrate_inline(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:
            codex_home = Path(directory)
            toml_config = codex_home / "config.toml"
            hooks_config = codex_home / "hooks.json"
            user_config = (
                'approval_policy = "on-request"\n'
                '\n'
                '[[hooks.SessionStart]]\n'
                'matcher = "startup"\n'
                '[[hooks.SessionStart.hooks]]\n'
                'type = "command"\n'
                'command = "user-session-start"\n'
                'timeout = 5\n'
            )
            toml_config.write_text(user_config, encoding="utf-8")
            legacy_script = codex_home / "scripts" / "codex" / "codex_total_recall.py"
            hooks_config.write_text(
                json.dumps(MODULE.desired_config(legacy_script, "python"), indent=2) + "\n",
                encoding="utf-8",
            )
            managed_launcher = codex_home / ".adaptive-agents" / "launcher.py"

            self.assertEqual(
                MODULE.main(
                    [
                        "--config",
                        str(hooks_config),
                        "--script",
                        str(managed_launcher),
                        "--python",
                        "python",
                        "--toml-config",
                        str(toml_config),
                        "--apply",
                    ]
                ),
                0,
            )

            updated_toml = toml_config.read_text(encoding="utf-8")
            self.assertTrue(updated_toml.startswith(user_config))
            parsed = MODULE.tomllib.loads(updated_toml)
            session_start = parsed["hooks"]["SessionStart"]
            self.assertEqual(session_start[0]["hooks"][0]["command"], "user-session-start")
            self.assertEqual(len(session_start), 2)
            self.assertIn("ADAPTIVE_AGENTS_TOTAL_RECALL_HOOKS", updated_toml)
            self.assertFalse(hooks_config.exists())

            self.assertEqual(
                MODULE.main(
                    [
                        "--config",
                        str(hooks_config),
                        "--script",
                        str(managed_launcher),
                        "--python",
                        "python",
                        "--toml-config",
                        str(toml_config),
                        "--check",
                    ]
                ),
                0,
            )

    def test_inline_user_hooks_without_managed_json_are_preserved(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:
            config = Path(directory) / "config.toml"
            hooks_config = Path(directory) / "hooks.json"
            user_config = (
                '[[hooks.SessionStart]]\n'
                'matcher = "startup"\n'
                '[[hooks.SessionStart.hooks]]\n'
                'type = "command"\n'
                'command = "user-session-start"\n'
            )
            config.write_text(user_config, encoding="utf-8")
            script = Path(directory) / "launcher.py"

            self.assertEqual(
                MODULE.main(
                    [
                        "--config",
                        str(hooks_config),
                        "--script",
                        str(script),
                        "--python",
                        "python",
                        "--toml-config",
                        str(config),
                        "--apply",
                    ]
                ),
                0,
            )

            updated = config.read_text(encoding="utf-8")
            parsed = MODULE.tomllib.loads(updated)
            self.assertTrue(updated.startswith(user_config))
            self.assertEqual(parsed["hooks"]["SessionStart"][0]["hooks"][0]["command"], "user-session-start")
            self.assertFalse(hooks_config.exists())

    def test_malformed_inline_markers_fail_without_mutation(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:
            codex_home = Path(directory)
            toml_config = codex_home / "config.toml"
            hooks_config = codex_home / "hooks.json"
            toml_original = (
                '[[hooks.SessionStart]]\n'
                'matcher = "startup"\n'
                f'{MODULE.INLINE_HOOKS_START}\n'
            )
            managed_hooks = json.dumps(
                MODULE.desired_config(codex_home / "launcher.py", "python"),
                indent=2,
            ) + "\n"
            toml_config.write_text(toml_original, encoding="utf-8")
            hooks_config.write_text(managed_hooks, encoding="utf-8")

            with self.assertRaises(SystemExit):
                MODULE.main(
                    [
                        "--config",
                        str(hooks_config),
                        "--script",
                        str(codex_home / "new-launcher.py"),
                        "--python",
                        "python",
                        "--toml-config",
                        str(toml_config),
                        "--apply",
                    ]
                )

            self.assertEqual(toml_config.read_text(encoding="utf-8"), toml_original)
            self.assertEqual(hooks_config.read_text(encoding="utf-8"), managed_hooks)

    def test_unrecognized_inline_managed_block_fails_without_mutation(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:
            codex_home = Path(directory)
            toml_config = codex_home / "config.toml"
            hooks_config = codex_home / "hooks.json"
            toml_original = (
                '[[hooks.SessionStart]]\n'
                'matcher = "startup"\n'
                '[[hooks.SessionStart.hooks]]\n'
                'type = "command"\n'
                'command = "user-session-start"\n'
                f'{MODULE.INLINE_HOOKS_START}\n'
                '[[hooks.UnknownEvent]]\n'
                '[[hooks.UnknownEvent.hooks]]\n'
                'type = "command"\n'
                'command = "user-managed-looking-hook"\n'
                f'{MODULE.INLINE_HOOKS_END}\n'
            )
            managed_hooks = json.dumps(
                MODULE.desired_config(codex_home / "launcher.py", "python"),
                indent=2,
            ) + "\n"
            toml_config.write_text(toml_original, encoding="utf-8")
            hooks_config.write_text(managed_hooks, encoding="utf-8")

            with self.assertRaises(SystemExit):
                MODULE.main(
                    [
                        "--config",
                        str(hooks_config),
                        "--script",
                        str(codex_home / "new-launcher.py"),
                        "--python",
                        "python",
                        "--toml-config",
                        str(toml_config),
                        "--apply",
                    ]
                )

            self.assertEqual(toml_config.read_text(encoding="utf-8"), toml_original)
            self.assertEqual(hooks_config.read_text(encoding="utf-8"), managed_hooks)

    def test_disabled_hooks_block_installation(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:
            config = Path(directory) / "config.toml"
            config.write_text("[features]\nhooks = false\n", encoding="utf-8")

            with self.assertRaises(SystemExit):
                MODULE.validate_hook_layer(config, Path(directory) / "hooks.json")


if __name__ == "__main__":
    unittest.main()
