import os
import shutil
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from kumade.loader import KumadefileLoader
from kumade.manager import TaskManager

ASSETS_DIR = Path(__file__).absolute().parent / "assets"


# NOTE: contextlib.chdir() is available from ver. 3.11
@contextmanager
def chdir(path: Path) -> Generator[None, None, None]:
    org_dir = Path.cwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(org_dir)


class TestKumadefileLoader(TestCase):
    def test_get_instance(self) -> None:
        loader = KumadefileLoader.get_instance()
        another = KumadefileLoader.get_instance()
        self.assertEqual(loader, another)

    def test_load(self) -> None:
        manager = TaskManager()
        with patch("kumade.manager.TaskManager.get_instance", return_value=manager):
            with TemporaryDirectory() as temp_dir_name:
                temp_dir = Path(temp_dir_name)
                shutil.copy(ASSETS_DIR / "Kumadefile.py", temp_dir)

                with chdir(temp_dir):
                    loader = KumadefileLoader()
                    self.assertIsNone(loader.loaded_kumadefile)

                    loader.load(None)

                    expected_kumadefile = Path().absolute() / "Kumadefile.py"
                    self.assertEqual(loader.loaded_kumadefile, expected_kumadefile)
                    self.assertIsNotNone(manager.find("greet"))

    def test_load_from_sub_dir(self) -> None:
        manager = TaskManager()
        with patch("kumade.manager.TaskManager.get_instance", return_value=manager):
            with TemporaryDirectory() as temp_dir_name:
                temp_dir = Path(temp_dir_name)
                shutil.copy(ASSETS_DIR / "Kumadefile.py", temp_dir)

                sub_dir = temp_dir / "sub"
                sub_dir.mkdir(parents=True, exist_ok=True)

                with chdir(sub_dir):
                    loader = KumadefileLoader()
                    self.assertIsNone(loader.loaded_kumadefile)

                    loader.load(None)

                    expected_kumadefile = Path().absolute().parent / "Kumadefile.py"
                    self.assertEqual(loader.loaded_kumadefile, expected_kumadefile)
                    self.assertIsNotNone(manager.find("greet"))

    def test_load_again(self) -> None:
        manager = TaskManager()
        with patch("kumade.manager.TaskManager.get_instance", return_value=manager):
            with TemporaryDirectory() as temp_dir_name:
                temp_dir = Path(temp_dir_name)
                shutil.copy(ASSETS_DIR / "Kumadefile.py", temp_dir)

                with chdir(temp_dir):
                    loader = KumadefileLoader()
                    self.assertIsNone(loader.loaded_kumadefile)

                    loader.load(None)

                    expected_kumadefile = Path().absolute() / "Kumadefile.py"
                    self.assertEqual(loader.loaded_kumadefile, expected_kumadefile)
                    self.assertIsNotNone(manager.find("greet"))

                    # Load again and check not to raise exception.
                    loader.load(None)
                    self.assertEqual(loader.loaded_kumadefile, expected_kumadefile)

                    # Load again with specifiying loaded kumadefile
                    # and check not to raise exception.
                    loader.load(loader.loaded_kumadefile)
                    self.assertEqual(loader.loaded_kumadefile, expected_kumadefile)

    def test_load_again_with_another_kumadefile(self) -> None:
        manager = TaskManager()
        with patch("kumade.manager.TaskManager.get_instance", return_value=manager):
            with TemporaryDirectory() as temp_dir_name:
                temp_dir = Path(temp_dir_name)
                shutil.copy(ASSETS_DIR / "Kumadefile.py", temp_dir)
                shutil.copy(ASSETS_DIR / "Kumadefile.py", temp_dir / "Another.py")

                with chdir(temp_dir):
                    loader = KumadefileLoader()
                    self.assertIsNone(loader.loaded_kumadefile)

                    loader.load(None)

                    expected_kumadefile = Path().absolute() / "Kumadefile.py"
                    self.assertEqual(loader.loaded_kumadefile, expected_kumadefile)
                    self.assertIsNotNone(manager.find("greet"))

                    # Load again with another kumadefile
                    another_file_path = Path().absolute() / "Another.py"
                    with self.assertRaises(RuntimeError):
                        loader.load(another_file_path)

    def test_load_without_kumadefile(self) -> None:
        manager = TaskManager()
        with patch("kumade.manager.TaskManager.get_instance", return_value=manager):
            with TemporaryDirectory() as temp_dir_name:
                temp_dir = Path(temp_dir_name)
                with chdir(temp_dir):
                    loader = KumadefileLoader()
                    self.assertIsNone(loader.loaded_kumadefile)

                    with self.assertRaises(RuntimeError):
                        loader.load(None)
