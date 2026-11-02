#!/usr/bin/env python3
"""Supported Markdown-only Codex runtime and explicit deprecation regressions."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import codex_hooks_config as hooks
import codex_total_recall as recall


class TotalRecallTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store = recall.SessionStore(Path(self.temp.name) / "sessions")

    def payload(self, kind: str = "SessionStart", **fields: object) -> dict:
        return {"session_id": "test", "hook_event_name": kind, **fields}

    def test_only_markdown_is_created_with_an_explicit_manifest(self) -> None:
        session, _, _ = self.store.capture(self.payload())
        self.assertEqual({p.name for p in session.iterdir()},
                         {"manifest.json", "INDEX.md", "ledger.md", ".graph.lock"})
        manifest = recall.read_json(session / "manifest.json")
        self.assertEqual(manifest["ledger_path"], "ledger.md")
        self.assertEqual(manifest["format"], "markdown-1")
        self.assertEqual(recall.validate(session), [])

    def test_default_guidance_encourages_opportunistic_topics_without_stop_gates(self) -> None:
        for kind in ("SessionStart", "UserPromptSubmit"):
            output = recall.handle_hook(self.payload(kind), self.store)
            context = output["hookSpecificOutput"]["additionalContext"]
            self.assertIn("meaningful subject", context)
            self.assertLessEqual(len(context.encode()), 1200)
            self.assertNotIn("repair batch", context)
            self.assertNotIn("frozen snapshot", context)
        self.assertIsNone(recall.handle_hook(self.payload("Stop", last_assistant_message="Done"), self.store))

    def test_compaction_preserves_source_prefix_and_model_graph(self) -> None:
        session, event, _ = self.store.capture(self.payload("PostToolUse", tool_response="Exact evidence"))
        index = session / "INDEX.md"
        index.write_text(index.read_text(encoding="utf-8").replace(
            "No model-authored topics yet.", f"- [A useful subject](ledger.md#{event})"), encoding="utf-8")
        graph, prefix = index.read_bytes(), (session / "ledger.md").read_bytes()
        for kind in ("PreCompact", "PostCompact", "SessionStart", "Stop"):
            recall.handle_hook(self.payload(kind, source="compact"), self.store)
        self.assertEqual(index.read_bytes(), graph)
        self.assertTrue((session / "ledger.md").read_bytes().startswith(prefix))
        self.assertEqual(recall.validate(session), [])

    def test_deprecated_sessions_fail_without_rewriting_history_or_identity(self) -> None:
        for name in ("ledger.jsonl", "ledger.json"):
            store = recall.SessionStore(Path(self.temp.name) / name)
            payload = self.payload()
            session = store.session_for("test", payload)
            (session / name).write_bytes(b'{"old":"untouched"}\n')
            before = {p: p.read_bytes() for p in store.root.rglob("*") if p.is_file()}
            for action in (lambda: store.capture(payload), lambda: recall.read_events(session)):
                with self.assertRaisesRegex(ValueError, "deprecated.*fresh"):
                    action()
            self.assertEqual(before, {p: p.read_bytes() for p in store.root.rglob("*") if p.is_file()})

    def test_missing_index_is_recreated_on_duplicate_delivery(self) -> None:
        payload = self.payload()
        session, _, _ = self.store.capture(payload)
        (session / "INDEX.md").unlink()
        self.assertFalse(self.store.capture(payload)[2])
        self.assertTrue((session / "INDEX.md").exists())
        self.assertEqual(len(recall.read_events(session)), 1)

    def test_hook_contracts_agree_and_tool_results_have_context_capacity(self) -> None:
        script = Path(recall.__file__)
        self.assertEqual(recall.hook_configuration(script), hooks.desired_config(script, sys.executable))
        handler = recall.hook_configuration(script)["hooks"]["PostToolUse"][0]["hooks"][0]
        self.assertEqual(handler["additionalContextLimit"], 1200)
        self.assertNotIn("async", handler)

    def test_cli_retired_modes_fail_explicitly_and_hooks_need_no_stdin(self) -> None:
        for flag in ("--migrate-ledger", "--require-coverage", "--line"):
            result = subprocess.run([sys.executable, recall.__file__, flag, self.temp.name],
                                    capture_output=True, timeout=30)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(b"unrecognized arguments", result.stderr)
        result = subprocess.run([sys.executable, recall.__file__, "--hooks-json"],
                                capture_output=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PostToolUse", json.loads(result.stdout)["hooks"])

    def test_cli_wire_capture_is_locale_independent_and_bad_input_is_visible(self) -> None:
        payload = self.payload("Stop", last_assistant_message="\u201cExact\u201d \u03bb \U0001f642\n" * 1000)
        env = dict(os.environ, PYTHONIOENCODING="cp1252:surrogateescape", PYTHONUTF8="0")
        args = [sys.executable, recall.__file__, "--root", str(self.store.root)]
        result = subprocess.run(args, input=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                                capture_output=True, env=env, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        session = next(self.store.root.glob("*/ledger.md")).parent
        self.assertEqual(recall.read_events(session)[0]["payload"], payload)
        for bad in (b"{", b'{"bad":"\xff"}', b"[]"):
            result = subprocess.run(args, input=bad, capture_output=True, timeout=30)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(b"Codex Total Recall:", result.stderr)

    def test_validator_detects_bad_links_without_requesting_coverage(self) -> None:
        session, _, _ = self.store.capture(self.payload())
        index = session / "INDEX.md"
        index.write_text(index.read_text(encoding="utf-8")
                         + "\n[Unknown](ledger.md#not-an-anchor)\n[Outside](../other.md)\n", encoding="utf-8")
        errors = recall.validate(session)
        self.assertTrue(any("unknown source anchor" in e for e in errors))
        self.assertTrue(any("invalid source path" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
