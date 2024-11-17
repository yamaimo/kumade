# Print server and client for multi process

import builtins
from dataclasses import dataclass
from multiprocessing import Process, Queue
from typing import Any, Optional


@dataclass(frozen=True)
class PrintCommand:
    """
    Print command.

    Attributes
    ----------
    client_name : str
        Client name.
        Empty string means an exit command.
    message : str
        Message to be printed.
    """

    client_name: str
    message: str

    @classmethod
    def exit(cls) -> "PrintCommand":
        """Return an exit command."""
        return cls("", "")

    @property
    def is_exit(self) -> bool:
        """An exit command or not."""
        return self.client_name == ""


class PrintClient:
    """
    Print client.

    This class works as a context manager
    and replaces the built-in print() function
    with this print() method by using with-statement.
    """

    def __init__(self, name: str, queue: Queue) -> None:
        """
        Parameters
        ----------
        name : str
            Name of client (empty string is not allowed).
        queue : Queue
            Queue for print commands.
        """
        assert len(name) > 0
        self.__name = name
        self.__queue = queue
        self.__org_print = None

    def print(self, *objects: Any, sep: str = " ", **kwargs: Any) -> None:
        """
        Send a print command.

        Parameters
        ----------
        *objects : list
            Objects to be printed.
        sep : str, default " "
            Separator for concatenating objects.
        **kwargs : dict
            Other keyword arguments are ignored.
        """
        message = sep.join(map(str, objects))
        command = PrintCommand(self.__name, message)
        self.__queue.put(command)

    def __enter__(self) -> None:
        self.__org_print = builtins.print  # type: ignore
        builtins.print = self.print  # type: ignore

    def __exit__(self, exc_type, exc_value, traceback) -> None:  # type: ignore
        builtins.print = self.__org_print  # type: ignore


class PrintServer:
    """
    Print server.
    """

    def __init__(self, queue: Queue) -> None:
        """
        Parameters
        ----------
        queue : Queue
            Queue for print commands.
        """
        self.__queue = queue
        self.__process: Optional[Process] = None

    def start(self) -> None:
        """Start print server process."""
        if self.__process is not None:
            return

        self.__process = Process(target=self)
        self.__process.start()

    def stop(self) -> None:
        """Stop print server process."""
        if self.__process is None:
            return

        self.__queue.put(PrintCommand.exit())
        self.__process.join()
        self.__process = None

    def __call__(self) -> None:
        """Main for print server process."""
        while True:
            command = self.__queue.get()
            if command.is_exit:
                return
            print(f"[{command.client_name}] {command.message}")

    def create_client(self, client_name: str) -> PrintClient:
        """
        Create print client.

        Parameters
        ----------
        client_name : str
            Name of client (empty string is not allowed).

        Returns
        -------
        client : PrintClient
            Created client.
        """
        return PrintClient(client_name, self.__queue)
