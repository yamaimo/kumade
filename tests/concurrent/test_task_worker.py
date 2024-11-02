from collections.abc import Generator
from contextlib import contextmanager
from multiprocessing import Queue
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from kumade.concurrent.printer import PrintClient, PrintCommand
from kumade.concurrent.runner import TaskCommand, TaskWorker
from kumade.loader import KumadefileLoader
from kumade.manager import TaskManager

ASSETS_DIR = Path(__file__).absolute().parent.parent / "assets"


@contextmanager
def setup() -> Generator[tuple[KumadefileLoader, TaskManager], None, None]:
    loader = KumadefileLoader()
    manager = TaskManager()
    with patch("kumade.loader.KumadefileLoader.get_instance", return_value=loader):
        with patch("kumade.manager.TaskManager.get_instance", return_value=manager):
            # NOTE: Make Config.set() dummy.
            with patch("kumade.config.Config.set"):
                yield (loader, manager)


class TestTaskWorker(TestCase):
    def test_start_and_stop(self) -> None:
        with setup():
            kumadefile = ASSETS_DIR / "Kumadefile.py"

            print_queue: Queue[PrintCommand] = Queue()
            print_client = PrintClient("worker", print_queue)

            request_queue: Queue[TaskCommand] = Queue()
            notify_queue: Queue[TaskCommand] = Queue()

            worker = TaskWorker(
                kumadefile, {}, print_client, request_queue, notify_queue
            )

            worker.start()
            worker.start()  # This does nothing and raises no exception.

            worker.stop()
            worker.stop()  # This does nothing and raises no exception.

    def test_main(self) -> None:
        with setup():
            kumadefile = ASSETS_DIR / "Kumadefile.py"

            print_queue: Queue[PrintCommand] = Queue()
            print_client = PrintClient("worker", print_queue)

            request_queue: Queue[TaskCommand] = Queue()
            notify_queue: Queue[TaskCommand] = Queue()

            worker = TaskWorker(
                kumadefile, {}, print_client, request_queue, notify_queue
            )

            request_queue.put(TaskCommand("greet"))
            request_queue.put(TaskCommand.exit())

            # Execute main in same process.
            worker()

            # A task completion is notified.
            notification = notify_queue.get()
            self.assertEqual(notification, TaskCommand("greet"))

            # "greet" task outputs a string by running.
            output = print_queue.get()
            self.assertEqual(output, PrintCommand("worker", "Hi, this is Kumade."))

    def test_main_with_verbose(self) -> None:
        with setup():
            kumadefile = ASSETS_DIR / "Kumadefile.py"

            print_queue: Queue[PrintCommand] = Queue()
            print_client = PrintClient("worker", print_queue)

            request_queue: Queue[TaskCommand] = Queue()
            notify_queue: Queue[TaskCommand] = Queue()

            worker = TaskWorker(
                kumadefile,
                {},
                print_client,
                request_queue,
                notify_queue,
                verbose=True,
            )

            request_queue.put(TaskCommand("greet"))
            request_queue.put(TaskCommand.exit())

            # Execute main in same process.
            worker()

            # Task outputs its name with verbose option.
            verbose_output = print_queue.get()
            self.assertEqual(verbose_output, PrintCommand("worker", "[Task] greet"))

    def test_main_with_abnormal_task_name(self) -> None:
        kumadefile = ASSETS_DIR / "Kumadefile.py"

        # Unknown path is ignored.
        with setup():
            print_queue: Queue[PrintCommand] = Queue()
            print_client = PrintClient("worker", print_queue)

            request_queue: Queue[TaskCommand] = Queue()
            notify_queue: Queue[TaskCommand] = Queue()

            worker = TaskWorker(
                kumadefile, {}, print_client, request_queue, notify_queue
            )

            request_queue.put(TaskCommand(Path("dummy")))
            request_queue.put(TaskCommand.exit())

            # Execute main in same process.
            worker()

        # Unknown task causes RuntimeError
        with setup():
            kumadefile = ASSETS_DIR / "Kumadefile.py"

            print_queue = Queue()
            print_client = PrintClient("worker", print_queue)

            request_queue = Queue()
            notify_queue = Queue()

            worker = TaskWorker(
                kumadefile, {}, print_client, request_queue, notify_queue
            )

            request_queue.put(TaskCommand("dummy"))
            request_queue.put(TaskCommand.exit())

            with self.assertRaises(RuntimeError):
                # Execute main in same process.
                worker()
