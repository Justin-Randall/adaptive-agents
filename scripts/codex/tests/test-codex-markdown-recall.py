#!/usr/bin/env python3
"""Falsifiable storage gates for the isolated Markdown ledger experiment."""

import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import codex_markdown_recall as md


class MarkdownLedgerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.store = md.MarkdownStore(Path(self.temp.name) / "recall")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def payload(self, **fields: object) -> dict:
        return {"session_id": "test", "hook_event_name": "PostToolUse", **fields}

    def test_tool_capture_delivers_real_bounded_source_handles(self) -> None:
        payload = self.payload(tool_input={"command": "read notes"}, tool_response={
            "stdout": "Actual newly observed evidence.\n" * 800})
        output = md.handle_hook(payload, self.store, proactive=True)
        self.assertIsNotNone(output)
        context = output["hookSpecificOutput"]["additionalContext"]
        session = next(p for p in self.store.root.iterdir() if p.is_dir())
        event = md.read_events(session)[0]
        self.assertIn(f"ledger.md#{event['event_id']}", context)
        self.assertNotIn("../ledger.md", context)
        self.assertIn("relative to INDEX.md", context)
        self.assertLessEqual(len(context.encode()), md.core.MAX_ADDITIONAL_CONTEXT_BYTES)
        anchors = re.findall(r"ledger\.md#(evt-[\w-]+-f\d+-p\d+)", context)
        self.assertTrue(anchors)
        for anchor in anchors:
            self.assertIn("Actual newly observed", md.read_source(session, anchor)["text"])
        self.assertIn("more parts", context)
        self.assertEqual(md.handle_hook(payload, self.store, proactive=True), output)
        self.assertEqual(len(md.read_events(session)), 1)

    def test_roundtrip_values_without_a_jsonl_mirror(self) -> None:
        cases = [
            {"tool_response": "Hello\n\nWorld\n"},
            {"tool_response": {"nested": [None, False, 0, 1.25, "", {"$text": "literal"}]}},
            {"tool_response": "CRLF\r\nCR\rLF\nTabs\t trailing  \n"},
            {"tool_response": "\u201cUnicode\u201d \u03bb \U0001f642\n" * 1500},
            {"tool_response": "````text\n# Fake heading\n<a id=\"fake\"></a>\n````\n"
             "<!-- recall-record bytes=1 -->\n"},
            {"tool_response": "Control \x00 \x1b and blank \n\n"},
        ]
        for n, case in enumerate(cases):
            payload = self.payload(turn_id=str(n), **case)
            session, _, _ = self.store.capture(payload)
        self.assertEqual([e["payload"] for e in md.read_events(session)],
                         [self.payload(turn_id=str(n), **c) for n, c in enumerate(cases)])
        self.assertFalse((session / "ledger.jsonl").exists())
        text = (session / "ledger.md").read_bytes().decode("utf-8")
        self.assertIn("Hello\n\nWorld\n", text)
        self.assertIn("\u201cUnicode\u201d", text)
        self.assertEqual(md.validate(session), [])

    def test_anchor_addressing_and_bytes_survive_appends(self) -> None:
        text = "Opening\n" + "Long narrative observation.\n" * 300 + "FINAL corrected limit 47.\n"
        session, event, _ = self.store.capture(self.payload(tool_response=text))
        before = (session / "ledger.md").read_bytes()
        parts = md.text_parts(md.read_events(session)[0])
        selected = next(p for p in parts if "corrected limit" in p["text"])
        self.assertNotEqual(selected["anchor"], event)
        page = md.read_source(session, selected["anchor"])
        self.assertIn("corrected limit", page["text"])
        self.store.capture(self.payload(turn_id="later", tool_response="Other evidence"))
        self.assertTrue((session / "ledger.md").read_bytes().startswith(before))
        self.assertEqual(md.read_source(session, selected["anchor"]), page)
        match = md.search(session, "corrected limit")["matches"][0]
        self.assertEqual(match["anchor"], selected["anchor"])

    def test_interrupted_append_fails_without_losing_prefix(self) -> None:
        session, _, _ = self.store.capture(self.payload(tool_response="Retained"))
        path = session / "ledger.md"
        prefix = path.read_bytes()
        path.write_bytes(prefix + b"<!-- recall-record bytes=500 sha256=unfinished")
        with self.assertRaisesRegex(ValueError, "incomplete|corrupt"):
            md.read_events(session)
        with self.assertRaises(ValueError):
            self.store.capture(self.payload(turn_id="later"))
        self.assertTrue(path.read_bytes().startswith(prefix))

    def test_identical_delivery_is_idempotent_and_corruption_visible(self) -> None:
        payload = self.payload(tool_response="Unique exact source")
        session, _, _ = self.store.capture(payload)
        self.assertFalse(self.store.capture(payload)[2])
        path = session / "ledger.md"
        path.write_bytes(path.read_bytes().replace(b"Unique exact source", b"Altered exact value"))
        with self.assertRaisesRegex(ValueError, "corrupt|checksum"):
            md.read_events(session)

    def test_concurrent_processes_and_restart_preserve_sources(self) -> None:
        script = Path(md.__file__)
        def capture(n: int) -> subprocess.CompletedProcess:
            return subprocess.run([sys.executable, str(script), "--root", str(self.store.root)],
                input=json.dumps(self.payload(turn_id=str(n), tool_response=f"Observation {n}")),
                text=True, capture_output=True, timeout=30)
        with ThreadPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(capture, range(8)))
        self.assertTrue(all(r.returncode == 0 for r in results), [r.stderr for r in results])
        session = next(p for p in self.store.root.iterdir() if p.is_dir())
        self.assertEqual(len(md.read_events(session)), 8)
        self.assertEqual(md.MarkdownStore(self.store.root).capture(self.payload(turn_id="8"))[0], session)
        self.assertEqual(len(md.read_events(session)), 9)

    def test_bounded_unicode_reads_and_explicit_bad_coordinates(self) -> None:
        session, _, _ = self.store.capture(self.payload(tool_response="\U0001f642" * 4000))
        part = md.text_parts(md.read_events(session)[0])[0]
        offset, pieces = 0, []
        while True:
            page = md.read_source(session, part["anchor"], offset)
            self.assertLessEqual(len(json.dumps(page, ensure_ascii=True).encode()), 4096)
            pieces.append(page["text"])
            if page["next_offset"] is None:
                break
            offset = page["next_offset"]
        self.assertEqual("".join(pieces), part["text"])
        with self.assertRaises(ValueError):
            md.read_source(session, "not-a-source")
        with self.assertRaises(ValueError):
            md.read_source(session, part["anchor"], -1)
        self.assertIsNone(md.handle_hook(self.payload(hook_event_name="Stop"), self.store))

    def test_header_only_restart_and_jsonl_rejection(self) -> None:
        payload = self.payload(tool_response="First source")
        session = self.store.session_for("test", payload)
        (session / "ledger.md").write_bytes(md.HEADER)
        self.store.capture(payload)
        self.assertEqual(len(md.read_events(session)), 1)
        legacy = md.core.SessionStore(Path(self.temp.name) / "legacy")
        old_session = legacy.session_for("test", payload)
        (old_session / "ledger.jsonl").write_text('{"historical":"evidence"}\n', encoding="utf-8")
        before = {p.name: p.read_bytes() for p in old_session.iterdir() if p.is_file()}
        with self.assertRaisesRegex(ValueError, "deprecated"):
            md.MarkdownStore(legacy.root).capture(payload)
        self.assertEqual({p.name: p.read_bytes() for p in old_session.iterdir() if p.is_file()}, before)

    def test_search_raw_newlines_and_cross_part_phrase(self) -> None:
        text = "x" * 1595 + "CROSS BOUNDARY\r\nsecond line\ncontrol\x00text"
        session, _, _ = self.store.capture(self.payload(tool_response=text))
        for query in ("CROSS BOUNDARY", "BOUNDARY\r\nsecond", "control\x00text"):
            result = md.search(session, query)
            self.assertTrue(result["matches"], query)
            hit = result["matches"][0]
            page = md.read_source(session, hit["anchor"], hit["offset"])
            recovered = page["text"]
            if page["next_part"]:
                recovered += md.read_source(session, page["next_part"])["text"]
            self.assertIn(query, recovered)

    def test_search_pagination_bounds_and_no_match_cursor(self) -> None:
        session, _, _ = self.store.capture(self.payload(tool_response="First"))
        base = md.read_events(session)[0]
        events = []
        for n in range(1, 261):
            payload = self.payload(turn_id=str(n), tool_response="common " + ("\u03bb later" if n == 257 else "text"))
            fingerprint = md.core.event_fingerprint(payload)
            events.append({**base, "sequence": n, "event_id": f"evt-{n:06d}-{fingerprint[:12]}",
                           "fingerprint": fingerprint, "payload": payload})
        (session / "ledger.md").write_bytes(md.HEADER + b"".join(md.render_event(e) for e in events))
        empty_page = md.search(session, "\u03bb later")
        self.assertEqual(empty_page, {"matches": [], "next_event": 257})
        self.assertEqual(md.search(session, "\u03bb later", 257)["matches"][0]["anchor"],
                         md.text_parts(events[256])[0]["anchor"])
        cursor, anchors = 1, []
        while cursor is not None:
            page = md.search(session, "common", cursor)
            self.assertLessEqual(len(json.dumps(page, ensure_ascii=True).encode()), 4096)
            anchors.extend(m["anchor"] for m in page["matches"])
            cursor = page["next_event"]
        self.assertEqual(len(anchors), 260)
        self.assertEqual(len(set(anchors)), 260)
        for query, cursor in [("", 1), ("x", 0), ("x", 262)]:
            with self.assertRaises(ValueError):
                md.search(session, query, cursor)


if __name__ == "__main__":
    unittest.main()
