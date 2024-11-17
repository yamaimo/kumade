from collections.abc import Generator
from contextlib import contextmanager
from multiprocessing import Queue
from pathlib import Path
from typing import Optional
from unittest import TestCase
from unittest.mock import MagicMock, patch

from kumade.concurrent.printer import PrintCommand, PrintServer
from kumade.concurrent.runner import ConcurrentTaskRunner, TaskCommand, TaskWorker
from kumade.config import Config
from kumade.decorator import depend, task
from kumade.loader import KumadefileLoader
from kumade.manager import TaskManager
from kumade.task import TaskName

ASSETS_DIR = Path(__file__).absolute().parent.parent / "assets"


@contextmanager
def setup() -> Generator[tuple[KumadefileLoader, TaskManager, Config], None, None]:
    loader = KumadefileLoader()
    manager = TaskManager()
    config = Config({})
    with patch("kumade.loader.KumadefileLoader.get_instance", return_value=loader):
        with patch("kumade.manager.TaskManager.get_instance", return_value=manager):
            with patch("kumade.config.Config.get_instance", return_value=config):
                yield (loader, manager, config)


class RecordQueue:
    def __init__(self) -> None:
        self.__queue: Queue[TaskCommand] = Queue()
        self.__completed_list: list[TaskName] = []

    def put(self, command: TaskCommand) -> None:
        self.__queue.put(command)

    def get(self, block: bool = True, timeout: Optional[float] = None) -> TaskCommand:
        command: TaskCommand = self.__queue.get()
        self.__completed_list.append(command.target)
        return command

    def index(self, target: TaskName) -> Optional[int]:
        found: Optional[int] = None
        try:
            found = self.__completed_list.index(target)
        except ValueError:
            pass

        # If the completed list has the duplicated target, return None.
        if found is not None:
            try:
                self.__completed_list.index(target, found + 1)
                found = None
            except ValueError:
                pass

        return found


def create_runner(
    loader: KumadefileLoader, config: Config, notify_queue: RecordQueue
) -> ConcurrentTaskRunner:
    kumadefile = loader.loaded_kumadefile
    assert kumadefile is not None

    config_values = config.values

    print_queue: Queue[PrintCommand] = Queue()
    print_server = PrintServer(print_queue)

    request_queue: Queue[TaskCommand] = Queue()

    workers: list[TaskWorker] = []
    for i in range(2):
        print_client = print_server.create_client(f"Worker{i}")
        worker = TaskWorker(
            kumadefile,
            config_values,
            print_client,
            request_queue,
            notify_queue,  # type: ignore
            False,
        )
        workers.append(worker)

    runner = ConcurrentTaskRunner(
        MagicMock(),  # make print_server mock not to output error message.
        workers,
        request_queue,
        notify_queue,  # type: ignore
    )
    return runner


