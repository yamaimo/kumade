# CLI

import importlib.util
import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import List, Tuple

import kumade
from kumade.manager import TaskManager
from kumade.runner import TaskRunner
from kumade.task import Task, TaskName


class CLI:
    @classmethod
    def create(cls) -> "CLI":
        option = cls.__parse_args()

        if option.file is not None:
            kumadefile = Path(option.file)
            if not kumadefile.exists():
                raise RuntimeError(f"File {kumadefile} does not exist.")
        else:
            kumadefile = cls.__search_kumadefile(Path().absolute())

        shows_tasks = option.tasks or option.alltasks
        shows_all = option.alltasks

        manager = TaskManager.get_instance()

        return cls(
            manager,
            kumadefile,
            shows_tasks,
            shows_all,
            option.verbose,
            option.targets,
        )

    @classmethod
    def __parse_args(cls) -> Namespace:
        parser = ArgumentParser(description="A make-like build utility for Python.")
        parser.add_argument("--version", action="version", version=kumade.__version__)

        parser.add_argument(
            "-f", "--file", metavar="FILE", help="use FILE as a Kumadefile"
        )
        parser.add_argument(
            "-t", "--tasks", action="store_true", help="show tasks and exit"
        )
        parser.add_argument(
            "-T",
            "--alltasks",
            action="store_true",
            help="show all tasks (including no description) and exit",
        )
        parser.add_argument(
            "-v", "--verbose", action="store_true", help="show task name at running"
        )
        parser.add_argument("targets", nargs="*", help="targets to run")

        return parser.parse_args()

    @classmethod
    def __search_kumadefile(cls, current_dir: Path) -> Path:
        for filename in ["Kumadefile.py", "kumadefile.py"]:
            path = current_dir / filename
            if path.exists():
                return path

        parent_dir = current_dir.parent
        if current_dir == parent_dir:
            raise RuntimeError("Kumadefile.py is not found.")
        else:
            return cls.__search_kumadefile(parent_dir)

    def __init__(
        self,
        manager: TaskManager,
        kumadefile: Path,
        shows_tasks: bool,
        shows_all: bool,
        verbose: bool,
        targets: List[str],
    ) -> None:
        self.__manager = manager
        self.__kumadefile = kumadefile
        self.__shows_tasks = shows_tasks
        self.__shows_all = shows_all
        self.__verbose = verbose
        self.__targets = targets

    def run(self) -> None:
        self.__load_kumadefile()

        if self.__shows_tasks:
            self.__show_tasks()
            return

        if len(self.__targets) == 0:
            default_task_name = self.__manager.default_task_name
            if default_task_name is None:
                raise RuntimeError("No target is specified.")
            self.__targets.append(default_task_name)

        targets_to_run: List[TaskName] = []
        for target in self.__targets:
            if self.__manager.find(target):
                targets_to_run.append(target)
            else:
                target_path = Path(target).absolute()
                if self.__manager.find(target_path):
                    targets_to_run.append(target_path)
                else:
                    raise RuntimeError(f"Unknown target '{target}' is specified.")

        runner = TaskRunner(self.__verbose)
        runner.run(targets_to_run)

    def __load_kumadefile(self) -> None:
        # NOTE: https://docs.python.org/3/library/importlib.html#importing-a-source-file-directly
        module_name = "kumadefile"
        spec = importlib.util.spec_from_file_location(module_name, self.__kumadefile)
        assert spec is not None
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        assert spec.loader is not None and spec.loader.exec_module is not None
        spec.loader.exec_module(module)

    def __show_tasks(self) -> None:
        if self.__shows_all:
            tasks = self.__manager.get_all_tasks()
        else:
            tasks = self.__manager.get_tasks_described_with_help()

        len_of_names = [len(str(task.name)) for task in tasks if task.has_help]
        name_width = max(len_of_names) + 2

        def get_sort_key(task: Task) -> Tuple[int, str]:
            if task.has_help:
                priority = 0
            elif isinstance(task.name, str):
                priority = 1
            else:
                priority = 2
            return (priority, str(task.name))

        sorted_tasks = sorted(tasks, key=get_sort_key)
        for task in sorted_tasks:
            if task.has_help:
                padding = " " * (name_width - len(str(task.name)))
                print(f"{task.name}{padding}# {task.help}")
            elif isinstance(task.name, str):
                print(task.name)
            else:
                print(f"(Path) {task.name}")


def main() -> None:
    cli = CLI.create()
    cli.run()


if __name__ == "__main__":
    main()
