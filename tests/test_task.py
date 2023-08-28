from unittest import TestCase
from unittest.mock import MagicMock

from kumade.task import Task


class TestTask(TestCase):
    def test_has_help(self) -> None:
        task_with_help = Task("test", lambda: None, [], [], "Test task.")
        self.assertTrue(task_with_help.has_help)

        task_without_help = Task("test", lambda: None, [], [], None)
        self.assertFalse(task_without_help.has_help)

    def test_run(self) -> None:
        procedure = MagicMock()
        task = Task("test", procedure, [], [], None)
        task.run()
        procedure.assert_called_with()

        procedure = MagicMock()
        task = Task("test", procedure, ["a", ["b", "c"]], [], None)
        task.run()
        procedure.assert_called_with("a", ["b", "c"])
