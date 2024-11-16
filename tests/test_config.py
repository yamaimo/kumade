from collections.abc import Generator
from contextlib import contextmanager
from typing import Optional
from unittest import TestCase

from kumade.config import Config


@contextmanager
def set_config_instance(instance: Optional[Config]) -> Generator[None, None, None]:
    # Save original instance
    org_instance = Config._Config__instance  # type: ignore
    try:
        Config._Config__instance = instance  # type: ignore
        yield
    finally:
        # Restore original instance
        Config._Config__instance = org_instance  # type: ignore


class TestConfig(TestCase):
    def test_get_instance(self) -> None:
        instance = Config({"item1": 1, "item2": True})
        with set_config_instance(instance):
            config = Config.get_instance()
            another = Config.get_instance()
            self.assertEqual(config, another)

    def test_get_instance_before_set(self) -> None:
        with set_config_instance(None):
            with self.assertRaises(RuntimeError):
                Config.get_instance()

    def test_set(self) -> None:
        with set_config_instance(None):
            Config.set({"item1": 1, "item2": "test"})
            config = Config.get_instance()
            self.assertEqual(config.get("item1"), 1)
            self.assertEqual(config.get("item2"), "test")

    def test_set_again(self) -> None:
        with set_config_instance(None):
            Config.set({"item1": 1, "item2": "test"})
            with self.assertRaises(RuntimeError):
                Config.set({"item3": False, "item4": 0.0})

    def test_get(self) -> None:
        config = Config({"item1": 1, "item2": "test"})

        self.assertEqual(config.get("item1"), 1)
        self.assertEqual(config.get("item2"), "test")

        # access via attribute
        self.assertEqual(config.item1, 1)
        self.assertEqual(config.item2, "test")

        # access via key
        self.assertEqual(config["item1"], 1)
        self.assertEqual(config["item2"], "test")

    def test_get_with_not_added_item(self) -> None:
        config = Config({"item1": 1, "item2": "test"})
        with self.assertRaises(RuntimeError):
            config.get("item0")

    def test_values(self) -> None:
        config = Config({"item1": 1, "item2": "test"})
        values = config.values

        expected = {"item1": 1, "item2": "test"}
        self.assertDictEqual(values, expected)
