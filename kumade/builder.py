# Task builder

import shutil
from pathlib import Path
from typing import Any, Optional, Protocol

from kumade.task import Task, TaskName, TaskProcedure


class ArgsConfigurable(Protocol):
    """
    Protocol for task builder which can set arguments for task.
    """

    def set_args(self, args: list[Any]) -> None:
        """
        Set arguments for task.

        Parameters
        ----------
        args : list[Any]
            Arguments to be set.
        """
        ...  # pragma: no cover


class DependenciesConfigurable(Protocol):
    """
    Protocol for task builder which can set dependencies for task.
    """

    def set_dependencies(self, dependencies: list[TaskName]) -> None:
        """
        Set dependencies for task.

        Parameters
        ----------
        dependencies : list[TaskName]
            Dependencies to be set.
        """
        ...  # pragma: no cover


class HelpConfigurable(Protocol):
    """
    Protocol for task builder which can set task description.
    """

    def set_help(self, help: str) -> None:
        """
        Set task description.

        Parameters
        ----------
        help : str
            Task description to be set.
        """
        ...  # pragma: no cover


class TaskBuilder(ArgsConfigurable, DependenciesConfigurable, HelpConfigurable):
    """
    Builder for normal task.
    """

    def __init__(self, name: str) -> None:
        """
        Parameters
        ----------
        name : str
            Task name.
        """
        self.__name = name
        self.__args: list[Any] = []
        self.__dependencies: list[TaskName] = []
        self.__help: Optional[str] = None

    def set_args(self, args: list[Any]) -> None:
        """
        Set arguments for task.

        Parameters
        ----------
        args : list[Any]
            Arguments to be set.
        """
        self.__args = args

    def set_dependencies(self, dependencies: list[TaskName]) -> None:
        """
        Set dependencies for task.

        Parameters
        ----------
        dependencies : list[TaskName]
            Dependencies to be set.
        """
        self.__dependencies = dependencies

    def set_help(self, help: str) -> None:
        """
        Set task description.

        Parameters
        ----------
        help : str
            Task description to be set.
        """
        self.__help = help

    def build(self, procedure: TaskProcedure) -> Task:
        """
        Build a task with specified settings.

        Parameters
        ----------
        procedure : TaskProcedure
            Procedure to be executed by the task.

        Returns
        -------
        task : Task
            Built task.
        """
        return Task(
            self.__name,
            procedure,
            self.__args,
            self.__dependencies,
            self.__help,
        )


class FileTaskBuilder(ArgsConfigurable, DependenciesConfigurable):
    """
    Builder for file creation task.
    """

    def __init__(self, path: Path) -> None:
        """
        Parameters
        ----------
        path : Path
            Path of the file to be created.
        """
        self.__path = path
        self.__args: list[Any] = []
        self.__dependencies: list[TaskName] = []

    def set_args(self, args: list[Any]) -> None:
        """
        Set arguments for task.

        Parameters
        ----------
        args : list[Any]
            Arguments to be set.
        """
        self.__args = args

    def set_dependencies(self, dependencies: list[TaskName]) -> None:
        """
        Set dependencies for task.

        Parameters
        ----------
        dependencies : list[TaskName]
            Dependencies to be set.
        """
        self.__dependencies = dependencies

    def build(self, procedure: TaskProcedure) -> Task:
        """
        Build a file creation task with specified settings.

        Parameters
        ----------
        procedure : TaskProcedure
            Procedure to create the target file.

        Returns
        -------
        task : Task
            Built task for file creation.
        """

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
    """
    Builder for file deletion task.
    """

    def __init__(self, name: str) -> None:
        """
        Parameters
        ----------
        name : str
            Task name.
        """
        self.__name = name
        self.__dependencies: list[TaskName] = []
        self.__help: Optional[str] = None

    def set_dependencies(self, dependencies: list[TaskName]) -> None:
        """
        Set dependencies for task.

        Parameters
        ----------
        dependencies : list[TaskName]
            Dependencies to be set.
        """
        self.__dependencies = dependencies

    def set_help(self, help: str) -> None:
        """
        Set task description.

        Parameters
        ----------
        help : str
            Task description to be set.
        """
        self.__help = help

    def build(self, clean_paths: list[Path]) -> Task:
        """
        Build a file deletion task with specified settings.

        Parameters
        ----------
        clean_paths : list[Path]
            Paths of the files to be deleted by the task.

        Returns
        -------
        task : Task
            Built task for file deletion.
        """

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