class TestConcurrentTaskRunner(TestCase):
    def test_create(self) -> None:
        with setup() as (loader, _, config):
            loader.load(ASSETS_DIR / "concurrent.py")
            runner = ConcurrentTaskRunner.create(2)
            runner.run(["simple.a"])

    def test_run(self) -> None:
        #  [a]--->[b]--->[c]
        with setup() as (loader, _, config):
            loader.load(ASSETS_DIR / "concurrent.py")
            notify_queue = RecordQueue()

            runner = create_runner(loader, config, notify_queue)
            runner.run(["simple.a"])

            a_index = notify_queue.index("simple.a")
            b_index = notify_queue.index("simple.b")
            c_index = notify_queue.index("simple.c")

            self.assertIsNotNone(a_index)
            self.assertIsNotNone(b_index)
            self.assertIsNotNone(c_index)

            # To avoid type error by mypy
            assert a_index is not None
            assert b_index is not None
            assert c_index is not None

            self.assertGreater(a_index, b_index)
            self.assertGreater(b_index, c_index)

    def test_run_with_multi_dependencies(self) -> None:
        #  [a]--->[b]--->[d]
        #   |      |      A
        #   |      +---->[e]--->[f]
        #   |             A      A
        #   +---->[c]--->[g]     |
        #          |             |
        #          +-------------+
        with setup() as (loader, _, config):
            loader.load(ASSETS_DIR / "concurrent.py")
            notify_queue = RecordQueue()

            runner = create_runner(loader, config, notify_queue)
            runner.run(["multi_dep.a"])

            a_index = notify_queue.index("multi_dep.a")
            b_index = notify_queue.index("multi_dep.b")
            c_index = notify_queue.index("multi_dep.c")
            d_index = notify_queue.index("multi_dep.d")
            e_index = notify_queue.index("multi_dep.e")
            f_index = notify_queue.index("multi_dep.f")
            g_index = notify_queue.index("multi_dep.g")

            self.assertIsNotNone(a_index)
            self.assertIsNotNone(b_index)
            self.assertIsNotNone(c_index)
            self.assertIsNotNone(d_index)
            self.assertIsNotNone(e_index)
            self.assertIsNotNone(f_index)
            self.assertIsNotNone(g_index)

            # To avoid type error by mypy
            assert a_index is not None
            assert b_index is not None
            assert c_index is not None
            assert d_index is not None
            assert e_index is not None
            assert f_index is not None
            assert g_index is not None

            self.assertGreater(a_index, b_index)
            self.assertGreater(a_index, c_index)
            self.assertGreater(b_index, d_index)
            self.assertGreater(b_index, e_index)
            self.assertGreater(c_index, f_index)
            self.assertGreater(c_index, g_index)
            self.assertGreater(e_index, d_index)
            self.assertGreater(e_index, f_index)

    def test_run_with_multi_targets(self) -> None:
        #  [a]--->[b]--->[c]
        #          |
        #          +---->[d]--->[e]
        #                 A
        #  [f]--->[g]-----+
        #   |
        #   +---->[h]--->[i]
        with setup() as (loader, _, config):
            loader.load(ASSETS_DIR / "concurrent.py")
            notify_queue = RecordQueue()

            runner = create_runner(loader, config, notify_queue)
            runner.run(["multi_tgt.b", "multi_tgt.g", "multi_tgt.i", "multi_tgt.h"])

            a_index = notify_queue.index("multi_tgt.a")
            b_index = notify_queue.index("multi_tgt.b")
            c_index = notify_queue.index("multi_tgt.c")
            d_index = notify_queue.index("multi_tgt.d")
            e_index = notify_queue.index("multi_tgt.e")
            f_index = notify_queue.index("multi_tgt.f")
            g_index = notify_queue.index("multi_tgt.g")
            h_index = notify_queue.index("multi_tgt.h")
            i_index = notify_queue.index("multi_tgt.i")

            self.assertIsNone(a_index)
            self.assertIsNotNone(b_index)
            self.assertIsNotNone(c_index)
            self.assertIsNotNone(d_index)
            self.assertIsNotNone(e_index)
            self.assertIsNone(f_index)
            self.assertIsNotNone(g_index)
            self.assertIsNotNone(h_index)
            self.assertIsNotNone(i_index)

            # To avoid type error by mypy
            assert b_index is not None
            assert c_index is not None
            assert d_index is not None
            assert e_index is not None
            assert g_index is not None
            assert h_index is not None
            assert i_index is not None

            self.assertGreater(b_index, c_index)
            self.assertGreater(b_index, d_index)
            self.assertGreater(d_index, e_index)
            self.assertGreater(g_index, d_index)
            self.assertGreater(h_index, i_index)

    def test_run_with_task_depending_on_itself(self) -> None:
        #  [a]--->[b]---+
        #          A    |
        #          +----+
        with setup() as (loader, _, _):
            # dummy
            loader.load(ASSETS_DIR / "Kumadefile.py")

            @task("a")
            @depend("b")
            def a() -> None:
                pass

            @task("b")
            @depend("b")
            def b() -> None:
                pass

            runner = ConcurrentTaskRunner.create(2)
            with self.assertRaises(RuntimeError):
                runner.run(["a"])

    def test_run_with_unknown_task(self) -> None:
        #  [a]--->[b]--->[c]
        #                (not defined)
        with setup() as (loader, _, _):
            # dummy
            loader.load(ASSETS_DIR / "Kumadefile.py")

            @task("a")
            @depend("b")
            def a() -> None:
                pass

            @task("b")
            @depend("c")
            def b() -> None:
                pass

            runner = ConcurrentTaskRunner.create(2)
            with self.assertRaises(RuntimeError):
                runner.run(["a"])

    def test_run_with_non_task_path(self) -> None:
        # [a]--->[out.txt]--->[in.txt]
        #        (task)       (not task)
        with setup() as (loader, _, config):
            loader.load(ASSETS_DIR / "concurrent.py")
            notify_queue = RecordQueue()

            runner = create_runner(loader, config, notify_queue)
            runner.run(["path.a"])

            a_index = notify_queue.index("path.a")
            out_file_index = notify_queue.index(ASSETS_DIR / "out.txt")

            self.assertIsNotNone(a_index)
            self.assertIsNotNone(out_file_index)

    def test_run_error_task(self) -> None:
        with setup() as (loader, _, config):
            loader.load(ASSETS_DIR / "concurrent.py")
            notify_queue = RecordQueue()

            runner = create_runner(loader, config, notify_queue)
            with self.assertRaises(RuntimeError):
                runner.run(["error_task"])
