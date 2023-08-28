from unittest import TestCase
from unittest.mock import MagicMock

from kumade.builder import TaskBuilder


class TestTaskBuilder(TestCase):
    def test_build_with_setter(self) -> None:
        procedure = MagicMock()

        builder = TaskBuilder("test")
        builder.set_args(["a", ["b", "c"]])
        builder.set_dependencies(["task1", "task2"])
        builder.set_help("Test task.")
        task = builder.build(procedure)

        self.assertEqual(task.name, "test")
        self.assertEqual(task.args, ["a", ["b", "c"]])
        self.assertEqual(task.dependencies, ["task1", "task2"])
        self.assertEqual(task.help, "Test task.")

        task.run()
        procedure.assert_called_with("a", ["b", "c"])

    def test_build_without_setter(self) -> None:
        procedure = MagicMock()

        builder = TaskBuilder("test")
        task = builder.build(procedure)

        self.assertEqual(task.name, "test")
        self.assertEqual(task.args, [])
        self.assertEqual(task.dependencies, [])
        self.assertEqual(task.help, None)

        task.run()
        procedure.assert_called_with()
