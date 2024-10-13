# Utility to create and register task

from pathlib import Path
from typing import Optional

from kumade.builder import CleanTaskBuilder, FileTaskBuilder
from kumade.manager import TaskManager
from kumade.task import TaskName


def set_default(name: str) -> None:
    """
    Set default task.

    Parameters
    ----------
    name : str
        Name of the default task to be set.
    """
    manager = TaskManager.get_instance()
    manager.default_task_name = name


def clean(
    name: str,
    paths: list[Path],
    dependencies: Optional[list[TaskName]] = None,
    help: Optional[str] = None,
) -> None:
    """
    Define and register a file deletion task.

    Parameters
    ----------
    name : str
        Task name.
    paths : list[Path]
        Paths of the files to be deleted.
    dependencies : Optional[list[TaskName]], default None
        Dependencies.
    help : Optional[str], default None
        Task description.
    """
    builder = CleanTaskBuilder(name)

    if dependencies is not None:
        builder.set_dependencies(dependencies)
    if help is not None:
        builder.set_help(help)

    new_task = builder.build(paths)
    TaskManager.get_instance().register(new_task)


def directory(
    path: Path,
    dependencies: Optional[list[TaskName]] = None,
) -> None:
    """
    Define and register a directory creation task.

    Parameters
    ----------
    path : Path
        Path of the directory to be created.
    dependencies : Optional[list[TaskName]], default None
        Dependencies.
    """
    builder = FileTaskBuilder(path)

    builder.set_args([path])
    if dependencies is not None:
        builder.set_dependencies(dependencies)

    new_task = builder.build(lambda path: path.mkdir(parents=True))
    TaskManager.get_instance().register(new_task)
