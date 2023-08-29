from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock, patch

from kumade.decorator import bind_args, depend, file, help, task
from kumade.manager import TaskManager


class TestDecorator(TestCase):
    def test_task(self) -> None:
        manager = TaskManager()
        with patch("kumade.manager.TaskManager.get_instance", return_value=manager):
            checker = MagicMock()

            @task("test")
            def procedure() -> None:
                checker()

            registered = manager.find("test")
            self.assertIsNotNone(registered)
            assert registered is not None  # for lint

            registered.run()
            checker.assert_called()

    def test_file(self) -> None:
        manager = TaskManager()
        with patch("kumade.manager.TaskManager.get_instance", return_value=manager):
            checker = MagicMock()

            @file(Path("test.txt"))
            def procedure() -> None:
                checker()

            registered = manager.find(Path("test.txt"))
            self.assertIsNotNone(registered)
            assert registered is not None  # for lint

            registered.run()
            checker.assert_called()

    def test_bind_args(self) -> None:
        manager = TaskManager()
        with patch("kumade.manager.TaskManager.get_instance", return_value=manager):
            i = 0

            checker_without_bind = MagicMock()

            @task("test_without_bind")
            def procedure1() -> None:
                checker_without_bind(i)

            checker_with_bind = MagicMock()

            @task("test_with_bind")
            @bind_args(i)
            def procedure2(i: int) -> None:
                checker_with_bind(i)

            i = 1

            without_bind = manager.find("test_without_bind")
            assert without_bind is not None  # for lint
            without_bind.run()
            checker_without_bind.assert_called_with(1)

            with_bind = manager.find("test_with_bind")
            assert with_bind is not None  # for lint
            with_bind.run()
            checker_with_bind.assert_called_with(0)

    def test_depend(self) -> None:
        manager = TaskManager()
        with patch("kumade.manager.TaskManager.get_instance", return_value=manager):

            @task("test")
            @depend("a", Path("b.txt"))
            def procedure() -> None:
                pass

            registered = manager.find("test")
            assert registered is not None  # for lint

            self.assertEqual(len(registered.dependencies), 2)
            self.assertIn("a", registered.dependencies)
            self.assertIn(Path("b.txt"), registered.dependencies)

    def test_help(self) -> None:
        manager = TaskManager()
        with patch("kumade.manager.TaskManager.get_instance", return_value=manager):

            @task("test")
            @help("Test task.")
            def procedure() -> None:
                pass

            registered = manager.find("test")
            assert registered is not None  # for lint

            self.assertEqual(registered.help, "Test task.")
