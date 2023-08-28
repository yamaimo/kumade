from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import MagicMock

from kumade.builder import FileTaskBuilder


class TestFileTaskBuilder(TestCase):
    def test_build_without_dependencies(self) -> None:
        with TemporaryDirectory() as temp_dir_name:
            temp_dir = Path(temp_dir_name)

            target_file = temp_dir / "test.txt"
            assert not target_file.exists()

            procedure = MagicMock(side_effect=lambda a, b: target_file.touch())

            builder = FileTaskBuilder(target_file)
            builder.set_args(["a", ["b", "c"]])
            task = builder.build(procedure)

            task.run()

            procedure.assert_called_with("a", ["b", "c"])
            self.assertTrue(target_file.exists())
            procedure.reset_mock()

            task.run()

            procedure.assert_not_called()

    def test_build_with_dependencies(self) -> None:
        with TemporaryDirectory() as temp_dir_name:
            temp_dir = Path(temp_dir_name)

            target_file = temp_dir / "test.txt"
            assert not target_file.exists()

            dep_file1 = temp_dir / "dep1.txt"
            dep_file1.touch()
            assert dep_file1.exists()
            dep_file2 = temp_dir / "dep2.txt"
            dep_file2.touch()
            assert dep_file2.exists()

            procedure = MagicMock(side_effect=lambda: target_file.touch())

            builder = FileTaskBuilder(target_file)
            builder.set_dependencies([dep_file1, dep_file2, "dummy"])
            task = builder.build(procedure)

            task.run()

            procedure.assert_called()
            self.assertTrue(target_file.exists())
            procedure.reset_mock()

            task.run()

            procedure.assert_not_called()
            procedure.reset_mock()

            dep_file1.touch()
            task.run()

            procedure.assert_called()
            self.assertGreater(target_file.stat().st_mtime, dep_file1.stat().st_mtime)
            self.assertGreater(target_file.stat().st_mtime, dep_file2.stat().st_mtime)

    def test_ignore_dir_timestamp(self) -> None:
        with TemporaryDirectory() as temp_dir_name:
            temp_dir = Path(temp_dir_name)

            target_file = temp_dir / "test.txt"
            assert not target_file.exists()

            dep_file = temp_dir / "dep.txt"
            dep_file.touch()
            assert dep_file.exists()
            dep_dir = temp_dir / "dep_dir"
            dep_dir.mkdir(parents=True)
            assert dep_dir.exists()

            procedure = MagicMock(side_effect=lambda: target_file.touch())

            builder = FileTaskBuilder(target_file)
            builder.set_dependencies([dep_file, dep_dir])
            task = builder.build(procedure)

            task.run()

            procedure.assert_called()
            self.assertTrue(target_file.exists())
            procedure.reset_mock()

            dep_dir.touch()
            task.run()

            procedure.assert_not_called()
            self.assertLess(target_file.stat().st_mtime, dep_dir.stat().st_mtime)
