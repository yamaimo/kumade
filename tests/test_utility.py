from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from kumade.config import Config, ConfigItem, ConfigRegistry
from kumade.manager import TaskManager
from kumade.utility import (
    _str_to_bool,
    add_bool_config,
    add_config,
    add_float_config,
    add_int_config,
    add_path_config,
    add_str_config,
    clean,
    directory,
    get_config,
    set_default,
)


class TestUtility(TestCase):
    def test_set_default(self) -> None:
        manager = TaskManager()
        with patch("kumade.manager.TaskManager.get_instance", return_value=manager):
            set_default("test")
            self.assertEqual(manager.default_task_name, "test")

    def test_clean(self) -> None:
        manager = TaskManager()
        with patch("kumade.manager.TaskManager.get_instance", return_value=manager):
            with TemporaryDirectory() as temp_dir_name:
                temp_dir = Path(temp_dir_name)

                test_file1 = temp_dir / "test.txt"
                test_file1.touch()
                assert test_file1.exists()
                test_dir = temp_dir / "test"
                test_dir.mkdir(parents=True)
                assert test_dir.exists()
                test_file2 = test_dir / "test.txt"
                test_file2.touch()
                assert test_file2.exists()

                clean(
                    "clean",
                    [test_file1, test_dir],
                    dependencies=["clean1", "clean2"],
                    help="Clean task.",
                )

                registered = manager.find("clean")
                self.assertIsNotNone(registered)
                assert registered is not None  # for lint

                self.assertEqual(len(registered.dependencies), 2)
                self.assertIn("clean1", registered.dependencies)
                self.assertIn("clean2", registered.dependencies)
                self.assertEqual(registered.help, "Clean task.")

                registered.run()

                self.assertFalse(test_file1.exists())
                self.assertFalse(test_dir.exists())
                self.assertFalse(test_file2.exists())

    def test_directory(self) -> None:
        manager = TaskManager()
        with patch("kumade.manager.TaskManager.get_instance", return_value=manager):
            with TemporaryDirectory() as temp_dir_name:
                temp_dir = Path(temp_dir_name)

                test_dir = temp_dir / "test"
                assert not test_dir.exists()

                directory(test_dir, dependencies=["dep1", "dep2"])

                registered = manager.find(test_dir)
                self.assertIsNotNone(registered)
                assert registered is not None  # for lint

                self.assertEqual(len(registered.dependencies), 2)
                self.assertIn("dep1", registered.dependencies)
                self.assertIn("dep2", registered.dependencies)

                registered.run()

                self.assertTrue(test_dir.exists())

                # check mkdir() is not called if it already exists.
                # (if mkdir() is called again, an error will occur.)
                registered.run()

    def test_add_config(self) -> None:
        registry = ConfigRegistry()
        with patch("kumade.config.ConfigRegistry.get_instance", return_value=registry):
            converter = lambda s: [s]  # noqa: E731
            default_value: list[str] = []
            item: ConfigItem[list[str]] = ConfigItem(
                "test", converter, default_value, "Test item."
            )

            all_items = registry.get_all_items()
            self.assertNotIn(item, all_items)

            add_config("test", converter, default_value, "Test item.")

            all_items = registry.get_all_items()
            self.assertIn(item, all_items)

            confirmed_values = registry.get_confirmed_values({})
            self.assertDictEqual(confirmed_values, {"test": []})

            confirmed_values = registry.get_confirmed_values({"test": "hoge"})
            self.assertDictEqual(confirmed_values, {"test": ["hoge"]})

    def test_add_bool_config(self) -> None:
        registry = ConfigRegistry()
        with patch("kumade.config.ConfigRegistry.get_instance", return_value=registry):
            item = ConfigItem("bool", _str_to_bool, False, "Bool item.")

            all_items = registry.get_all_items()
            self.assertNotIn(item, all_items)

            add_bool_config("bool", "Bool item.")

            all_items = registry.get_all_items()
            self.assertIn(item, all_items)

            confirmed_values = registry.get_confirmed_values({})
            self.assertDictEqual(confirmed_values, {"bool": False})

            # test converter

            confirmed_values = registry.get_confirmed_values({"bool": "True"})
            self.assertDictEqual(confirmed_values, {"bool": True})

            confirmed_values = registry.get_confirmed_values({"bool": "true"})
            self.assertDictEqual(confirmed_values, {"bool": True})

            confirmed_values = registry.get_confirmed_values({"bool": "False"})
            self.assertDictEqual(confirmed_values, {"bool": False})

            confirmed_values = registry.get_confirmed_values({"bool": "false"})
            self.assertDictEqual(confirmed_values, {"bool": False})

            with self.assertRaises(RuntimeError):
                registry.get_confirmed_values({"bool": "hoge"})

    def test_add_int_config(self) -> None:
        registry = ConfigRegistry()
        with patch("kumade.config.ConfigRegistry.get_instance", return_value=registry):
            item = ConfigItem("int", int, 1, "Int item.")

            all_items = registry.get_all_items()
            self.assertNotIn(item, all_items)

            add_int_config("int", "Int item.", default_value=1)

            all_items = registry.get_all_items()
            self.assertIn(item, all_items)

            confirmed_values = registry.get_confirmed_values({})
            self.assertDictEqual(confirmed_values, {"int": 1})

            confirmed_values = registry.get_confirmed_values({"int": "10"})
            self.assertDictEqual(confirmed_values, {"int": 10})

    def test_add_float_config(self) -> None:
        registry = ConfigRegistry()
        with patch("kumade.config.ConfigRegistry.get_instance", return_value=registry):
            item = ConfigItem("float", float, 1.0, "Float item.")

            all_items = registry.get_all_items()
            self.assertNotIn(item, all_items)

            add_float_config("float", "Float item.", default_value=1.0)

            all_items = registry.get_all_items()
            self.assertIn(item, all_items)

            confirmed_values = registry.get_confirmed_values({})
            self.assertDictEqual(confirmed_values, {"float": 1.0})

            confirmed_values = registry.get_confirmed_values({"float": "3.14"})
            self.assertDictEqual(confirmed_values, {"float": 3.14})

    def test_add_str_config(self) -> None:
        registry = ConfigRegistry()
        with patch("kumade.config.ConfigRegistry.get_instance", return_value=registry):
            item = ConfigItem("str", str, "dummy", "Str item.")

            all_items = registry.get_all_items()
            self.assertNotIn(item, all_items)

            add_str_config("str", "Str item.", default_value="dummy")

            all_items = registry.get_all_items()
            self.assertIn(item, all_items)

            confirmed_values = registry.get_confirmed_values({})
            self.assertDictEqual(confirmed_values, {"str": "dummy"})

            confirmed_values = registry.get_confirmed_values({"str": "value"})
            self.assertDictEqual(confirmed_values, {"str": "value"})

    def test_add_path_config(self) -> None:
        registry = ConfigRegistry()
        with patch("kumade.config.ConfigRegistry.get_instance", return_value=registry):
            default_path = Path("tmp")
            item = ConfigItem("path", Path, default_path, "Path item.")

            all_items = registry.get_all_items()
            self.assertNotIn(item, all_items)

            add_path_config("path", "Path item.", default_value=default_path)

            all_items = registry.get_all_items()
            self.assertIn(item, all_items)

            confirmed_values = registry.get_confirmed_values({})
            self.assertDictEqual(confirmed_values, {"path": default_path})

            confirmed_values = registry.get_confirmed_values({"path": "hoge"})
            self.assertDictEqual(confirmed_values, {"path": Path("hoge")})

    def test_get_config(self) -> None:
        config = Config({"name": "Taro", "age": 10})
        with patch("kumade.config.Config.get_instance", return_value=config):
            ret = get_config()
            self.assertEqual(ret, config)
