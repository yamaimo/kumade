# Kumadefile loader

import importlib.util
import sys
from pathlib import Path
from typing import Optional


class KumadefileLoader:
    """
    Kumadefile loader.
    """

    __instance: Optional["KumadefileLoader"] = None

    @classmethod
    def get_instance(cls) -> "KumadefileLoader":
        """
        Return the singleton instance of kumadefile loader.

        Returns
        -------
        loader : KumadefileLoader
            The instance of kumadefile loader.
        """
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance

    def __init__(self) -> None:
        self.__loaded_kumadefile: Optional[Path] = None

    @property
    def loaded_kumadefile(self) -> Optional[Path]:
        """
        Path of loaded kumadefile.

        Returns
        -------
        path : Optional[Path]
            Path of loadef kumadefile.
            If kumadefile has not been loaded yet, return None.
        """
        return self.__loaded_kumadefile

    def load(self, kumadefile: Optional[Path]) -> None:
        """
        Load kumadefile.

        If no kumadefile is specified, loader searches for
        Kumadefile.py or kumadefile.py in the current directory
        or upper directories.

        If you try to load the loaded kumadefile again, this method does nothing.

        Parameters
        ----------
        kumadefile : Optional[Path]
            Path of kumadefile to be loaded.
            If None is specified, loader searches for kumadefile.

        Raises
        ------
        RuntimeError
            If you try to load a different kumadefile.
        """
        if kumadefile is None:
            kumadefile = self.__search_kumadefile(Path().absolute())

        # If kumadefile has already been loaded, return early.
        # However, RuntimeError is thrown due to illegal state
        # if kumadefile to be loaded is different from loaded kumadefile.
        if self.__loaded_kumadefile is not None:
            if self.__loaded_kumadefile == kumadefile:
                return
            else:
                raise RuntimeError("Trying to load a different kumadefile.")

        # Enable to import python modules easily from Kumadefile.py
        base_dir = kumadefile.parent
        sys.path.append(str(base_dir))

        self.__load_kumadefile(kumadefile)
        self.__loaded_kumadefile = kumadefile

    def __search_kumadefile(self, current_dir: Path) -> Path:
        for filename in ["Kumadefile.py", "kumadefile.py"]:
            path = current_dir / filename
            if path.exists():
                return path

        parent_dir = current_dir.parent
        if current_dir == parent_dir:
            raise RuntimeError("Kumadefile.py is not found.")
        else:
            return self.__search_kumadefile(parent_dir)

    def __load_kumadefile(self, kumadefile: Path) -> None:
        # NOTE: https://docs.python.org/3/library/importlib.html#importing-a-source-file-directly
        module_name = "kumadefile"
        spec = importlib.util.spec_from_file_location(module_name, kumadefile)
        assert spec is not None
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        assert spec.loader is not None and spec.loader.exec_module is not None
        spec.loader.exec_module(module)
