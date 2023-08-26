# Task

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, List, Optional, Union

TaskName = Union[str, Path]
TaskProcedure = Callable[..., None]


@dataclass(frozen=True)
class Task:
    name: TaskName
    procedure: TaskProcedure
    args: List[Any]
    dependencies: List[TaskName]
    help: Optional[str]

    def run(self) -> None:
        self.procedure(*self.args)
