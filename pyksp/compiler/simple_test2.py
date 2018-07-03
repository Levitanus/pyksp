
class KspCondBrake(Exception):
    pass


__condition = True


def Break():
    raise KspCondBrake()


def check(condition=None):
    global __condition

    if condition is None:
        if __condition is False:
            __condition = True
            Break()
        return True
    __condition = condition


class For:

    def __init__(self, array):
        self.seq = array

    def __enter__(self):
        return self.for_handler

    def __exit__(self, exc, value, trace):
        return True

    def for_handler(self):
        for i in self.seq:
            yield i


array = [1, 3, 4, 7]
with For(array) as f:
    for i in f():
        print(i)
