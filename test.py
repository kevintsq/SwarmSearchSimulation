from abc import ABC, abstractmethod


class Foo(ABC):
    def __init__(self):
        self.print()

    @abstractmethod
    def print(self):
        pass


class Bar(Foo):
    def __init__(self):
        super().__init__()

    def print(self):
        print("Bar!")
