#!/usr/bin/env python3
import json
import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
from vscode import copilot_total_recall as adapter
from codex import codex_total_recall as recall


class CopilotResponseTests(unittest.TestCase):
    def test_extracts_latest_visible_assistant_message(self):
        with tempfile.TemporaryDirectory() as temp:
            transcript = Path(temp) / "events.jsonl"
            rows = [
                {"type": "assistant.message", "data": {"content": "first"}},
                {"type": "assistant.message", "data": {"content": "the distinctive long answer"}},
            ]
            transcript.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
            self.assertEqual("the distinctive long answer", adapter.latest_assistant_response(str(transcript)))

    def test_stop_capture_is_deduplicated(self):
        with tempfile.TemporaryDirectory() as temp:
            transcript = Path(temp) / "events.jsonl"
            transcript.write_text(json.dumps({"type": "assistant.message", "data": {"content": "repeatable answer"}}) + "\n", encoding="utf-8")
            store = recall.SessionStore(Path(temp) / "store", provider="copilot")
            data = {"cwd": temp, "hook_event_name": "Stop", "session_id": "provider-1", "transcriptPath": str(transcript)}
            normalized = adapter.normalize(data)
            adapter.capture_assistant_response(normalized, store)
            adapter.capture_assistant_response(normalized, store)
            session = next((Path(temp) / "store").glob("*/ledger.md"))
            ledger = session.read_text(encoding="utf-8")
            self.assertEqual(1, ledger.count("## Event "))
            self.assertIn("AssistantResponse", ledger)
            self.assertIn("repeatable answer", ledger)

    def test_missing_or_malformed_transcript_is_explicitly_ignored(self):
        self.assertIsNone(adapter.latest_assistant_response("missing.jsonl"))

    def test_reads_latest_response_from_tail_of_large_transcript(self):
        with tempfile.TemporaryDirectory() as temp:
            transcript = Path(temp) / "events.jsonl"
            transcript.write_bytes(
                b"x" * (adapter.TRANSCRIPT_MAX_BYTES + 1024)
                + b"\n"
                + json.dumps({"type": "assistant.message", "data": {"content": "latest tail answer"}}).encode()
                + b"\n"
            )
            self.assertEqual("latest tail answer", adapter.latest_assistant_response(str(transcript)))


if __name__ == "__main__":
    unittest.main()
