from contextlib import contextmanager, redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Generator
from unittest import TestCase
from unittest.mock import MagicMock, patch

from kumade.decorator import depend, file, task
from kumade.manager import TaskManager
from kumade.runner import TaskRunner


# to reduce indent
@contextmanager
def setup() -> Generator:
    manager = TaskManager()
    with patch("kumade.manager.TaskManager.get_instance", return_value=manager):
        with StringIO() as stdout:
            with redirect_stdout(stdout):
                yield (manager, stdout)


class TestTaskRunner(TestCase):
    def test_run(self) -> None:
        #  [a]--->[b]--->[c]
        with setup():
            value = [0]  # to make value mutable with keeping reference
            called = {}

            checker_a = MagicMock()
            checker_b = MagicMock()
            checker_c = MagicMock()

            @task("a")
            @depend("b")
            def a() -> None:
                checker_a()
                called["a"] = value[0]
                value[0] += 1

            @task("b")
            @depend("c")
            def b() -> None:
                checker_b()
                called["b"] = value[0]
                value[0] += 1

            @task("c")
            def c() -> None:
                checker_c()
                called["c"] = value[0]
                value[0] += 1

            runner = TaskRunner()
            runner.run(["a"])

            checker_a.assert_called_once()
            checker_b.assert_called_once()
            checker_c.assert_called_once()

            self.assertGreater(called["a"], called["b"])
            self.assertGreater(called["b"], called["c"])

    def test_run_with_multi_dependencies(self) -> None:
        #  [a]--->[b]--->[d]
        #   |      |      A
        #   |      +---->[e]--->[f]
        #   |             A      A
        #   +---->[c]--->[g]     |
        #          |             |
        #          +-------------+
        with setup():
            value = [0]  # to make value mutable with keeping reference
            called = {}

            checker_a = MagicMock()
            checker_b = MagicMock()
            checker_c = MagicMock()
            checker_d = MagicMock()
            checker_e = MagicMock()
            checker_f = MagicMock()
            checker_g = MagicMock()

            @task("a")
            @depend("b", "c")
            def a() -> None:
                checker_a()
                called["a"] = value[0]
                value[0] += 1

            @task("b")
            @depend("d", "e")
            def b() -> None:
                checker_b()
                called["b"] = value[0]
                value[0] += 1

            @task("c")
            @depend("f", "g")
            def c() -> None:
                checker_c()
                called["c"] = value[0]
                value[0] += 1

            @task("d")
            def d() -> None:
                checker_d()
                called["d"] = value[0]
                value[0] += 1

            @task("e")
            @depend("d", "f")
            def e() -> None:
                checker_e()
                called["e"] = value[0]
                value[0] += 1

            @task("f")
            def f() -> None:
                checker_f()
                called["f"] = value[0]
                value[0] += 1

            @task("g")
            @depend("e")
            def g() -> None:
                checker_g()
                called["g"] = value[0]
                value[0] += 1

            runner = TaskRunner()
            runner.run(["a"])

            checker_a.assert_called_once()
            checker_b.assert_called_once()
            checker_c.assert_called_once()
            checker_d.assert_called_once()
            checker_e.assert_called_once()
            checker_f.assert_called_once()
            checker_g.assert_called_once()

            self.assertGreater(called["a"], called["b"])
            self.assertGreater(called["a"], called["c"])
            self.assertGreater(called["b"], called["d"])
            self.assertGreater(called["b"], called["e"])
            self.assertGreater(called["c"], called["f"])
            self.assertGreater(called["c"], called["g"])
            self.assertGreater(called["e"], called["d"])
            self.assertGreater(called["e"], called["f"])

    def test_run_with_multi_targets(self) -> None:
        #  [a]--->[b]--->[c]
        #          |
        #          +---->[d]--->[e]
        #                 A
        #  [f]--->[g]-----+
        #   |
        #   +---->[h]--->[i]
        with setup():
            value = [0]  # to make value mutable with keeping reference
            called = {}

            checker_a = MagicMock()
            checker_b = MagicMock()
            checker_c = MagicMock()
            checker_d = MagicMock()
            checker_e = MagicMock()
            checker_f = MagicMock()
            checker_g = MagicMock()
            checker_h = MagicMock()
            checker_i = MagicMock()

            @task("a")
            @depend("b")
            def a() -> None:
                checker_a()
                called["a"] = value[0]
                value[0] += 1

            @task("b")
            @depend("c", "d")
            def b() -> None:
                checker_b()
                called["b"] = value[0]
                value[0] += 1

            @task("c")
            def c() -> None:
                checker_c()
                called["c"] = value[0]
                value[0] += 1

            @task("d")
            @depend("e")
            def d() -> None:
                checker_d()
                called["d"] = value[0]
                value[0] += 1

            @task("e")
            def e() -> None:
                checker_e()
                called["e"] = value[0]
                value[0] += 1

            @task("f")
            @depend("g", "h")
            def f() -> None:
                checker_f()
                called["f"] = value[0]
                value[0] += 1

            @task("g")
            @depend("d")
            def g() -> None:
                checker_g()
                called["g"] = value[0]
                value[0] += 1

            @task("h")
            @depend("i")
            def h() -> None:
                checker_h()
                called["h"] = value[0]
                value[0] += 1

            @task("i")
            def i() -> None:
                checker_i()
                called["i"] = value[0]
                value[0] += 1

            runner = TaskRunner()
            runner.run(["b", "g", "i", "h"])

            checker_a.assert_not_called()
            checker_b.assert_called_once()
            checker_c.assert_called_once()
            checker_d.assert_called_once()
            checker_e.assert_called_once()
            checker_f.assert_not_called()
            checker_g.assert_called_once()
            checker_h.assert_called_once()
            checker_i.assert_called_once()

            self.assertGreater(called["b"], called["c"])
            self.assertGreater(called["b"], called["d"])
            self.assertGreater(called["d"], called["e"])
            self.assertGreater(called["g"], called["d"])
            self.assertGreater(called["h"], called["i"])

    def test_run_with_task_depending_on_itself(self) -> None:
        #  [a]--->[b]---+
        #          A    |
        #          +----+
        with setup():

            @task("a")
            @depend("b")
            def a() -> None:
                pass

            @task("b")
            @depend("b")
            def b() -> None:
                pass

            runner = TaskRunner()
            with self.assertRaises(RuntimeError):
                runner.run(["a"])

    def test_run_with_circular_dependency(self) -> None:
        #  [a]--->[b]--->[c]
        #   |      A      |
        #   +---->[d]<----+
        with setup():

            @task("a")
            @depend("b", "d")
            def a() -> None:
                pass

            @task("b")
            @depend("c")
            def b() -> None:
                pass

            @task("c")
            @depend("d")
            def c() -> None:
                pass

            @task("d")
            @depend("b")
            def d() -> None:
                pass

            runner = TaskRunner()
            with self.assertRaises(RuntimeError):
                runner.run(["a"])

    def test_run_with_unknown_task(self) -> None:
        #  [a]--->[b]--->[c]
        #                (not defined)
        with setup():

            @task("a")
            @depend("b")
            def a() -> None:
                pass

            @task("b")
            @depend("c")
            def b() -> None:
                pass

            runner = TaskRunner()
            with self.assertRaises(RuntimeError):
                runner.run(["a"])

    def test_run_with_non_task_path(self) -> None:
        # [a]--->[out.txt]--->[in.txt]
        #        (task)       (not task)
        with setup():
            with TemporaryDirectory() as temp_dir_name:
                temp_dir = Path(temp_dir_name)

                in_file = temp_dir / "in.txt"
                in_file.touch()

                out_file = temp_dir / "out.txt"

                checker_a = MagicMock()
                checker_out_file = MagicMock()

                @task("a")
                @depend(out_file)
                def a() -> None:
                    checker_a()

                @file(out_file)
                @depend(in_file)
                def create_out_file() -> None:
                    checker_out_file()

                runner = TaskRunner()
                runner.run(["a"])

                checker_a.assert_called_once()
                checker_out_file.assert_called_once()

    def test_run_verbose(self) -> None:
        #  [a]--->[b]--->[c]
        with setup() as (manager, stdout):

            @task("a")
            @depend("b")
            def a() -> None:
                pass

            @task("b")
            @depend("c")
            def b() -> None:
                pass

            @task("c")
            def c() -> None:
                pass

            runner = TaskRunner(verbose=True)
            runner.run(["a"])

            expected_output = "[Task] c\n[Task] b\n[Task] a\n"
            self.assertEqual(stdout.getvalue(), expected_output)
