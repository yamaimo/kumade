# An example python module which will be imported from Kumadefile.py


class SomeUsefulTask:
    def __init__(self, name: str) -> None:
        self.__name = name

    def execute(self) -> None:
        print(f"Execute some useful task named '{self.__name}'.")
