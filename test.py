class Base:
    class Nested:
        def print(self):
            print("From Base!")

    def wrap(self):
        self.print()

    def print(self):
        n = self.Nested()
        n.print()


class Derived(Base):
    class Nested:
        def print(self):
            print("From Derived!")

    def print(self):
        n = self.Nested()
        n.print()


d = Derived()
d.wrap()
