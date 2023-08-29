from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from kumade.manager import TaskManager
from kumade.utility import clean, directory, set_default


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
