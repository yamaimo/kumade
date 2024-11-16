# Task runner

from pathlib import Path

from kumade.manager import TaskManager
from kumade.task import Task, TaskName


class TaskRunner:
    """
    Task runner.
    """

    def __init__(self, verbose: bool = False) -> None:
        """
        Parameters
        ----------
        verbose : bool, default False
            Whether to display the running task name or not.
        """
        self.__manager = TaskManager.get_instance()
        self.__verbose = verbose

    def run(self, targets: list[TaskName]) -> None:
        """
        Execute specified tasks with considering dependencies.

        Parameters
        ----------
        targets : list[TaskName]
            Target task names or paths to be executed.

        Raises
        ------
        RuntimeError
            If target has circular dependency.
            If target is not found.
            If task execution causes an error.
        """
        queue = self.__create_queue(targets)
        self.__execute_queue(queue)

    def __create_queue(self, targets: list[TaskName]) -> list[Task]:
        queue: list[Task] = []
        visited: set[TaskName] = set()
        added: set[TaskName] = set()
        for target in targets:
            self.__create_queue_recursively(target, queue, visited, added)
        return queue

    def __create_queue_recursively(
        self,
        target: TaskName,
        queue: list[Task],
        visited: set[TaskName],
        added: set[TaskName],
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

    def __execute_queue(self, queue: list[Task]) -> None:
        for task in queue:
            if self.__verbose:
                print(f"[Task] {task.name}")

            try:
                task.run()
            except Exception as e:
                raise RuntimeError(f"Target {task.name} causes an error.") from e
