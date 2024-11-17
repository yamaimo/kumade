# Task worker and runner for multi process

import queue
import traceback
from dataclasses import dataclass
from multiprocessing import Process, Queue
from pathlib import Path
from typing import Any, Optional

from kumade.concurrent.printer import PrintClient, PrintCommand, PrintServer
from kumade.config import Config
from kumade.loader import KumadefileLoader
from kumade.manager import TaskManager
from kumade.task import TaskName


@dataclass(frozen=True)
class TaskCommand:
    """
    Task command.

    Attributes
    ----------
    target : TaskName
        Target task name.
        Empty string means an exit command.
    """

    target: TaskName

    @classmethod
    def exit(cls) -> "TaskCommand":
        """Return an exit command."""
        return cls("")

    @property
    def is_exit(self) -> bool:
        """An exit command or not."""
        return self.target == ""


@dataclass(frozen=True)
class ExecutionResult:
    """
    Execution result.

    Attributes
    ----------
    target : TaskName
        Target task name.
    error : Optional[RuntimeError], default None
        Error that occurred when executing task.
    """

    target: TaskName
    error: Optional[RuntimeError] = None


class TaskWorker:
    """
    Task worker.
    """

    def __init__(
        self,
        kumadefile: Path,
        config_values: dict[str, Any],
        print_client: PrintClient,
        request_queue: Queue,
        notify_queue: Queue,
        verbose: bool = False,
    ) -> None:
        """
        Parameters
        ----------
        kumadefile : Path
            Path of kumadefile to be loaded.
        config_values : dict[str, Any]
            Confirmed configuration values.
        print_client : PrintClient
            Print client.
        request_queue : Queue
            Queue for receiving task commands from task runner.
        notify_queue : Queue
            Queue for notifying task completion to task runner.
        verbose : bool, default False
            Whether to display the running task name or not.
        """
        self.__kumadefile = kumadefile
        self.__config_values = config_values
        self.__print_client = print_client
        self.__request_queue = request_queue
        self.__notify_queue = notify_queue
        self.__verbose = verbose
        self.__process: Optional[Process] = None

    def start(self) -> None:
        """Start task worker process."""
        if self.__process is not None:
            return

        self.__process = Process(target=self)
        self.__process.start()

    def stop(self) -> None:
        """Stop task worker process."""
        if self.__process is None:
            return

        self.__request_queue.put(TaskCommand.exit())
        self.__process.join()
        self.__process = None

    def __call__(self) -> None:
        """Main for task worker process."""
        self.__setup_global_objects()
        manager = TaskManager.get_instance()
        with self.__print_client:
            while True:
                command = self.__request_queue.get()
                if command.is_exit:
                    # Spread the exit command to other worker before exiting,
                    # because it may be intended for others.
                    self.__request_queue.put(command)
                    return
                result = self.__execute_target(manager, command.target)
                self.__notify_queue.put(result)

    def __setup_global_objects(self) -> None:
        # Spawned process doesn't have the task objects (and config values)
        # which are defined and registered by loading kumadefile.
        # (Forked process has them because 'fork' creates the copy of process.)
        # So load kumadefile in this process again if necessary.

        loader = KumadefileLoader.get_instance()
        is_spawned_process = loader.loaded_kumadefile is None
        if is_spawned_process:
            loader.load(self.__kumadefile)
            Config.set(self.__config_values)

    def __execute_target(
        self, manager: TaskManager, target: TaskName
    ) -> ExecutionResult:
        try:
            task = manager.find(target)
            if task is None:
                # NOTE: A path in dependencies need not be a task.
                if isinstance(target, Path):
                    return ExecutionResult(target)
                else:
                    raise RuntimeError(f"Target {target} is not found.")

            if self.__verbose:
                print(f"[Task] {task.name}")

            try:
                task.run()
            except Exception as e:
                raise RuntimeError(f"Target {target} causes an error.") from e

            return ExecutionResult(target)
        except RuntimeError as e:
            # Task runner can not show stack trace, so print stack trace here.
            print(traceback.format_exc())
            return ExecutionResult(target, e)


