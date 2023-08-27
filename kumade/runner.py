# Task runner

from pathlib import Path
from typing import List, Set

from kumade.manager import TaskManager
from kumade.task import Task, TaskName


class TaskRunner:
    def __init__(self, verbose: bool = False) -> None:
        self.__manager = TaskManager.get_instance()
        self.__verbose = verbose

    def run(self, targets: List[TaskName]) -> None:
        queue = self.__create_queue(targets)
        self.__execute_queue(queue)

    def __create_queue(self, targets: List[TaskName]) -> List[Task]:
        queue: List[Task] = []
        visited: Set[TaskName] = set()
        added: Set[TaskName] = set()
        for target in targets:
            self.__create_queue_recursively(target, queue, visited, added)
        return queue

    def __create_queue_recursively(
        self,
        target: TaskName,
        queue: List[Task],
        visited: Set[TaskName],
        added: Set[TaskName],
    ) -> None:
        if target in visited:
            if target in added:
                return
            else:
                raise RuntimeError(f"Target {target} has circular dependency.")

        task = self.__manager.find(target)
        if task is None:
            # NOTE: A path in dependencies need not be a task.
            if isinstance(target, Path):
                return
            else:
                raise RuntimeError(f"Target {target} is not found.")

        visited.add(target)

        for dep in task.dependencies:
            self.__create_queue_recursively(dep, queue, visited, added)

        queue.append(task)
        added.add(target)

    def __execute_queue(self, queue: List[Task]) -> None:
        for task in queue:
            if self.__verbose:
                print(f"[Task] {task.name}")
            task.run()
