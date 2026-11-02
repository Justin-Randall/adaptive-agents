#!/usr/bin/env python3
"""Reject recall-provenance claims with missing, contaminated, or unordered evidence."""

import importlib.util
import json
import os
from pathlib import Path
import unittest
from unittest import mock


import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

SPEC = importlib.util.spec_from_file_location("dogfood", Path(__file__).resolve().parents[1] / "dogfood-codex-total-recall.py")
assert SPEC and SPEC.loader
DOGFOOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(DOGFOOD)


class InstalledClientTests(unittest.TestCase):
    def test_installed_mode_preserves_native_environment(self) -> None:
        with (mock.patch.dict(os.environ, {"KEEP_NATIVE": "yes"}, clear=True),
              mock.patch.object(DOGFOOD.subprocess, "Popen") as process,
              mock.patch.object(DOGFOOD.threading, "Thread"),
              mock.patch.object(DOGFOOD.Client, "call")):
            DOGFOOD.Client("codex", Path("native-home"), Path("workspace"), isolated=False)
        env = process.call_args.kwargs["env"]
        self.assertEqual(env, {"KEEP_NATIVE": "yes", "CODEX_HOME": "native-home"})
        self.assertNotIn("ADAPTIVE_AGENTS_ROOT", env)
        self.assertNotIn("PYTHONIOENCODING", env)
        self.assertNotIn("PYTHONUTF8", env)

    def test_isolated_mode_keeps_wire_regression_environment(self) -> None:
        with (mock.patch.dict(os.environ, {}, clear=True),
              mock.patch.object(DOGFOOD.subprocess, "Popen") as process,
              mock.patch.object(DOGFOOD.threading, "Thread"),
              mock.patch.object(DOGFOOD.Client, "call")):
            DOGFOOD.Client("codex", Path("private-home"), Path("workspace"))
        self.assertEqual(process.call_args.kwargs["env"]["PYTHONIOENCODING"], "cp1252:surrogateescape")


class AssistantCaptureTests(unittest.TestCase):
    def setUp(self) -> None:
        self.answer = ("\u201cThe keeper\u2019s journal\u201d records the observations.\n" * 260
                       + "\nOBSERVATORY KEY: A7Q9M2R4\nORCHARD KEY: B8N3P6T2\nCLINIC KEY: C4V7W9X3")
        self.event = {"kind": "Stop", "sequence": 7,
                      "payload": {"last_assistant_message": self.answer}}

    def test_requires_complete_long_unicode_final_reply(self) -> None:
        result = DOGFOOD.assistant_capture(self.answer, [self.event])
        self.assertTrue(all(result["checks"].values()))
        self.assertEqual(result["source_line"], 7)
        self.assertEqual(result["keys"]["ORCHARD"], "B8N3P6T2")

    def test_rejects_missing_truncated_or_mojibake_capture(self) -> None:
        for text in ("", self.answer[:4096],
                     self.answer.encode("utf-8").decode("cp1252", errors="surrogateescape")):
            with self.subTest(text_length=len(text)):
                event = {**self.event, "payload": {"last_assistant_message": text}}
                self.assertFalse(all(DOGFOOD.assistant_capture(self.answer, [event])["checks"].values()))

    def test_prompt_copy_is_not_assistant_capture(self) -> None:
        event = {**self.event, "kind": "UserPromptSubmit"}
        self.assertFalse(all(DOGFOOD.assistant_capture(self.answer, [event])["checks"].values()))

    def test_rejects_weak_fixture_even_when_captured(self) -> None:
        for answer in (self.answer[:100], self.answer.replace("\u201d", '"'),
                       self.answer + "\nORCHARD KEY: AAAAAAAA"):
            with self.subTest(answer_length=len(answer)):
                event = {**self.event, "payload": {"last_assistant_message": answer}}
                self.assertFalse(all(DOGFOOD.assistant_capture(answer, [event])["checks"].values()))


