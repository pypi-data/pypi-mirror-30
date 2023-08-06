from .vector import Vector


class Stack(Vector):
    """The Stack class represents a last-in-first-out (LIFO) stack of objects
    """
    def __init__(self):
        super().__init__()

    def peek(self):
        return super().get(super().size() - 1)

    def pop(self):
        return super().remove(super().size() - 1)

    def push(self, item):
        super().add(item)

