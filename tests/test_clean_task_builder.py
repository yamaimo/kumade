from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from kumade.builder import CleanTaskBuilder


class TestCleanTaskBuilder(TestCase):
    def test_build(self) -> None:
        with TemporaryDirectory() as temp_dir_name:
            temp_dir = Path(temp_dir_name)

            test_file1 = temp_dir / "test.txt"
            test_file1.touch()
            assert test_file1.exists()
            test_dir = temp_dir / "test"
            test_dir.mkdir(parents=True)
            assert test_dir.exists()
            test_file2 = test_dir / "test.txt"
            test_file2.touch()
            assert test_file2.exists()

            builder = CleanTaskBuilder("clean")
            builder.set_dependencies(["clean1", "clean2"])
            builder.set_help("Clean task.")
            task = builder.build([test_file1, test_dir])

            self.assertEqual(task.name, "clean")
            self.assertEqual(task.dependencies, ["clean1", "clean2"])
            self.assertEqual(task.help, "Clean task.")

            task.run()

            self.assertFalse(test_file1.exists())
            self.assertFalse(test_dir.exists())
            self.assertFalse(test_file2.exists())