class ProvenanceTests(unittest.TestCase):
    def evidence(self) -> dict:
        fact = "SURVEY-7e824b96e005e937aaef4e32"
        index = "- [Nesting survey archive accession](ledger.jsonl#L4-L4)"
        page = json.dumps({"ledger_line": 4, "offset": 0, "next_offset": None, "text": fact})
        return {
            "fact": fact, "source_line": 4, "index_text": index,
            "context_serialized": "Recover details through the session index.",
            "question": "Recover the nesting survey archive accession.",
            "answer": f"The accession is {fact}. [Ledger](ledger.jsonl#L4-L4)",
            "trace": [
                self.event(1, "started", "index", "Get-Content INDEX.md"),
                self.event(2, "completed", "index", "Get-Content INDEX.md", index),
                self.event(3, "started", "source", "python reader.py --read session --line 4"),
                self.event(4, "completed", "source", "python reader.py --read session --line 4", page),
            ],
        }

    @staticmethod
    def event(sequence: int, state: str, item_id: str, command: str, output: str = "") -> dict:
        return {"sequence": sequence, "method": f"item/{state}",
                "item": {"id": item_id, "type": "commandExecution", "command": command,
                         "aggregatedOutput": output, "exitCode": 0}}

    def test_accepts_ordered_index_then_source_evidence(self) -> None:
        self.assertTrue(all(DOGFOOD.verify_provenance(**self.evidence()).values()))

    def test_accepts_wetland_topic_for_nesting_source(self) -> None:
        evidence = self.evidence()
        evidence["index_text"] = "- [Wetland sluice protection](ledger.jsonl#L4-L4)"
        evidence["trace"][1]["item"]["aggregatedOutput"] = evidence["index_text"]
        self.assertTrue(all(DOGFOOD.verify_provenance(**evidence).values()))

    def test_content_topics_must_link_to_the_actual_tool_result_line(self) -> None:
        index = "\n".join((
            "- [Release waiting period](ledger.jsonl#L6-L6)",
            "- [Nesting protection](ledger.jsonl#L6-L6)",
            "- [Pressure sensor quarantine](ledger.jsonl#L6-L6)",
            "- [Authorized fixture seed invocation](ledger.jsonl#L7-L8)",
            "- [Pressure trip](ledger.jsonl#L8-L8)",
            "- [Release wait](ledger.jsonl#L8-L8)",
            "- [Swallow nesting protection](ledger.jsonl#L8-L8)",
        ))
        self.assertEqual(
            DOGFOOD.content_topic_checks(index, tool_result_line=8),
            {"calibration": True, "release": True, "nesting": True},
        )
        self.assertEqual(
            DOGFOOD.content_topic_checks(index, tool_result_line=9),
            {"calibration": False, "release": False, "nesting": False},
        )

    def test_accepts_native_editor_line_citation(self) -> None:
        evidence = self.evidence()
        evidence["answer"] = f'{evidence["fact"]} [ledger line 4](ledger.jsonl:4)'
        self.assertTrue(all(DOGFOOD.verify_provenance(**evidence).values()))
        evidence["answer"] = f'{evidence["fact"]} [ledger line 40](ledger.jsonl:40)'
        self.assertFalse(all(DOGFOOD.verify_provenance(**evidence).values()))

    def test_rejects_answer_already_in_context_index_or_question(self) -> None:
        for field in ("context_serialized", "index_text", "question"):
            with self.subTest(field=field):
                evidence = self.evidence()
                evidence[field] += evidence["fact"]
                self.assertFalse(all(DOGFOOD.verify_provenance(**evidence).values()))

    def test_rejects_parallel_or_early_source_call(self) -> None:
        evidence = self.evidence()
        evidence["trace"][2]["sequence"] = 1
        self.assertFalse(all(DOGFOOD.verify_provenance(**evidence).values()))

    def test_rejects_citation_without_actual_source_read(self) -> None:
        evidence = self.evidence()
        evidence["trace"] = evidence["trace"][:2]
        self.assertFalse(all(DOGFOOD.verify_provenance(**evidence).values()))

    def test_rejects_wrong_source_line(self) -> None:
        evidence = self.evidence()
        evidence["trace"][3]["item"]["aggregatedOutput"] = json.dumps(
            {"ledger_line": 5, "offset": 0, "next_offset": None, "text": evidence["fact"]})
        self.assertFalse(all(DOGFOOD.verify_provenance(**evidence).values()))

    def test_rejects_earlier_nonledger_disclosure(self) -> None:
        evidence = self.evidence()
        evidence["trace"].insert(0, self.event(0, "completed", "leak", "cat original.txt", evidence["fact"]))
        self.assertFalse(all(DOGFOOD.verify_provenance(**evidence).values()))

    def test_rejects_combined_index_and_source_command(self) -> None:
        evidence = self.evidence()
        evidence["trace"][1]["item"]["command"] += "; python reader.py --read session --line 4"
        self.assertFalse(all(DOGFOOD.verify_provenance(**evidence).values()))


if __name__ == "__main__":
    unittest.main()
