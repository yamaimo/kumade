__version__ = "0.1.0"

from kumade.decorator import bind_args, depend, file, help, task

__all__ = ["task", "file", "bind_args", "depend", "help"]

# dummy

from typing import Any, List


def create_clean_task(*args: Any) -> List:
    return []
