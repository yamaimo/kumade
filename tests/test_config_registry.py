from unittest import TestCase

from kumade.config import ConfigItem, ConfigRegistry


class TestConfigRegistry(TestCase):
    def test_get_instance(self) -> None:
        registry = ConfigRegistry.get_instance()
        another = ConfigRegistry.get_instance()
        self.assertEqual(registry, another)

    def test_add_item_and_get_all_items(self) -> None:
        registry = ConfigRegistry()

        item1 = ConfigItem("item1", int, 0, "Item 1.")
        item2 = ConfigItem("item2", int, 0, "Item 2.")

        registry.add_item(item1)
        registry.add_item(item2)

        all_items = registry.get_all_items()
        self.assertEqual(len(all_items), 2)
        self.assertIn(item1, all_items)
        self.assertIn(item2, all_items)

    def test_add_item_with_same_item_name(self) -> None:
        registry = ConfigRegistry()

        item = ConfigItem("item", int, 0, "Item.")
        another = ConfigItem("item", int, 0, "Another Item.")
        assert item != another

        registry.add_item(item)
        with self.assertRaises(RuntimeError):
            registry.add_item(another)

    def test_get_confirmed_values(self) -> None:
        registry = ConfigRegistry()

        int_item = ConfigItem("count", int, 0, "Count.")
        float_item = ConfigItem("threshold", float, 0.0, "Threshold.")
        str_item = ConfigItem("name", lambda s: s, "Taro", "Name.")

        registry.add_item(int_item)
        registry.add_item(float_item)
        registry.add_item(str_item)

        confirmed_values = registry.get_confirmed_values({})
        self.assertEqual(len(confirmed_values), 3)
        self.assertIn("count", confirmed_values)
        self.assertEqual(confirmed_values["count"], 0)
        self.assertIn("threshold", confirmed_values)
        self.assertEqual(confirmed_values["threshold"], 0.0)
        self.assertIn("name", confirmed_values)
        self.assertEqual(confirmed_values["name"], "Taro")

        user_specified = {"count": "10", "name": "Jiro"}
        confirmed_values = registry.get_confirmed_values(user_specified)
        self.assertEqual(len(confirmed_values), 3)
        self.assertIn("count", confirmed_values)
        self.assertEqual(confirmed_values["count"], 10)
        self.assertIn("threshold", confirmed_values)
        self.assertEqual(confirmed_values["threshold"], 0.0)
        self.assertIn("name", confirmed_values)
        self.assertEqual(confirmed_values["name"], "Jiro")

    def test_get_confirmed_values_with_not_added_item(self) -> None:
        registry = ConfigRegistry()

        item0 = ConfigItem("item0", int, 0, "Item 0.")
        item1 = ConfigItem("item1", int, 0, "Item 1.")

        registry.add_item(item0)
        registry.add_item(item1)

        user_specified = {"item1": "10", "item2": "20"}
        with self.assertRaises(RuntimeError):
            registry.get_confirmed_values(user_specified)
