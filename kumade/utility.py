# Utility to create and register task

from pathlib import Path
from typing import List, Optional

from kumade.builder import CleanTaskBuilder, FileTaskBuilder
from kumade.manager import TaskManager
from kumade.task import TaskName


def set_default(name: str) -> None:
    manager = TaskManager.get_instance()
    manager.default_task_name = name


def clean(
    name: str,
    paths: List[Path],
    dependencies: Optional[List[TaskName]] = None,
    help: Optional[str] = None,
) -> None:
    builder = CleanTaskBuilder(name)

    if dependencies is not None:
        builder.set_dependencies(dependencies)
    if help is not None:
        builder.set_help(help)

    new_task = builder.build(paths)
    TaskManager.get_instance().register(new_task)


def directory(
    path: Path,
    dependencies: Optional[List[TaskName]] = None,
) -> None:
    builder = FileTaskBuilder(path)

    builder.set_args([path])
    if dependencies is not None:
        builder.set_dependencies(dependencies)

    new_task = builder.build(lambda path: path.mkdir(parents=True))
    TaskManager.get_instance().register(new_task)
