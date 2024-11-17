# CLI

from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Optional

import kumade
from kumade.concurrent.runner import ConcurrentTaskRunner
from kumade.config import Config, ConfigRegistry
from kumade.loader import KumadefileLoader
from kumade.manager import TaskManager
from kumade.runner import TaskRunner
from kumade.task import Task, TaskName


class CLI:
    """
    Command Line Interface.
    """

    @classmethod
    def create(cls) -> "CLI":
        """
        Parse command line arguments and create a CLI instance.

        Returns
        -------
        cli : CLI
            Created CLI instance.
        """
        option = cls.__parse_args()

        if option.file is not None:
            kumadefile = Path(option.file)
            if not kumadefile.exists():
                raise RuntimeError(f"File {kumadefile} does not exist.")
        else:
            kumadefile = None

        shows_tasks = option.tasks or option.alltasks
        shows_all = option.alltasks

        n_workers: Optional[int] = None
        if option.jobs is not None:
            n_workers = int(option.jobs)

        # Separate config_and_targets into config and targets.
        config: dict[str, str] = {}
        targets: list[str] = []
        for item in option.config_and_targets:
            if "=" in item:
                name, value = item.split("=")
                config[name] = value
            else:
                targets.append(item)

        loader = KumadefileLoader.get_instance()
        registry = ConfigRegistry.get_instance()
        manager = TaskManager.get_instance()

        return cls(
            loader,
            registry,
            manager,
            kumadefile,
            shows_tasks,
            shows_all,
            n_workers,
            option.verbose,
            config,
            targets,
        )

    @classmethod
    def __parse_args(cls) -> Namespace:
        parser = ArgumentParser(description="A make-like build utility for Python.")
        parser.add_argument("--version", action="version", version=kumade.__version__)

        parser.add_argument(
            "-f", "--file", metavar="FILE", help="use FILE as a Kumadefile"
        )
        parser.add_argument(
            "-t",
            "--tasks",
            action="store_true",
            help="show config items and tasks, and exit",
        )
        parser.add_argument(
            "-T",
            "--alltasks",
            action="store_true",
            help="show config items and all tasks (including no description), and exit",
        )
        parser.add_argument(
            "-j",
            "--jobs",
            metavar="N",
            help="execute tasks concurrently with N workers",
        )
        parser.add_argument(
            "-v", "--verbose", action="store_true", help="show task name at running"
        )
        # NOTE: All config and targets will be pushed in 'config_and_targets'.
        # 'targets' is pseudo argument for help message.
        parser.add_argument(
            "config_and_targets",
            nargs="*",
            help="configurations",
            metavar="config=value",
        )
        parser.add_argument("targets", nargs="*", help="targets to run")

        return parser.parse_args()

    def __init__(
        self,
        loader: KumadefileLoader,
        registry: ConfigRegistry,
        manager: TaskManager,
        kumadefile: Optional[Path],
        shows_tasks: bool,
        shows_all: bool,
        n_workers: Optional[int],
        verbose: bool,
        config: dict[str, str],
        targets: list[str],
    ) -> None:
        """
        Parameters
        ----------
        loader : KumadefileLoader
            Kumadefile loader.
        registry : ConfigRegistry
            Config registry.
        manager : TaskManager
            Task manager.
        kumadefile : Optional[Path]
            Path of Kumadefile.py.
        shows_tasks : bool
            If true, show available task names and exit.
        shows_all : bool
            Whether to show all task names or not.
            If false, only task names with descriptions are shown.
        n_workers : Optional[int]
            The number of worker processes.
            If None or less than 2, no concurrent execution.
        verbose : bool
            Whether to display the running task name or not.
        config : dict[str, str]
            User specified values for configuration items.
        targets : list[str]
            Target task names to be executed.
        """
        self.__loader = loader
        self.__registry = registry
        self.__manager = manager
        self.__kumadefile = kumadefile
        self.__shows_tasks = shows_tasks
        self.__shows_all = shows_all
        self.__n_workers = n_workers
        self.__verbose = verbose
        self.__config = config
        self.__targets = targets

    def run(self) -> None:
        """
        Run CLI and execute target tasks with considering dependencies.
        """
        self.__loader.load(self.__kumadefile)

        if self.__shows_tasks:
            self.__show_config_items()
            self.__show_tasks()
            return

        confirmed_values = self.__registry.get_confirmed_values(self.__config)
        Config.set(confirmed_values)

        if len(self.__targets) == 0:
            default_task_name = self.__manager.default_task_name
            if default_task_name is None:
                raise RuntimeError("No target is specified.")
            self.__targets.append(default_task_name)

        targets_to_run: list[TaskName] = []
        for target in self.__targets:
            if self.__manager.find(target):
                targets_to_run.append(target)
            else:
                target_path = Path(target).absolute()
                if self.__manager.find(target_path):
                    targets_to_run.append(target_path)
                else:
                    raise RuntimeError(f"Unknown target '{target}' is specified.")

        if (self.__n_workers is None) or (self.__n_workers < 2):
            runner = TaskRunner(self.__verbose)
            runner.run(targets_to_run)
        else:
            concurrent_runner = ConcurrentTaskRunner.create(self.__n_workers)
            concurrent_runner.run(targets_to_run)

    def __show_config_items(self) -> None:
        print("Configuration items:")

        items = self.__registry.get_all_items()

        if len(items) == 0:
            print("  (None)")
            return

        len_of_names = [len(item.name) for item in items]
        name_width = max(len_of_names) + 2

        sorted_items = sorted(items, key=lambda item: item.name)

        for item in sorted_items:
            padding = " " * (name_width - len(item.name))
            print(
                f"  {item.name}{padding}# {item.help} (default: {item.default_value})"
            )

    def __show_tasks(self) -> None:
        print("Tasks:")

        if self.__shows_all:
            tasks = self.__manager.get_all_tasks()
        else:
            tasks = self.__manager.get_tasks_described_with_help()

        len_of_names = [len(str(task.name)) for task in tasks if task.has_help]
        name_width = max(len_of_names) + 2

        def get_sort_key(task: Task) -> tuple[int, str]:
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
                print(f"  {task.name}{padding}# {task.help}")
            elif isinstance(task.name, str):
                print(f"  {task.name}")
            else:
                print(f"  (Path) {task.name}")


def main() -> None:
    cli = CLI.create()
    cli.run()


if __name__ == "__main__":
    main()
