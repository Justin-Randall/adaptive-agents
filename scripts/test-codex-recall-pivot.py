#!/usr/bin/env python3
"""Reject answer-only, unordered and partial recall evidence."""

import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch


SPEC = importlib.util.spec_from_file_location("pivot", Path(__file__).with_name("dogfood-codex-recall-pivot.py"))
assert SPEC and SPEC.loader
PIVOT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PIVOT)


class PivotChecks(unittest.TestCase):
    def trace(self) -> list[dict]:
        return [
            {"sequence": 1, "method": "item/completed", "item": {
                "id": "index", "type": "commandExecution", "exitCode": 0, "command": "read INDEX.md",
                "aggregatedOutput": "<!-- semantic-breadcrumbs:start -->"}},
            {"sequence": 2, "method": "item/started", "item": {"id": "source", "type": "commandExecution"}},
            {"sequence": 3, "method": "item/completed", "item": {
                "id": "source", "type": "commandExecution", "exitCode": 0, "command": "--read path --line 13",
                "aggregatedOutput": json.dumps({"ledger_line": 13, "next_offset": None,
                                                "text": "First sentence. Second sentence."})}},
        ]

    def check(self, answer: str, trace: list[dict]) -> dict[str, bool]:
        return PIVOT.retrieval_checks(answer, trace, 13, "Chapter 003, paragraph 0020: First sentence. Second sentence.")

    def test_exact_paragraph_and_ordered_evidence_pass(self) -> None:
        self.assertTrue(all(self.check("First sentence. Second sentence. [source](ledger.jsonl#L13)", self.trace()).values()))

    def test_first_sentence_is_not_complete_paragraph(self) -> None:
        self.assertFalse(self.check("First sentence. [source](ledger.jsonl#L13)", self.trace())["exact"])

    def test_source_started_before_index_completed_fails(self) -> None:
        trace = self.trace()
        trace[0]["sequence"] = 4
        self.assertFalse(self.check("First sentence. Second sentence. line 13", trace)["index_before_source"])

    def test_correct_answer_without_returned_source_fails(self) -> None:
        trace = self.trace()
        trace[-1]["item"]["aggregatedOutput"] = ""
        result = self.check("First sentence. Second sentence. line 13", trace)
        self.assertFalse(result["source_read"])
        self.assertFalse(result["source_contains_answer"])

    def test_busy_provider_stream_cannot_extend_deadline(self) -> None:
        client = PIVOT.DOGFOOD.Client.__new__(PIVOT.DOGFOOD.Client)
        client.completed = []
        with patch.object(PIVOT.DOGFOOD.time, "monotonic", side_effect=[0, 2]):
            with self.assertRaisesRegex(TimeoutError, "exceeded"):
                client.wait_turn(0, timeout=1)


if __name__ == "__main__":
    unittest.main()
