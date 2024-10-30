from contextlib import redirect_stdout
from io import StringIO
from multiprocessing import Queue
from unittest import TestCase

from kumade.concurrent.printer import PrintCommand, PrintServer


class TestPrintServer(TestCase):
    def test_start_and_stop(self) -> None:
        queue: Queue[PrintCommand] = Queue()
        print_server = PrintServer(queue)

        print_server.start()
        print_server.start()  # This does nothing and raises no exception.

        print_server.stop()
        print_server.stop()  # This does nothing and raises no exception.

    def test_main(self) -> None:
        queue: Queue[PrintCommand] = Queue()
        print_server = PrintServer(queue)

        queue.put(PrintCommand("Client 0", "This is test message."))
        queue.put(PrintCommand.exit())

        with redirect_stdout(StringIO()) as f:
            # Execute main in same process.
            print_server()

            output = f.getvalue()

        expected = "[Client 0] This is test message.\n"
        self.assertEqual(output, expected)

    def test_create_client(self) -> None:
        queue: Queue[PrintCommand] = Queue()
        print_server = PrintServer(queue)

        client = print_server.create_client("Client 0")
        client.print("Test.")

        command = queue.get()
        self.assertEqual(command.client_name, "Client 0")
        self.assertEqual(command.message, "Test.")