class ConcurrentTaskRunner:
    """
    Task runner for multi process.
    """

    @classmethod
    def create(cls, n_workers: int, verbose: bool = False) -> "ConcurrentTaskRunner":
        """
        Create a concurrent task runner.

        This method also creates a print server and task workers.

        Parameters
        ----------
        n_workers : int
            The number of worker processes.
        verbose : bool, default False
            Whether to display the running task name or not.

        Returns
        -------
        runner : ConcurrentTaskRunner
            Created task runner.
        """
        loader = KumadefileLoader.get_instance()
        kumadefile = loader.loaded_kumadefile
        assert kumadefile is not None

        config = Config.get_instance()
        config_values = config.values

        print_queue: Queue[PrintCommand] = Queue()
        print_server = PrintServer(print_queue)

        request_queue: Queue[TaskCommand] = Queue()
        notify_queue: Queue[ExecutionResult] = Queue()

        workers: list[TaskWorker] = []
        for i in range(n_workers):
            print_client = print_server.create_client(f"Worker{i}")
            worker = TaskWorker(
                kumadefile,
                config_values,
                print_client,
                request_queue,
                notify_queue,
                verbose,
            )
            workers.append(worker)

        return cls(print_server, workers, request_queue, notify_queue)

    def __init__(
        self,
        print_server: PrintServer,
        workers: list[TaskWorker],
        request_queue: Queue,
        notify_queue: Queue,
    ) -> None:
        """
        Parameters
        ----------
        print_server : PrintServer
            Print server.
        workers : list[TaskWorker]
            List of task workers.
        request_queue : Queue
            Queue for requesting task worker to run tasks.
        notify_queue : Queue
            Queue for receiving notification from task worker.
        """
        self.__print_server = print_server
        self.__workers = workers
        self.__request_queue = request_queue
        self.__notify_queue = notify_queue
        self.__manager = TaskManager.get_instance()

    def run(self, targets: list[TaskName]) -> None:
        """
        Execute specified tasks with considering dependencies.

        Parameters
        ----------
        targets : list[TaskName]
            Target task names or paths to be executed.

        Raises
        ------
        RuntimeError
            If target has circular dependency.
            If target is not found.
            If task execution causes an error.
        """
        try:
            deps_count = self.__create_dependencies_count(targets)
            self.__start_workers()
            self.__dispatch_tasks(deps_count)
        finally:
            self.__stop_workers()

    def __start_workers(self) -> None:
        self.__print_server.start()
        for worker in self.__workers:
            worker.start()

    def __stop_workers(self) -> None:
        # Clear request queue.
        try:
            while True:
                # If request queue is empty, raises queue.Empty exception.
                self.__request_queue.get_nowait()
        except queue.Empty:
            pass

        for worker in self.__workers:
            worker.stop()
        self.__print_server.stop()

    def __create_dependencies_count(
        self, targets: list[TaskName]
    ) -> dict[TaskName, int]:
        deps_count: dict[TaskName, int] = {}
        visited: set[TaskName] = set()
        added: set[TaskName] = set()
        for target in targets:
            self.__create_deps_count_recursively(target, deps_count, visited, added)
        return deps_count

    def __create_deps_count_recursively(
        self,
        target: TaskName,
        deps_count: dict[TaskName, int],
        visited: set[TaskName],
        added: set[TaskName],
    ) -> int:
        if target in visited:
            if target in added:
                return 1
            else:
                raise RuntimeError(f"Target {target} has circular dependency.")

        task = self.__manager.find(target)
        if task is None:
            # NOTE: A path in dependencies need not be a task.
            if isinstance(target, Path):
                return 0
            else:
                raise RuntimeError(f"Target {target} is not found.")

        visited.add(target)

        count = 0
        for dep in task.dependencies:
            count += self.__create_deps_count_recursively(
                dep, deps_count, visited, added
            )

        deps_count[target] = count
        added.add(target)
        return 1

    def __dispatch_tasks(self, deps_count: dict[TaskName, int]) -> None:
        n_rest_tasks = len(deps_count)
        while n_rest_tasks > 0:
            # Request non-blocked tasks to run.
            next_deps_count = dict(deps_count)
            for target, count in deps_count.items():
                if count == 0:
                    del next_deps_count[target]
                    command = TaskCommand(target)
                    self.__request_queue.put(command)
            deps_count = next_deps_count

            # Wait task completion.
            result = self.__notify_queue.get()
            if result.error is not None:
                raise result.error
            completed_target = result.target
            n_rest_tasks -= 1

            # Update dependencies count.
            for target in deps_count:
                task = self.__manager.find(target)
                assert task is not None
                if completed_target in task.dependencies:
                    deps_count[target] -= 1
