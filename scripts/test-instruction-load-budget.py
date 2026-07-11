#!/usr/bin/env python3

import importlib.util
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


sys.dont_write_bytecode = True

REPO_ROOT = Path(__file__).resolve().parent.parent
CHECKER_PATH = REPO_ROOT / "scripts" / "check-instruction-load-budget.py"
WRAPPER_PATH = REPO_ROOT / "scripts" / "check-instruction-load-budget.sh"


def load_checker():
    spec = importlib.util.spec_from_file_location("instruction_load_budget", CHECKER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


checker = load_checker()


class InstructionLoadBudgetTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        (self.root / "scripts").mkdir()
        self.write_text("AGENTS.md", "alpha beta\n")

    def tearDown(self):
        self.temp_dir.cleanup()

    def write_text(self, relative_path, text, newline=""):
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline=newline)
        return path

    def write_bytes(self, relative_path, content):
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return path

    def manifest(self, profiles=None, warning=26_215, high_water=32_768):
        return {
            "schemaVersion": 1,
            "metricVersion": 1,
            "highWaterEstimatedTokens": high_water,
            "warningEstimatedTokens": warning,
            "profiles": profiles
            or [
                {
                    "name": "startup",
                    "extends": [],
                    "maxEstimatedTokens": high_water,
                    "maxGrowthEstimatedTokens": None,
                    "files": [
                        {
                            "path": "AGENTS.md",
                            "classification": "always",
                            "reason": "Canonical entrypoint requires INDEX routing.",
                        }
                    ],
                }
            ],
        }

    def write_manifest(self, manifest=None):
        path = self.root / "instruction-load-routes.json"
        path.write_text(
            json.dumps(manifest or self.manifest(), indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        return path

    def run_checker(self, *args):
        stdout = io.StringIO()
        stderr = io.StringIO()
        exit_code = checker.run(list(args), repo_root=self.root, stdout=stdout, stderr=stderr)
        return exit_code, stdout.getvalue(), stderr.getvalue()

    def establish_baseline(self, manifest=None):
        self.write_manifest(manifest)
        exit_code, _, stderr = self.run_checker("--update-baseline")
        self.assertEqual(0, exit_code, stderr)
        return (self.root / "instruction-load-baseline.json").read_bytes()

    def test_metric_arithmetic_handles_zero_and_odd_values(self):
        self.assertEqual(0, checker.ceil_word_estimate(0))
        self.assertEqual(2, checker.ceil_word_estimate(1))
        self.assertEqual(5, checker.ceil_word_estimate(3))
        self.assertEqual(0, checker.ceil_character_estimate(0))
        self.assertEqual(1, checker.ceil_character_estimate(1))
        self.assertEqual(2, checker.ceil_character_estimate(5))

    def test_lf_and_crlf_have_identical_metrics_and_hashes(self):
        lf = checker.measure_bytes(b"alpha beta\ngamma\n", "fixture.md")
        crlf = checker.measure_bytes(b"alpha beta\r\ngamma\r\n", "fixture.md")
        self.assertEqual(lf, crlf)

    def test_profile_inheritance_preserves_order_and_deduplicates(self):
        self.write_text("INDEX.md", "index\n")
        profiles = [
            {
                "name": "startup",
                "extends": [],
                "files": [self.entry("AGENTS.md"), self.entry("INDEX.md")],
            },
            {
                "name": "coding",
                "extends": ["startup"],
                "files": [self.entry("INDEX.md"), self.entry("AGENTS.md")],
            },
        ]
        expanded = checker.validate_and_expand_manifest(self.manifest(profiles), self.root)
        self.assertEqual(["AGENTS.md", "INDEX.md"], [item["path"] for item in expanded[1]["files"]])

    def test_profile_inheritance_cycle_is_rejected(self):
        profiles = [
            {"name": "one", "extends": ["two"], "files": []},
            {"name": "two", "extends": ["one"], "files": []},
        ]
        with self.assertRaisesRegex(checker.ValidationError, "cycle"):
            checker.validate_and_expand_manifest(self.manifest(profiles), self.root)

    def test_unsafe_paths_are_rejected(self):
        unsafe_paths = [
            "../outside.md",
            "/absolute.md",
            "C:/drive.md",
            "folder\\file.md",
            "*.md",
            "https://example.test/file.md",
        ]
        for unsafe_path in unsafe_paths:
            with self.subTest(path=unsafe_path):
                profiles = [{"name": "unsafe", "extends": [], "files": [self.entry(unsafe_path)]}]
                with self.assertRaises(checker.ValidationError):
                    checker.validate_and_expand_manifest(self.manifest(profiles), self.root)

    def test_unknown_classification_is_rejected(self):
        entry = self.entry("AGENTS.md")
        entry["classification"] = "sometimes"
        profiles = [{"name": "bad", "extends": [], "files": [entry]}]
        with self.assertRaisesRegex(checker.ValidationError, "classification"):
            checker.validate_and_expand_manifest(self.manifest(profiles), self.root)

    def test_malformed_manifest_is_rejected(self):
        manifest = self.manifest()
        del manifest["metricVersion"]
        with self.assertRaisesRegex(checker.ValidationError, "metricVersion"):
            checker.validate_and_expand_manifest(manifest, self.root)

    def test_unknown_manifest_property_is_rejected(self):
        manifest = self.manifest()
        manifest["unexpected"] = True
        with self.assertRaisesRegex(checker.ValidationError, "unexpected"):
            checker.validate_and_expand_manifest(manifest, self.root)

    def test_strict_utf8_failure_names_the_file(self):
        self.write_bytes("AGENTS.md", b"\xff")
        self.write_manifest()
        exit_code, _, stderr = self.run_checker("--report")
        self.assertEqual(1, exit_code)
        self.assertIn("AGENTS.md", stderr)
        self.assertIn("UTF-8", stderr)

    def test_missing_counted_file_fails(self):
        profiles = [{"name": "startup", "extends": [], "files": [self.entry("MISSING.md")]}]
        self.write_manifest(self.manifest(profiles))
        exit_code, _, stderr = self.run_checker("--report")
        self.assertEqual(1, exit_code)
        self.assertIn("MISSING.md", stderr)

    def test_content_growth_makes_baseline_stale(self):
        self.establish_baseline()
        self.write_text("AGENTS.md", "alpha beta gamma\n")
        exit_code, _, stderr = self.run_checker("--check")
        self.assertEqual(1, exit_code)
        self.assertIn("stale baseline", stderr.lower())
        self.assertIn("delta", stderr.lower())

    def test_same_size_content_change_makes_hash_stale(self):
        self.establish_baseline()
        self.write_text("AGENTS.md", "omega zeta\n")
        exit_code, _, stderr = self.run_checker("--check")
        self.assertEqual(1, exit_code)
        self.assertIn("sha256", stderr)

    def test_malformed_committed_baseline_is_rejected(self):
        self.establish_baseline()
        path = self.root / "instruction-load-baseline.json"
        baseline = json.loads(path.read_text(encoding="utf-8"))
        del baseline["profiles"][0]["totals"]
        path.write_text(json.dumps(baseline), encoding="utf-8")
        exit_code, _, stderr = self.run_checker("--check")
        self.assertEqual(1, exit_code)
        self.assertIn("baseline profile startup is missing totals", stderr)

    def test_warning_boundary(self):
        self.write_text("AGENTS.md", "x" * (26_215 * 4 - 3))
        self.establish_baseline()
        exit_code, stdout, stderr = self.run_checker("--check")
        self.assertEqual(0, exit_code, stderr)
        self.assertIn("WARN: profile startup", stdout)
        self.assertIn("26215", stdout)

    def test_value_below_warning_boundary_does_not_warn(self):
        self.write_text("AGENTS.md", "x" * (26_214 * 4 - 3))
        self.establish_baseline()
        exit_code, stdout, stderr = self.run_checker("--check")
        self.assertEqual(0, exit_code, stderr)
        self.assertNotIn("WARN:", stdout)

    def test_hard_limit_boundary_passes_and_next_value_fails(self):
        self.write_text("AGENTS.md", "x" * (32_768 * 4 - 3))
        self.write_manifest()
        exit_code, _, stderr = self.run_checker("--update-baseline")
        self.assertEqual(0, exit_code, stderr)

        self.write_text("AGENTS.md", "x" * (32_769 * 4 - 3))
        exit_code, _, stderr = self.run_checker("--update-baseline")
        self.assertEqual(1, exit_code)
        self.assertIn("32769", stderr)
        self.assertIn("32768", stderr)

    def test_default_mode_reports_estimated_tokens_against_high_water_and_passes(self):
        self.write_manifest()
        exit_code, stdout, stderr = self.run_checker()
        self.assertEqual(0, exit_code, stderr)
        self.assertIn("STARTUP PASS:", stdout)
        self.assertIn("used=3 estimated tokens", stdout)
        self.assertIn("limit=32,768", stdout)
        self.assertIn("remaining=32,765", stdout)

    def test_default_mode_fails_when_profile_exceeds_high_water(self):
        self.write_text("AGENTS.md", "x" * (32_769 * 4 - 3))
        self.write_manifest()
        exit_code, stdout, stderr = self.run_checker()
        self.assertEqual(1, exit_code, stderr)
        self.assertIn("STARTUP FAIL:", stdout)
        self.assertIn("used=32,769 estimated tokens", stdout)
        self.assertIn("limit=32,768", stdout)
        self.assertIn("remaining=-1", stdout)

    def test_default_mode_reports_only_static_startup_cost(self):
        self.write_text("ACTIVE.md", "x" * (32_769 * 4 - 3))
        profiles = [
            {
                "name": "startup",
                "extends": [],
                "files": [self.entry("AGENTS.md")],
            },
            {
                "name": "active_work",
                "extends": ["startup"],
                "files": [self.entry("ACTIVE.md")],
            },
        ]
        self.write_manifest(self.manifest(profiles))
        exit_code, stdout, stderr = self.run_checker()
        self.assertEqual(0, exit_code, stderr)
        self.assertIn("STARTUP PASS", stdout)
        self.assertIn("used=3 estimated tokens", stdout)
        self.assertNotIn("active_work", stdout)
        self.assertNotIn("32,769", stdout)

    def test_baseline_and_check_ignore_non_startup_content(self):
        self.write_text("ACTIVE.md", "small active plan\n")
        profiles = [
            {
                "name": "startup",
                "extends": [],
                "files": [self.entry("AGENTS.md")],
            },
            {
                "name": "active_work",
                "extends": ["startup"],
                "files": [self.entry("ACTIVE.md")],
            },
        ]
        self.establish_baseline(self.manifest(profiles))
        baseline = json.loads(
            (self.root / "instruction-load-baseline.json").read_text(encoding="utf-8")
        )
        self.assertEqual(["startup"], [profile["name"] for profile in baseline["profiles"]])

        self.write_text("ACTIVE.md", "x" * (32_769 * 4 - 3))
        exit_code, _, stderr = self.run_checker("--check")
        self.assertEqual(0, exit_code, stderr)

    def test_baseline_output_is_deterministic_with_one_lf(self):
        first = self.establish_baseline()
        exit_code, _, stderr = self.run_checker("--update-baseline")
        self.assertEqual(0, exit_code, stderr)
        second = (self.root / "instruction-load-baseline.json").read_bytes()
        self.assertEqual(first, second)
        self.assertTrue(second.endswith(b"\n"))
        self.assertFalse(second.endswith(b"\n\n"))

    def test_report_and_check_are_read_only(self):
        self.establish_baseline()
        before = self.snapshot_files()
        for mode in ("--report", "--check"):
            exit_code, _, stderr = self.run_checker(mode)
            self.assertEqual(0, exit_code, stderr)
        self.assertEqual(before, self.snapshot_files())

    def test_update_baseline_changes_only_baseline(self):
        self.write_manifest()
        before = self.snapshot_files()
        exit_code, _, stderr = self.run_checker("--update-baseline")
        self.assertEqual(0, exit_code, stderr)
        after = self.snapshot_files()
        self.assertEqual(set(before) | {"instruction-load-baseline.json"}, set(after))
        for path, content in before.items():
            self.assertEqual(content, after[path])

    def test_script_resolves_root_outside_repository(self):
        self.establish_baseline()
        result = subprocess.run(
            [sys.executable, str(CHECKER_PATH), "--check", "--repo-root", str(self.root)],
            cwd=self.root.parent,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stderr)

    def test_active_plan_requires_exact_memory_path(self):
        active_path = ".adaptive-agents/planning/active/ACTIVE.md"
        memory_path = ".adaptive-agents/planning/active/PL-test.memory.md"
        self.write_text(active_path, "# PL-test: Active\n\n- Work Unit: PL-test\n")
        self.write_text(memory_path, "# Memory\n")
        profiles = [
            {
                "name": "adaptive_agents_planned_change",
                "extends": [],
                "files": [self.entry(active_path), self.entry(memory_path)],
            }
        ]
        expanded = checker.validate_and_expand_manifest(self.manifest(profiles), self.root)
        self.assertEqual(memory_path, expanded[0]["files"][-1]["path"])

        profiles[0]["files"] = [self.entry(active_path)]
        with self.assertRaisesRegex(checker.ValidationError, "memory"):
            checker.validate_and_expand_manifest(self.manifest(profiles), self.root)

    def test_no_active_plan_omits_memory(self):
        active_path = ".adaptive-agents/planning/active/ACTIVE.md"
        self.write_text(active_path, "# No Active Plan\n")
        profiles = [
            {
                "name": "adaptive_agents_planned_change",
                "extends": [],
                "files": [self.entry(active_path)],
            }
        ]
        checker.validate_and_expand_manifest(self.manifest(profiles), self.root)

    def test_per_profile_deduplication_does_not_suppress_other_profiles(self):
        profiles = [
            {"name": "one", "extends": [], "files": [self.entry("AGENTS.md")]},
            {"name": "two", "extends": [], "files": [self.entry("AGENTS.md")]},
        ]
        baseline = checker.build_baseline(self.root, self.manifest(profiles))
        self.assertEqual("AGENTS.md", baseline["profiles"][0]["files"][0]["path"])
        self.assertEqual("AGENTS.md", baseline["profiles"][1]["files"][0]["path"])

    def test_stricter_profile_limit_and_looser_limit_validation(self):
        strict = self.manifest()
        strict["profiles"][0]["maxEstimatedTokens"] = 1
        with self.assertRaisesRegex(checker.ValidationError, "exceeds profile limit"):
            checker.build_baseline(self.root, strict)

        loose = self.manifest()
        loose["profiles"][0]["maxEstimatedTokens"] = 32_769
        with self.assertRaisesRegex(checker.ValidationError, "looser"):
            checker.validate_and_expand_manifest(loose, self.root)

    def test_growth_tolerance_null_and_configured(self):
        manifest = self.manifest()
        self.establish_baseline(manifest)
        self.write_text("AGENTS.md", "alpha beta gamma\n")
        exit_code, _, stderr = self.run_checker("--check")
        self.assertEqual(1, exit_code)
        self.assertNotIn("growth limit", stderr.lower())

        manifest["profiles"][0]["maxGrowthEstimatedTokens"] = 0
        self.establish_baseline(manifest)
        self.write_text("AGENTS.md", "alpha beta gamma delta\n")
        exit_code, _, stderr = self.run_checker("--check")
        self.assertEqual(1, exit_code)
        self.assertIn("growth limit", stderr.lower())

    def test_usage_errors_exit_two(self):
        for args in (("--unknown",), ("--check", "--report")):
            with self.subTest(args=args):
                exit_code, _, stderr = self.run_checker(*args)
                self.assertEqual(2, exit_code)
                self.assertIn("usage:", stderr.lower())

    def test_shell_wrapper_forwards_exit_code_and_output(self):
        bash_command = "bash"
        wrapper_path = WRAPPER_PATH.as_posix()
        if sys.platform == "win32":
            git_path = Path(shutil.which("git"))
            bash_command = str(git_path.parents[2] / "bin" / "bash.exe")
            wrapper_path = f"/{WRAPPER_PATH.drive[0].lower()}{wrapper_path[2:]}"
        result = subprocess.run(
            [bash_command, wrapper_path, "--unknown"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(2, result.returncode)
        self.assertIn("usage:", result.stderr.lower())

    @staticmethod
    def entry(path):
        return {
            "path": path,
            "classification": "profile",
            "reason": "Required by fixture routing.",
        }

    def snapshot_files(self):
        return {
            path.relative_to(self.root).as_posix(): path.read_bytes()
            for path in self.root.rglob("*")
            if path.is_file()
        }


if __name__ == "__main__":
    unittest.main()