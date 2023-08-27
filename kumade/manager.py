# Task manager

from typing import Dict, List, Optional

from kumade.task import Task, TaskName


class TaskManager:
    __instance: Optional["TaskManager"] = None

    @classmethod
    def get_instance(cls) -> "TaskManager":
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance

    def __init__(self) -> None:
        self.__task: Dict[TaskName, Task] = {}
        self.__default_task_name: Optional[str] = None

    @property
    def default_task_name(self) -> Optional[str]:
        return self.__default_task_name

    @default_task_name.setter
    def default_task_name(self, value: Optional[str]) -> None:
        self.__default_task_name = value

    def register(self, task: Task) -> None:
        name = task.name
        if name in self.__task:
            raise RuntimeError(f"Task {name} already exists.")
        self.__task[name] = task

    def find(self, name: TaskName) -> Optional[Task]:
        return self.__task.get(name)

    def get_all_tasks(self) -> List[Task]:
        return list(self.__task.values())

    def get_tasks_described_with_help(self) -> List[Task]:
        return list(filter(lambda task: task.has_help, self.__task.values()))
