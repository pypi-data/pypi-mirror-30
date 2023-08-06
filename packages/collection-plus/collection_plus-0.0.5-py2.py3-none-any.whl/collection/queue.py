from .vector import Vector


class Queue(Vector):
    """Queues typically, but do not necessarily, order elements in a FIFO (first-in-first-out) manner
    """
    def __init__(self):
        super().__init__()

    def peek(self):
        return super().get(0)

    def poll(self):
        return super().remove(0)

    def offer(self, item):
        super().add(item)

