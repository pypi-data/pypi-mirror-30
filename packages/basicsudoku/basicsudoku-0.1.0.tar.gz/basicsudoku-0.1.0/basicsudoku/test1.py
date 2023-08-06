class Foo(object):
    def __iter__(self):
        return FooIterator()

class FooIterator(object):
    def __init__(self):
        self.i = 0

    def __next__(self):
        if self.i == 10:
            raise StopIteration

        self.i += 1

        return self.i - 1

    def __iter__(self):
        return self
