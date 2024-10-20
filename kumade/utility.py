# Utility to create and register task, define and get configuration.

from pathlib import Path
from typing import Optional, TypeVar

from kumade.builder import CleanTaskBuilder, FileTaskBuilder
from kumade.config import Config, ConfigItem, ConfigRegistry, Converter
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


T = TypeVar("T")


def add_config(
    name: str,
    converter: Converter[T],
    default_value: T,
    help: str,
) -> None:
    """
    Add a configuration item.

    Parameters
    ----------
    name : str
        Name of item.
    converter : Converter[T]
        Convert function from str to type of item value.
    default_value : T
        Default value.
    help : str
        Description of item.
    """
    item = ConfigItem(name, converter, default_value, help)
    ConfigRegistry.get_instance().add_item(item)


def _str_to_bool(value: str) -> bool:
    value = value.lower()
    if value == "true":
        return True
    elif value == "false":
        return False
    else:
        raise RuntimeError(f"Can't convert '{value}' to bool.")


def add_bool_config(name: str, help: str, default_value: bool = False) -> None:
    """
    Add a bool configuration item.

    Parameters
    ----------
    name : str
        Name of item.
    help : str
        Description of item.
    default_value : bool, default False
        Default value.
    """
    item = ConfigItem(name, _str_to_bool, default_value, help)
    ConfigRegistry.get_instance().add_item(item)


def add_int_config(name: str, help: str, default_value: int = 0) -> None:
    """
    Add an int configuration item.

    Parameters
    ----------
    name : str
        Name of item.
    help : str
        Description of item.
    default_value : int, default 0
        Default value.
    """
    item = ConfigItem(name, int, default_value, help)
    ConfigRegistry.get_instance().add_item(item)


def add_float_config(name: str, help: str, default_value: float = 0.0) -> None:
    """
    Add a float configuration item.

    Parameters
    ----------
    name : str
        Name of item.
    help : str
        Description of item.
    default_value : float, default 0.0
        Default value.
    """
    item = ConfigItem(name, float, default_value, help)
    ConfigRegistry.get_instance().add_item(item)


def add_str_config(name: str, help: str, default_value: str = "") -> None:
    """
    Add a string configuration item.

    Parameters
    ----------
    name : str
        Name of item.
    help : str
        Description of item.
    default_value : str, default ""
        Default value.
    """
    item = ConfigItem(name, str, default_value, help)
    ConfigRegistry.get_instance().add_item(item)


def add_path_config(name: str, help: str, default_value: Path = Path()) -> None:
    """
    Add a path configuration item.

    Parameters
    ----------
    name : str
        Name of item.
    help : str
        Description of item.
    default_value : Path, default current directory.
        Default value.
    """
    item = ConfigItem(name, Path, default_value, help)
    ConfigRegistry.get_instance().add_item(item)


def get_config() -> Config:
    """
    Get confirmed configuration.
    Note that this method can only be used in task procedure.

    Returns
    -------
    config : Config
        Confirmed configuration.

    Raises
    ------
    RuntimeError
        If the configuration is not confirmed.
    """
    return Config.get_instance()
