import importlib.util
import json
import queue
import tempfile
import unittest
from pathlib import Path


UI_MODULE_PATH = Path(__file__).resolve().parents[2] / "scripts" / "markdown_browser.py"
UI_MODULE_SPEC = importlib.util.spec_from_file_location("adaptive_agents_ui", UI_MODULE_PATH)
ui = importlib.util.module_from_spec(UI_MODULE_SPEC)
UI_MODULE_SPEC.loader.exec_module(ui)


class EventBrokerTests(unittest.TestCase):
    def test_publish_broadcasts_to_each_subscriber(self):
        broker = ui.EventBroker()
        first = broker.subscribe()
        second = broker.subscribe()
        event = ("file_changed", {"path": ".adaptive-agents/memory/INDEX.md"})

        broker.publish(*event)

        self.assertEqual(first.get_nowait(), event)
        self.assertEqual(second.get_nowait(), event)

    def test_unsubscribe_stops_delivery(self):
        broker = ui.EventBroker()
        subscribed = broker.subscribe()
        removed = broker.subscribe()
        broker.unsubscribe(removed)

        broker.publish("tree_changed", {})

        self.assertEqual(subscribed.get_nowait(), ("tree_changed", {}))
        with self.assertRaises(queue.Empty):
            removed.get_nowait()


class BrowserConfigTests(unittest.TestCase):
    def test_context_separates_target_project_and_system_home(self):
        with tempfile.TemporaryDirectory() as target_dir, tempfile.TemporaryDirectory() as system_dir:
            target = Path(target_dir)
            system = Path(system_dir)
            (system / "ui" / "markdown-browser").mkdir(parents=True)
            (target / ".adaptive-agents").mkdir()
            (target / ".adaptive-agents" / "project-layer.json").write_text(json.dumps({
                "projectName": "Other Project",
                "adaptiveAgentsHome": system.as_posix(),
            }), encoding="utf-8")

            config = ui.BrowserConfig.create(target_root=target, system_root=system)
            context = ui.context_json(config)

            self.assertEqual(context["targetName"], "Other Project")
            self.assertEqual(Path(context["targetRoot"]), target.resolve())
            self.assertEqual(Path(context["projectLayerRoot"]), target.resolve() / ".adaptive-agents")
            self.assertEqual(Path(context["systemHome"]), system.resolve())

    def test_context_defaults_system_home_to_canonical_root_without_manifest(self):
        with tempfile.TemporaryDirectory() as target_dir, tempfile.TemporaryDirectory() as system_dir:
            target = Path(target_dir)
            system = Path(system_dir)

            config = ui.BrowserConfig.create(target_root=target, system_root=system)
            context = ui.context_json(config)

            self.assertEqual(Path(context["targetRoot"]), target.resolve())
            self.assertEqual(Path(context["projectLayerRoot"]), target.resolve() / ".adaptive-agents")
            self.assertEqual(Path(context["systemHome"]), system.resolve())


if __name__ == "__main__":
    unittest.main()