from functools import partial


class partialmethod(partial):
    """Like Python 3's partialmethod but backported for Python 2
    """
    def __get__(self, instance, owner):
        if instance is None:
            return self
        return partial(self.func, instance, *(self.args or ()), **(self.keywords or {}))
