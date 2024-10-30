from multiprocessing import Queue
from unittest import TestCase

from kumade.concurrent.printer import PrintClient, PrintCommand


class TestPrintClient(TestCase):
    def test_print(self) -> None:
        queue: Queue[PrintCommand] = Queue()
        print_client = PrintClient("Client 0", queue)

        print_client.print("Test.")

        command = queue.get()
        self.assertEqual(command.client_name, "Client 0")
        self.assertEqual(command.message, "Test.")

        print_client.print("a", 1, True, sep=", ")

        command = queue.get()
        self.assertEqual(command.client_name, "Client 0")
        self.assertEqual(command.message, "a, 1, True")

        # Keyword args "end" and "flush" are ignored.
        print_client.print("Test...", end="", flush=True)

        command = queue.get()
        self.assertEqual(command.client_name, "Client 0")
        self.assertEqual(command.message, "Test...")

    def test_context_manager(self) -> None:
        queue: Queue[PrintCommand] = Queue()
        print_client = PrintClient("Client 0", queue)

        with print_client:
            # print_client.print() is used instead of the built-in print().
            print("Test.")

        command = queue.get()
        self.assertEqual(command.client_name, "Client 0")
        self.assertEqual(command.message, "Test.")
