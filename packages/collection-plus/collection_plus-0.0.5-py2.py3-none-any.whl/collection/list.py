class List:
    """List is an array of objects
    """
    def __init__(self):
        self._arr_ = []

    def add(self, e):
        """Append an element
        """
        self._arr_.append(e)

    def clear(self):
        """Clear array
        """
        self._arr_.clear()

    def empty(self):
        return self.size() == 0

    def remove(self, index):
        """Remove element at given index
        """
        if self.empty():
            return None

        return self._arr_.pop(index)

    def size(self):
        return len(self._arr_)

    def get(self, index):
        if self.empty():
            return None

        return self._arr_[index]

    def to_array(self):
        return self._arr_
