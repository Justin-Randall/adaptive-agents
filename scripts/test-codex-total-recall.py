#!/usr/bin/env python3
"""Focused tests for the Codex Total Recall foundation."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("codex_total_recall.py")
SPEC = importlib.util.spec_from_file_location("codex_total_recall", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class TotalRecallTests(unittest.TestCase):
    def setUp(self) -> None:
        # The bundled Windows runtime may resolve its default temp directory
        # inside a sandbox that is not writable. Keep fixtures under the
        # repository workspace, which is the supported test write boundary.
        self.temp = tempfile.TemporaryDirectory(dir=Path.cwd())
        self.store = MODULE.SessionStore(Path(self.temp.name) / "sessions" / "codex")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def hook(self, event: str, **extra: object) -> dict[str, object]:
        data: dict[str, object] = {
            "session_id": "thr_test-session",
            "cwd": "/workspace/example",
            "hook_event_name": event,
            "turn_id": "turn-1",
        }
        data.update(extra)
        return data

    def test_capture_is_idempotent_and_rebuilds_hierarchical_graph(self) -> None:
        first = self.store.capture(self.hook("UserPromptSubmit", prompt="Remember the middle decision."))
        second = self.store.capture(self.hook("UserPromptSubmit", prompt="Remember the middle decision."))
        self.assertTrue(first[2])
        self.assertFalse(second[2])
        self.assertEqual(first[1], second[1])
        session_dir = first[0]
        self.assertTrue((session_dir / "INDEX.md").is_file())
        self.assertTrue((session_dir / "indexes" / "events.md").is_file())
        self.assertTrue((session_dir / "indexes" / "by-type" / "index.md").is_file())
        self.assertEqual(MODULE.validate_session(session_dir), [])
        semantic = (session_dir / "INDEX.md").read_text(encoding="utf-8")
        self.assertIn("Recovery Bootstrap", semantic)
        self.assertIn("AGENTS.md", semantic)
        self.assertIn("descriptive Markdown link text", semantic)
        self.assertIn("why it matters", semantic)
        self.assertIn("event-type", semantic)

        first_event = json.loads((session_dir / "ledger.json").read_text(encoding="utf-8"))["events"][0]
        source_link = f"{first_event['path']}#{first_event['anchor']}"
        semantic = semantic.replace(
            "No model-authored semantic breadcrumbs have been accepted by the deterministic adapter yet. Add meaningful breadcrumbs directly to this section during the pre-compaction maintenance pass.",
            f"- [Durable test fact: ALPHA-RECALL-7291]({source_link})\n  - Why it matters: Used to verify post-compaction recall.",
        )
        (session_dir / "INDEX.md").write_text(semantic, encoding="utf-8")
        self.store.capture(self.hook("Stop", last_assistant_message="preserve root breadcrumbs"))
        rebuilt = (session_dir / "INDEX.md").read_text(encoding="utf-8")
        self.assertIn("Durable test fact: ALPHA-RECALL-7291", rebuilt)
        self.assertEqual(MODULE.validate_session(session_dir), [])

    def test_seed_template_and_context_packets_are_generated_from_authoritative_ledger(self) -> None:
        events = [
            self.hook("UserPromptSubmit", prompt="Choose the packet boundary."),
            self.hook("Stop", last_assistant_message="The packet must preserve context."),
            self.hook("PostToolUse", tool_name="Bash", tool_output="evidence"),
        ]
        session_dir = None
        for event in events:
            session_dir, _, _ = self.store.capture(event)
        assert session_dir

        ledger_lines = (session_dir / "ledger.jsonl").read_text(encoding="utf-8").splitlines()
        ledger = json.loads((session_dir / "ledger.json").read_text(encoding="utf-8"))
        self.assertEqual(len(ledger_lines), len(ledger["events"]))
        self.assertEqual(json.loads(ledger_lines[0])["payload"]["prompt"], "Choose the packet boundary.")
        self.assertEqual(json.loads(ledger_lines[0])["ledger_line"], 1)
        self.assertTrue((session_dir / "indexes" / "context-packets.md").is_file())
        packet = session_dir / "context-packets" / "packet-000002.md"
        self.assertTrue(packet.is_file())
        packet_text = packet.read_text(encoding="utf-8")
        self.assertIn("source-events", packet_text)
        self.assertIn(ledger["events"][1]["event_id"], packet_text)
        self.assertIn(ledger["events"][0]["event_id"], packet_text)
        manifest = json.loads((session_dir / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["index_template_version"], 2)
        self.assertEqual(manifest["graph_budget"]["mode"], "heuristic")
        self.assertEqual(MODULE.validate_session(session_dir), [])

    def test_direct_jsonl_line_range_locator_is_validated(self) -> None:
        session_dir, _, _ = self.store.capture(self.hook("UserPromptSubmit", prompt="topic one"))
        self.store.capture(self.hook("Stop", last_assistant_message="context one"))
        root = session_dir / "INDEX.md"
        root.write_text(
            root.read_text(encoding="utf-8")
            + "\n- [Topic one with surrounding context](ledger.jsonl#L1-L2) — Read ledger.jsonl lines 1–2.\n",
            encoding="utf-8",
        )
        self.assertEqual(MODULE.validate_session(session_dir), [])
        root.write_text(root.read_text(encoding="utf-8").replace("ledger.jsonl#L1-L2", "ledger.jsonl#L1-L99"), encoding="utf-8")
        errors = MODULE.validate_session(session_dir)
        self.assertTrue(any("broken Markdown anchor" in error for error in errors))

    def test_jsonl_ledger_is_authoritative_over_compatibility_mirror(self) -> None:
        session_dir, _, _ = self.store.capture(self.hook("UserPromptSubmit", prompt="authoritative JSONL"))
        mirror_path = session_dir / "ledger.json"
        mirror = json.loads(mirror_path.read_text(encoding="utf-8"))
        mirror["events"][0]["path"] = "events/stale-mirror.md"
        mirror["events"][0]["payload"]["prompt"] = "stale mirror detail"
        mirror_path.write_text(json.dumps(mirror), encoding="utf-8")
        self.store.capture(self.hook("Stop", last_assistant_message="continue from JSONL"))
        repaired = json.loads(mirror_path.read_text(encoding="utf-8"))
        self.assertEqual(repaired["events"][0]["path"], "events/000001-userpromptsubmit-" + repaired["events"][0]["fingerprint"][:10] + ".md")
        self.assertEqual(repaired["events"][0]["payload"]["prompt"], "authoritative JSONL")
        self.assertEqual(MODULE.validate_session(session_dir), [])

    def test_recursive_indexes_are_valid_without_a_fixed_depth(self) -> None:
        session_dir, _, _ = self.store.capture(self.hook("UserPromptSubmit", prompt="deep graph"))
        current = session_dir / "indexes"
        links = []
        for depth in range(8):
            next_dir = current / f"level-{depth}"
            next_dir.mkdir(parents=True, exist_ok=True)
            next_file = next_dir / "index.md"
            links.append(next_file)
            current = next_dir
        for index, next_file in zip(links, links[1:]):
            relative = next_file.relative_to(index.parent).as_posix()
            index.write_text(f"# Level\n\n- [Next semantic topic]({relative})\n", encoding="utf-8")
        event = json.loads((session_dir / "ledger.json").read_text(encoding="utf-8"))["events"][0]
        source_path = Path(*([".."] * (len(links[-1].relative_to(session_dir).parts) - 1))) / event["path"]
        links[-1].write_text(
            f"# Deep topic\n\n- [Source detail]({source_path.as_posix()}#{event['anchor']})\n",
            encoding="utf-8",
        )
        root = session_dir / "INDEX.md"
        root.write_text(root.read_text(encoding="utf-8") + "\n- [Deep topic](indexes/level-0/index.md)\n", encoding="utf-8")
        self.assertEqual(MODULE.validate_session(session_dir), [])

    def test_validator_rejects_missing_external_markdown_link(self) -> None:
        session_dir, _, _ = self.store.capture(self.hook("UserPromptSubmit", prompt="external link test"))
        root = session_dir / "INDEX.md"
        root.write_text(
            root.read_text(encoding="utf-8")
            + "\n- [Missing authority](file:///definitely-missing-adaptive-agents-authority.md)\n",
            encoding="utf-8",
        )
        errors = MODULE.validate_session(session_dir)
        self.assertTrue(any("broken Markdown link" in error for error in errors))

    def test_validator_ignores_markdown_inside_fenced_event_payloads(self) -> None:
        session_dir, _, _ = self.store.capture(
            self.hook("UserPromptSubmit", prompt="Payload text contains [not a graph edge](missing.md).")
        )
        self.assertEqual(MODULE.validate_session(session_dir), [])

    def test_all_representative_events_are_retained(self) -> None:
        events = [
            self.hook("UserPromptSubmit", prompt="user"),
            self.hook("PreToolUse", tool_name="Bash", tool_input={"command": "echo test"}),
            self.hook("PostToolUse", tool_name="Bash", tool_output="test"),
            self.hook("Stop", last_assistant_message="assistant"),
            self.hook("PreCompact", trigger="auto"),
            self.hook("PostCompact", trigger="auto"),
        ]
        session_dir = None
        for event in events:
            session_dir, _, created = self.store.capture(event)
            self.assertTrue(created)
        assert session_dir
        ledger = json.loads((session_dir / "ledger.json").read_text(encoding="utf-8"))
        self.assertEqual(len(ledger["events"]), len(events))
        self.assertEqual(ledger["events"][1]["payload"]["tool_name"], "Bash")
        self.assertEqual(ledger["events"][2]["payload"]["tool_output"], "test")
        self.assertEqual(MODULE.validate_session(session_dir), [])

    def test_provider_identity_maps_stably_and_separates_sessions(self) -> None:
        first, _, _ = self.store.capture(self.hook("SessionStart", source="startup"))
        same, _, _ = self.store.capture(self.hook("SessionEnd", reason="other"))
        other_data = self.hook("SessionStart", source="startup")
        other_data["session_id"] = "thr_other-session"
        second, _, _ = self.store.capture(other_data)
        self.assertEqual(first, same)
        self.assertNotEqual(first, second)
        mapping = json.loads((self.store.map_path).read_text(encoding="utf-8"))
        self.assertEqual(set(mapping["sessions"]), {"thr_test-session", "thr_other-session"})
        self.assertEqual(MODULE.validate_session(first), [])
        self.assertEqual(MODULE.validate_session(second), [])

    def test_session_namespace_supports_atomic_graph_updates(self) -> None:
        session_dir, _, _ = self.store.capture(self.hook("UserPromptSubmit", prompt="permission contract"))
        probe = session_dir / ".write-probe"
        probe.write_text("ok", encoding="utf-8")
        self.assertEqual(probe.read_text(encoding="utf-8"), "ok")
        probe.unlink()
        self.assertEqual(MODULE.validate_session(session_dir), [])

    def test_validator_rejects_orphaned_event(self) -> None:
        session_dir, _, _ = self.store.capture(self.hook("UserPromptSubmit", prompt="orphan test"))
        ledger_path = session_dir / "ledger.jsonl"
        event = json.loads(ledger_path.read_text(encoding="utf-8").splitlines()[0])
        event["path"] = "events/missing.md"
        ledger_path.write_text(json.dumps(event) + "\n", encoding="utf-8")
        errors = MODULE.validate_session(session_dir)
        self.assertTrue(any("record is missing" in error for error in errors))

    def test_validator_rejects_unaccounted_event_record(self) -> None:
        session_dir, _, _ = self.store.capture(self.hook("UserPromptSubmit", prompt="accounting test"))
        extra = session_dir / "events" / "999999-unaccounted.md"
        extra.write_text("# Unaccounted\n", encoding="utf-8")
        errors = MODULE.validate_session(session_dir)
        self.assertTrue(any("not accounted for in ledger" in error for error in errors))

    def test_malformed_ledger_is_preserved_and_stops_capture(self) -> None:
        session_dir, _, _ = self.store.capture(self.hook("UserPromptSubmit", prompt="preserve malformed"))
        ledger_path = session_dir / "ledger.jsonl"
        malformed = "{not-json}\n"
        ledger_path.write_text(malformed, encoding="utf-8")
        with self.assertRaises(ValueError):
            self.store.capture(self.hook("Stop", last_assistant_message="must not overwrite"))
        self.assertEqual(ledger_path.read_text(encoding="utf-8"), malformed)

    def test_legacy_graph_without_jsonl_or_template_metadata_remains_readable(self) -> None:
        session_dir, _, _ = self.store.capture(self.hook("UserPromptSubmit", prompt="legacy graph"))
        (session_dir / "ledger.jsonl").unlink()
        manifest_path = session_dir / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["version"] = 1
        manifest.pop("index_template_version", None)
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        self.assertEqual(MODULE.validate_session(session_dir), [])

    def test_session_start_returns_compact_recovery_context(self) -> None:
        output = MODULE.handle_hook(self.hook("SessionStart", source="compact"), self.store)
        self.assertIsNotNone(output)
        context = output["hookSpecificOutput"]["additionalContext"]  # type: ignore[index]
        self.assertIn("Total Recall session graph root", context)
        self.assertIn("Adaptive Agents remains active", context)
        self.assertIn("INDEX.md", context)
        self.assertIn("descriptive link text", context)
        self.assertIn("pre-compaction checkpoint", context)
        self.assertIn("canonical", context)
        self.assertIn("AGENTS.md", context)
        self.assertNotIn("consulting", context)

    def test_user_prompt_submit_returns_incremental_maintenance_context(self) -> None:
        output = MODULE.handle_hook(self.hook("UserPromptSubmit", prompt="Record durable test facts."), self.store)
        self.assertIsNotNone(output)
        context = output["hookSpecificOutput"]["additionalContext"]  # type: ignore[index]
        self.assertIn("semantic navigation surface", context)
        self.assertIn("descriptive link text", context)
        self.assertIn("PreCompact hook itself cannot inject model context", context)

    def test_semantic_maintenance_prompt_is_pre_compaction_and_source_anchored(self) -> None:
        session_dir, _, _ = self.store.capture(self.hook("UserPromptSubmit", prompt="durable fact"))
        prompt = MODULE.semantic_maintenance_prompt(session_dir)
        self.assertIn("Before compaction", prompt)
        self.assertIn("full session detail", prompt)
        self.assertIn("descriptive Markdown link text", prompt)
        self.assertIn((session_dir / "INDEX.md").as_posix(), prompt)
        self.assertIn("deterministic validator", prompt)

    def test_hook_configuration_covers_capture_and_recovery_events(self) -> None:
        config = MODULE.hook_configuration(MODULE_PATH)
        hooks = config["hooks"]
        for event in (
            "SessionStart",
            "UserPromptSubmit",
            "PreToolUse",
            "PostToolUse",
            "PreCompact",
            "PostCompact",
            "SubagentStart",
            "SubagentStop",
            "Stop",
            "SessionEnd",
        ):
            self.assertIn(event, hooks)
        self.assertEqual(hooks["SessionStart"][0]["hooks"][0]["additionalContextLimit"], 1200)
        self.assertEqual(hooks["UserPromptSubmit"][0]["hooks"][0]["additionalContextLimit"], 1200)


if __name__ == "__main__":
    unittest.main()
