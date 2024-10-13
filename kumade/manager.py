# Task manager

from typing import Optional

from kumade.task import Task, TaskName


class TaskManager:
    """
    Task manager.
    """

    __instance: Optional["TaskManager"] = None

    @classmethod
    def get_instance(cls) -> "TaskManager":
        """
        Return the singleton instance of task manager.

        Returns
        -------
        manager : TaskManager
            The instance of task manager.
        """
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance

    def __init__(self) -> None:
        self.__task: dict[TaskName, Task] = {}
        self.__default_task_name: Optional[str] = None

    @property
    def default_task_name(self) -> Optional[str]:
        """
        Default task name.

        Returns
        -------
        name : str
            Name of the default task.
            If not specified default task, return None.
        """
        return self.__default_task_name

    @default_task_name.setter
    def default_task_name(self, name: Optional[str]) -> None:
        """
        Set default task.

        Parameters
        ----------
        name : Optional[str]
            Name of the default task to be set.
        """
        self.__default_task_name = name

    def register(self, task: Task) -> None:
        """
        Register a task.

        Parameters
        ----------
        task : Task
            Task to be registered.

        Raises
        ------
        RuntimeError
            If a task with the same name has already been registered.
        """
        name = task.name
        if name in self.__task:
            raise RuntimeError(f"Task {name} already exists.")
        self.__task[name] = task

    def find(self, name: TaskName) -> Optional[Task]:
        """
        Find a task with the specified name.

        Parameters
        ----------
        name : TaskName
            Name or path of the task to be found.

        Returns
        -------
        task : Optional[Task]
            Found task.
            If not found, return None.
        """
        return self.__task.get(name)

    def get_all_tasks(self) -> list[Task]:
        """
        Return all registered tasks.

        Returns
        -------
        tasks : list[Task]
            List of all registered tasks.
        """
        return list(self.__task.values())

    def get_tasks_described_with_help(self) -> list[Task]:
        """
        Return registered tasks with descriptions.

        Returns
        -------
        tasks : list[Task]
            List of registered tasks with descriptions.
        """
        return list(filter(lambda task: task.has_help, self.__task.values()))
