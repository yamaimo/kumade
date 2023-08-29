# Task builder

import shutil
from pathlib import Path
from typing import Any, List, Optional, Protocol

from kumade.task import Task, TaskName, TaskProcedure


class ArgsConfigurable(Protocol):
    def set_args(self, args: List[Any]) -> None:
        ...  # pragma: no cover


class DependenciesConfigurable(Protocol):
    def set_dependencies(self, dependencies: List[TaskName]) -> None:
        ...  # pragma: no cover


class HelpConfigurable(Protocol):
    def set_help(self, help: str) -> None:
        ...  # pragma: no cover


class TaskBuilder(ArgsConfigurable, DependenciesConfigurable, HelpConfigurable):
    def __init__(self, name: str) -> None:
        self.__name = name
        self.__args: List[Any] = []
        self.__dependencies: List[TaskName] = []
        self.__help: Optional[str] = None

    def set_args(self, args: List[Any]) -> None:
        self.__args = args

    def set_dependencies(self, dependencies: List[TaskName]) -> None:
        self.__dependencies = dependencies

    def set_help(self, help: str) -> None:
        self.__help = help

    def build(self, procedure: TaskProcedure) -> Task:
        return Task(
            self.__name,
            procedure,
            self.__args,
            self.__dependencies,
            self.__help,
        )


class FileTaskBuilder(ArgsConfigurable, DependenciesConfigurable):
    def __init__(self, path: Path) -> None:
        self.__path = path
        self.__args: List[Any] = []
        self.__dependencies: List[TaskName] = []

    def set_args(self, args: List[Any]) -> None:
        self.__args = args

    def set_dependencies(self, dependencies: List[TaskName]) -> None:
        self.__dependencies = dependencies

    def build(self, procedure: TaskProcedure) -> Task:
        def procedure_with_file_check(*args: Any) -> None:
            if not self.__path.exists():
                return procedure(*args)
            if self.__path.is_dir():
                return

            timestamp = self.__path.stat().st_mtime
            for dep in self.__dependencies:
                if isinstance(dep, Path) and dep.is_file():
                    dep_timestamp = dep.stat().st_mtime
                    if timestamp < dep_timestamp:
                        return procedure(*args)
            return

        return Task(
            self.__path,
            procedure_with_file_check,
            self.__args,
            self.__dependencies,
            None,
        )


class CleanTaskBuilder(DependenciesConfigurable, HelpConfigurable):
    def __init__(self, name: str) -> None:
        self.__name = name
        self.__dependencies: List[TaskName] = []
        self.__help: Optional[str] = None

    def set_dependencies(self, dependencies: List[TaskName]) -> None:
        self.__dependencies = dependencies

    def set_help(self, help: str) -> None:
        self.__help = help

    def build(self, clean_paths: List[Path]) -> Task:
        def clean_procedure(*paths: Path) -> None:
            for path in paths:
                if path.exists():
                    if path.is_file():
                        path.unlink()
                    elif path.is_dir():
                        shutil.rmtree(path)

        return Task(
            self.__name,
            clean_procedure,
            clean_paths,
            self.__dependencies,
            self.__help,
        )
