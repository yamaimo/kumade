from pathlib import Path
from typing import Optional
from unittest import TestCase
from unittest.mock import MagicMock

from kumade.builder import FileTaskBuilder, TaskBuilder
from kumade.manager import TaskManager


class TestTaskManager(TestCase):
    def test_get_instance(self) -> None:
        manager = TaskManager.get_instance()
        another = TaskManager.get_instance()
        self.assertEqual(manager, another)

    def test_default_task_name(self) -> None:
        manager = TaskManager()

        default_task_name: Optional[str] = manager.default_task_name
        self.assertIsNone(default_task_name)

        manager.default_task_name = "test"
        self.assertEqual(manager.default_task_name, "test")

    def test_register_and_find(self) -> None:
        manager = TaskManager()

        task1 = TaskBuilder("task1").build(MagicMock())
        task2 = FileTaskBuilder(Path("test.txt")).build(MagicMock())
        task3 = TaskBuilder("task3").build(MagicMock())

        manager.register(task1)
        manager.register(task2)
        manager.register(task3)

        found = manager.find("task1")
        self.assertEqual(found, task1)

        found = manager.find(Path("test.txt"))
        self.assertEqual(found, task2)

        found = manager.find("task3")
        self.assertEqual(found, task3)

    def test_register_with_same_task_name(self) -> None:
        manager = TaskManager()

        task = TaskBuilder("task").build(MagicMock())
        another = TaskBuilder("task").build(MagicMock())
        assert task != another

        manager.register(task)
        with self.assertRaises(RuntimeError):
            manager.register(another)

    def test_find_with_not_registered_name(self) -> None:
        manager = TaskManager()

        found = manager.find("hoge")
        self.assertIsNone(found)

        found = manager.find(Path("test.txt"))
        self.assertIsNone(found)

    def test_get_all_tasks(self) -> None:
        manager = TaskManager()

        task1 = TaskBuilder("task1").build(MagicMock())
        task2 = FileTaskBuilder(Path("test.txt")).build(MagicMock())
        task3 = TaskBuilder("task3").build(MagicMock())

        manager.register(task1)
        manager.register(task2)
        manager.register(task3)

        all_tasks = manager.get_all_tasks()
        self.assertEqual(len(all_tasks), 3)
        self.assertIn(task1, all_tasks)
        self.assertIn(task2, all_tasks)
        self.assertIn(task3, all_tasks)

    def test_tasks_described_with_help(self) -> None:
        manager = TaskManager()

        task1 = TaskBuilder("task1").build(MagicMock())
        task2 = FileTaskBuilder(Path("test.txt")).build(MagicMock())

        builder = TaskBuilder("task3")
        builder.set_help("Task3")
        task3 = builder.build(MagicMock())

        manager.register(task1)
        manager.register(task2)
        manager.register(task3)

        described_tasks = manager.get_tasks_described_with_help()
        self.assertEqual(len(described_tasks), 1)
        self.assertIn(task3, described_tasks)
