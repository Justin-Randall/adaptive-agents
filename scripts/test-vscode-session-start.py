#!/usr/bin/env python3

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
ADAPTER = REPO_ROOT / "scripts" / "vscode-session-start.py"


class VscodeSessionStartTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory(dir=REPO_ROOT)
        self.root = Path(self.temporary_directory.name)
        self.write_text("AGENTS.md", "agent rules\n")
        self.write_text("INDEX.md", "routing index\n")
        self.write_text("instructions/global.instructions.md", "global guidance\n")
        self.write_manifest()
        self.runner = self.root / "session-start.sh"
        self.status_file = self.root / "status" / "vscode-session-start-status.json"
        self.write_runner("")

    def tearDown(self):
        self.temporary_directory.cleanup()

    def write_text(self, relative_path, content):
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def write_manifest(self, *, limit=32768):
        manifest = {
            "schemaVersion": 1,
            "metricVersion": 1,
            "highWaterEstimatedTokens": 32768,
            "warningEstimatedTokens": 26215,
            "profiles": [
                {
                    "name": "startup",
                    "extends": [],
                    "maxEstimatedTokens": limit,
                    "maxGrowthEstimatedTokens": None,
                    "files": [
                        {
                            "path": "AGENTS.md",
                            "classification": "always",
                            "reason": "test entrypoint",
                        },
                        {
                            "path": "INDEX.md",
                            "classification": "always",
                            "reason": "test router",
                        },
                    ],
                },
                {
                    "name": "non_trivial_coding",
                    "extends": ["startup"],
                    "maxEstimatedTokens": limit,
                    "maxGrowthEstimatedTokens": None,
                    "files": [
                        {
                            "path": "INDEX.md",
                            "classification": "profile",
                            "reason": "test deduplication",
                        },
                        {
                            "path": "instructions/global.instructions.md",
                            "classification": "profile",
                            "reason": "test guidance",
                        },
                    ],
                },
            ],
        }
        self.write_text("instruction-load-routes.json", json.dumps(manifest))

    def write_runner(self, output, *, exit_code=0):
        escaped_output = output.replace("'", "'\\''")
        script = "#!/usr/bin/env bash\n"
        if output:
            script += f"printf '%s' '{escaped_output}'\n"
        script += f"exit {exit_code}\n"
        self.runner.write_text(script, encoding="utf-8")

    def run_adapter(self, stdin=None):
        return subprocess.run(
            [
                sys.executable,
                str(ADAPTER),
                "--repo-root",
                str(self.root),
                "--runner",
                str(self.runner),
                "--status-file",
                str(self.status_file),
            ],
            input=stdin or json.dumps({"hookEventName": "SessionStart"}),
            capture_output=True,
            text=True,
            check=False,
        )

    def test_injects_resolved_profile_once_in_declared_order(self):
        result = self.run_adapter()
        self.assertEqual(0, result.returncode, result.stderr)
        payload = json.loads(result.stdout)
        context = payload["hookSpecificOutput"]["additionalContext"]
        self.assertEqual("SessionStart", payload["hookSpecificOutput"]["hookEventName"])
        self.assertIn("startup has already run", context)
        self.assertIn(f"Canonical Adaptive Agents repository: {self.root.as_posix()}", context)
        boundaries = [
            "--- FILE: AGENTS.md ---",
            "--- FILE: INDEX.md ---",
            "--- FILE: instructions/global.instructions.md ---",
        ]
        self.assertEqual(sorted(context.index(item) for item in boundaries), [context.index(item) for item in boundaries])
        self.assertEqual(1, context.count("--- FILE: INDEX.md ---"))
        self.assertIn("agent rules", context)
        self.assertIn("global guidance", context)

    def test_omits_dynamic_section_when_runner_is_silent(self):
        result = self.run_adapter()
        self.assertEqual(0, result.returncode, result.stderr)
        context = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
        self.assertNotIn("DYNAMIC STARTUP OUTPUT", context)

    def test_writes_success_status_after_context_and_runner_complete(self):
        result = self.run_adapter()
        self.assertEqual(0, result.returncode, result.stderr)
        status = json.loads(self.status_file.read_text(encoding="utf-8"))
        self.assertEqual(1, status["schemaVersion"])
        self.assertEqual("SessionStart", status["hookEventName"])
        self.assertEqual(self.root.as_posix(), status["repoRoot"])
        self.assertEqual(3, status["filesLoaded"])
        self.assertFalse(status["dynamicOutput"])
        self.assertRegex(status["completedAt"], r"^\d{4}-\d{2}-\d{2}T.*Z$")

    def test_preserves_structured_runner_output_and_json_encoding(self):
        runner_output = '--- PROMPT\nSay "hello"\n--- ON APPROVE\nrun next\n'
        self.write_runner(runner_output)
        result = self.run_adapter()
        self.assertEqual(0, result.returncode, result.stderr)
        context = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
        self.assertIn("--- DYNAMIC STARTUP OUTPUT ---\n" + runner_output.rstrip(), context)

    def test_rejects_malformed_manifest(self):
        self.write_text("instruction-load-routes.json", "{not json")
        result = self.run_adapter()
        self.assertNotEqual(0, result.returncode)
        self.assertIn("route manifest", result.stderr)
        self.assertEqual("", result.stdout)

    def test_rejects_missing_required_file(self):
        (self.root / "INDEX.md").unlink()
        result = self.run_adapter()
        self.assertNotEqual(0, result.returncode)
        self.assertIn("missing counted file", result.stderr)

    def test_rejects_profile_over_budget(self):
        self.write_text("AGENTS.md", "x" * 132000)
        result = self.run_adapter()
        self.assertNotEqual(0, result.returncode)
        self.assertIn("exceeds profile limit", result.stderr)

    def test_surfaces_runner_failure_without_success_payload(self):
        self.write_runner("probe failed", exit_code=7)
        result = self.run_adapter()
        self.assertNotEqual(0, result.returncode)
        self.assertIn("session-start runner failed with exit code 7", result.stderr)
        self.assertEqual("", result.stdout)
        self.assertFalse(self.status_file.exists())


if __name__ == "__main__":
    unittest.main()