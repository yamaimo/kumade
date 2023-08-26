__version__ = "0.1.0"

# dummy

from typing import Any, Callable, List


def task(*args: Any) -> Callable:
    return lambda: ()


def help(*args: Any) -> Callable:
    return lambda: ()


def depend(*args: Any) -> Callable:
    return lambda: ()


def bind_args(*args: Any) -> Callable:
    return lambda: ()


def file(*args: Any) -> Callable:
    return lambda: ()


def create_clean_task(*args: Any) -> List:
    return []
