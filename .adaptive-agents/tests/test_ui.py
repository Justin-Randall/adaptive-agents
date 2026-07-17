import importlib.util
import queue
import unittest
from pathlib import Path


UI_MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "ui.py"
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


if __name__ == "__main__":
    unittest.main()