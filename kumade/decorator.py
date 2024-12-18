# Decorator to create and register task

from collections.abc import Callable
from pathlib import Path
from typing import Any, Generic, Optional, TypeVar, Union

from kumade.builder import (
    ArgsConfigurable,
    DependenciesConfigurable,
    FileTaskBuilder,
    HelpConfigurable,
    TaskBuilder,
)
from kumade.manager import TaskManager
from kumade.task import TaskName, TaskProcedure

T = TypeVar("T")


class TaskConfig(Generic[T]):
    """
    Decorator class to set up task builder.
    """

    def __init__(
        self,
        base: Union[TaskProcedure, "TaskConfig[T]"],
        config_procedure: Callable[[T], None],
    ) -> None:
        """
        Parameters
        ----------
        base : Union[TaskProcedure, "TaskConfig[T]"]
            Base object to be decorated.
        config_procedure : Callable[[T], None]
            Procedure to set up task builder.
        """
        self.__base = base
        self.__config_procedure = config_procedure

    # NOTE: Make TaskConfig Callable in order to use as Decorator
    def __call__(self) -> None:
        pass  # pragma: no cover

    def setup_builder(self, builder: T) -> TaskProcedure:
        """
        Set up task builder and return task procedure.

        Parameters
        ----------
        builder : T
            Task builder to be set up.
            Type T is a class or a protocol of task builder.

        Returns
        -------
        procedure : TaskProcedure
            Procedure to be executed by the task.
        """
        if isinstance(self.__base, TaskConfig):
            procedure = self.__base.setup_builder(builder)
        else:
            procedure = self.__base
        self.__config_procedure(builder)
        return procedure


def task(name: str) -> Callable:
    """
    Decorator to define and register a normal task.

    Parameters
    ----------
    name : str
        Task name.
    """

    def decorator(base: Union[TaskProcedure, TaskConfig[TaskBuilder]]) -> TaskProcedure:
        task_config: TaskConfig[TaskBuilder] = TaskConfig(base, lambda builder: None)

        builder = TaskBuilder(name)
        procedure = task_config.setup_builder(builder)
        new_task = builder.build(procedure)

        TaskManager.get_instance().register(new_task)

        return procedure

    return decorator


def file(path: Path) -> Callable:
    """
    Decorator to define and register a file creation task.

    Parameters
    ----------
    path : Path
        Path of the file to be created.
    """

    def decorator(
        base: Union[TaskProcedure, TaskConfig[FileTaskBuilder]]
    ) -> TaskProcedure:
        task_config: TaskConfig[FileTaskBuilder] = TaskConfig(
            base, lambda builder: None
        )

        builder = FileTaskBuilder(path)
        procedure = task_config.setup_builder(builder)
        new_task = builder.build(procedure)

        TaskManager.get_instance().register(new_task)

        return procedure

    return decorator


def bind_args(*args: Any) -> Callable:
    """
    Decorator to bind arguments.
    Specified arguments will be passed to task procedure when executing.

    Parameters
    ----------
    *args : Any
        Arguments to be passed to task procedure.
    """

    def decorator(
        base: Union[TaskProcedure, TaskConfig[ArgsConfigurable]]
    ) -> TaskConfig[ArgsConfigurable]:
        return TaskConfig(base, lambda builder: builder.set_args(list(args)))

    return decorator


def depend(*dependencies: Optional[TaskName]) -> Callable:
    """
    Decorator to specify dependencies.

    Parameters
    ----------
    *dependencies : Option[TaskName]
        Task names or paths of depencencies.
    """

    def decorator(
        base: Union[TaskProcedure, TaskConfig[DependenciesConfigurable]]
    ) -> TaskConfig[DependenciesConfigurable]:
        deps: list[TaskName] = [dep for dep in dependencies if dep is not None]
        return TaskConfig(base, lambda builder: builder.set_dependencies(deps))

    return decorator


def help(desc: Optional[str]) -> Callable:
    """
    Decorator to set task description.

    Parameters
    ----------
    desc : Optional[str]
        Task description.
    """

    def decorator(
        base: Union[TaskProcedure, TaskConfig[HelpConfigurable]]
    ) -> TaskConfig[HelpConfigurable]:
        def set_help_if_needed(builder: HelpConfigurable) -> None:
            if desc is not None:
                builder.set_help(desc)

        return TaskConfig(base, set_help_if_needed)

    return decorator
