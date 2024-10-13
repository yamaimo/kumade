# Task

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional, Union

TaskName = Union[str, Path]
TaskProcedure = Callable[..., None]


@dataclass(frozen=True)
class Task:
    """
    Task.

    Attributes
    ----------
    name : TaskName
        Task name or path.
    procedure : TaskProcedure
        Procedure to be executed.
    args : list[Any]
        Arguments to be passed to procedure.
    dependencies : list[TaskName]
        Task names or paths of depencencies.
    help : Optional[str]
        Task description.
    """

    name: TaskName
    procedure: TaskProcedure
    args: list[Any]
    dependencies: list[TaskName]
    help: Optional[str]

    @property
    def has_help(self) -> bool:
        """
        Whether the task has a description.

        Returns
        -------
        bool
            return True if the task has a description.
        """
        return self.help is not None

    def run(self) -> None:
        """
        Execute task procedure.
        """
        self.procedure(*self.args)
