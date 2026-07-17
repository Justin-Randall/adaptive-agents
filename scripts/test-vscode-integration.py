#!/usr/bin/env python3

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
CHECKER = REPO_ROOT / "scripts" / "check-vscode-integration.py"


class VscodeIntegrationHealthTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory(dir=REPO_ROOT)
        self.root = Path(self.temporary_directory.name)
        self.settings = self.root / "settings.json"
        self.hook = self.root / "adaptive-agents.json"
        self.repo = "C:/Users/test/adaptive-agents"
        self.write_json(
            self.settings,
            {"github.copilot.chat.additionalReadAccessPaths": [self.repo]},
        )
        self.write_json(
            self.hook,
            {
                "hooks": {
                    "SessionStart": [
                        {
                            "type": "command",
                            "command": f'py -3 "{self.repo}/scripts/vscode-session-start.py"',
                            "timeout": 30,
                        }
                    ]
                }
            },
        )

    def tearDown(self):
        self.temporary_directory.cleanup()

    @staticmethod
    def write_json(path, data):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data), encoding="utf-8")

    def run_checker(self, version="1.129.0"):
        return subprocess.run(
            [
                sys.executable,
                str(CHECKER),
                "--settings",
                str(self.settings),
                "--hook",
                str(self.hook),
                "--repo-root",
                self.repo,
                "--version-output",
                version,
            ],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_accepts_valid_hook_native_integration(self):
        result = self.run_checker()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_reports_missing_malformed_and_stale_hooks(self):
        self.hook.unlink()
        result = self.run_checker()
        self.assertIn("hook file is missing", result.stdout)

        self.hook.write_text("{bad", encoding="utf-8")
        result = self.run_checker()
        self.assertIn("could not parse hook", result.stdout)

        self.write_json(
            self.hook,
            {
                "hooks": {
                    "SessionStart": [
                        {
                            "type": "command",
                            "command": 'py -3 "C:/old/scripts/vscode-session-start.py"',
                            "timeout": 30,
                        }
                    ]
                }
            },
        )
        result = self.run_checker()
        self.assertIn("does not invoke the canonical Python adapter", result.stdout)

    def test_reports_disabled_hooks_and_read_grant_drift(self):
        self.write_json(self.settings, {"chat.useHooks": False})
        result = self.run_checker()
        self.assertNotEqual(0, result.returncode)
        self.assertIn("chat.useHooks is false", result.stdout)
        self.assertIn("does not include the repo root", result.stdout)

    def test_reports_installer_owned_legacy_residue(self):
        self.write_json(
            self.settings,
            {
                "github.copilot.chat.additionalReadAccessPaths": [self.repo],
                "chat.instructionsFilesLocations": {f"{self.repo}/vscode": True},
                "chat.tools.terminal.autoApprove": {
                    f'/^bash\\ "{self.repo}/scripts/session\\-start\\.sh"$/': {
                        "approve": True,
                        "matchCommandLine": True,
                    }
                },
            },
        )
        result = self.run_checker()
        self.assertNotEqual(0, result.returncode)
        self.assertIn("legacy instructions registration remains", result.stdout)
        self.assertIn("legacy session-start terminal approval remains", result.stdout)

    def test_reports_unsupported_or_unknown_version(self):
        result = self.run_checker("1.128.2")
        self.assertIn("requires VS Code 1.129.0 or newer", result.stdout)
        result = self.run_checker("unknown")
        self.assertIn("could not parse VS Code version", result.stdout)


if __name__ == "__main__":
    unittest.main()