# Task runner

from typing import List, Set

from kumade.manager import TaskManager
from kumade.task import Task, TaskName


class TaskRunner:
    def __init__(self, verbose: bool = False) -> None:
        self.__manager = TaskManager.get_instance()
        self.__verbose = verbose

    def run(self, target: TaskName) -> None:
        queue = self.__create_queue(target)
        self.__execute_queue(queue)

    def __create_queue(self, target: TaskName) -> List[Task]:
        queue: List[Task] = []
        visited: Set[TaskName] = set()
        added: Set[TaskName] = set()
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
                raise ValueError(f"Target {target} is dependent from its dependencies.")

        task = self.__manager.find(target)
        if task is None:
            raise ValueError(f"Target {target} is not found.")

        visited.add(target)

        for dep in task.dependencies:
            self.__create_queue_recursively(dep, queue, visited, added)

        queue.append(task)
        added.add(target)

    def __execute_queue(self, queue: List[Task]) -> None:
        for task in queue:
            if self.__verbose:
                print(task.name)
            task.run()
