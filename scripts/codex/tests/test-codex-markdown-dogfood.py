#!/usr/bin/env python3
"""Focused checks for the Markdown dogfood evidence accounting."""

import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

SPEC = importlib.util.spec_from_file_location("trial", Path(__file__).resolve().parents[1] / "dogfood-codex-markdown.py")
assert SPEC and SPEC.loader
trial = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(trial)


class EvidenceTests(unittest.TestCase):
    def test_frozen_recall_requires_completed_source_text_and_read_citation(self) -> None:
        anchor = "evt-000004-123456abcdef-f1-p0"
        trace = [{"sequence": 1, "method": "item/completed", "item": {
            "type": "commandExecution", "exitCode": 0, "command": "python reader.py --read history",
            "aggregatedOutput": '{"source":"ledger.md#' + anchor
            + '","text":"Light damages the assay reagent.","next_offset":null}'}}]
        answer = f"Light damages the assay reagent. [Evidence](ledger.md#{anchor})"
        result = trial.frozen_checks(trace, answer, ["assay reagent", "light"], {anchor}, False)
        self.assertTrue(all(result.values()), result)
        self.assertFalse(trial.frozen_checks([], answer, ["assay reagent"], {anchor}, False)["source_evidence"])
        wrong = answer.replace(anchor, "evt-000005-abcdef123456")
        self.assertFalse(trial.frozen_checks(trace, wrong, ["assay reagent"], {anchor}, False)["citation_source"])
        trace[0]["item"]["exitCode"] = 1
        self.assertFalse(trial.frozen_checks(trace, answer, ["assay reagent"], {anchor}, False)["source_evidence"])

    def test_frozen_recall_accepts_sufficient_excerpt_but_rejects_missing_evidence_and_leakage(self) -> None:
        trace = [{"sequence": 1, "method": "item/completed", "item": {
            "type": "commandExecution", "exitCode": 0, "command": "python reader.py --search history",
            "aggregatedOutput": '{"matches":[{"anchor":"evt-1","excerpt":"CEDAR-204"}]}'}}]
        result = trial.frozen_checks(trace, "CEDAR-204 [e](ledger.md#evt-1)", ["CEDAR-204"], {"evt-1"}, True)
        self.assertTrue(all(result.values()), result)
        incomplete = trial.frozen_checks(trace, "CEDAR-204 from dispatch [e](ledger.md#evt-1)",
                                        ["CEDAR-204", "dispatch"], {"evt-1"}, True)
        self.assertFalse(incomplete["source_evidence"])
        self.assertFalse(trial.frozen_checks(trace, "CEDAR-204 [e](ledger.md#evt-2)",
                                            ["CEDAR-204"], {"evt-1"}, True)["citation_source"])
        self.assertFalse(trial.index_control_passes(trace, "UNKNOWN", ["CEDAR-204"]))
        self.assertFalse(trial.index_control_passes([], "UNKNOWN, perhaps CEDAR-204", ["CEDAR-204"]))
        self.assertTrue(trial.index_control_passes([], "UNKNOWN; not in the index.", ["CEDAR-204"]))

    def test_only_real_links_count_and_parts_keep_event_provenance(self) -> None:
        text = "[Pump](ledger.md#evt-000004-123456abcdef-f0-p2)\n```\n[x](ledger.md#evt-999999-abcdef123456)\n```"
        self.assertEqual(trial.linked_events(text), {"evt-000004-123456abcdef"})

    def test_maintenance_counts_completed_discovery_reads_and_patches_once(self) -> None:
        trace = [
            {"method": "item/started", "item": {"type": "fileChange"}},
            {"method": "item/completed", "item": {"type": "fileChange"}},
            {"method": "item/completed", "item": {"type": "commandExecution", "command": "Get-Content INDEX.md"}},
            {"method": "item/completed", "item": {"type": "commandExecution",
                                                "command": "python codex_markdown_recall.py --recent x"}},
            {"method": "item/completed", "item": {"type": "commandExecution",
                                                "command": "python managed-runtime\\launcher.py --recent x"}},
            {"method": "item/completed", "item": {"type": "commandExecution", "command": "Get-Content opening.txt"}},
        ]
        self.assertEqual(trial.maintenance_calls(trace), 4)

    def test_revision_requires_old_and_new_values_and_reason(self) -> None:
        self.assertFalse(trial.facts_pass("revision", "Use 54 kPa."))
        self.assertFalse(trial.facts_pass("revision", "Use 54 instead of 72."))
        self.assertTrue(trial.facts_pass("revision", "54 replaces 72 because the cold seal sticks."))

    def test_existing_report_cannot_be_overwritten(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report = root / "failed.json"
            report.write_bytes(b'{"passed": false}\n')
            result = subprocess.run(
                [sys.executable, str(Path(trial.__file__)), "--mode", "proactive", "--codex", "unused",
                 "--workspace", str(root / "unused"), "--report", str(report)],
                capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 2)
            self.assertIn("report already exists", result.stderr)
            self.assertEqual(report.read_bytes(), b'{"passed": false}\n')
            self.assertFalse((root / "unused").exists())


if __name__ == "__main__":
    unittest.main()
