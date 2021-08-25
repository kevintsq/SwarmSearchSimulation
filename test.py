class Base:
    class Nested:
        def print(self):
            print("From Base!")

    def __init__(self):
        self.cls = self.Nested()

    def wrap(self):
        self.print()

    def print(self):
        self.cls.print()


class Derived(Base):
    class Nested:
        def print(self):
            print("From Derived!")

    def __init__(self):
        super().__init__()

    def print(self):
        self.cls.print()


d = Derived()
d.wrap()
